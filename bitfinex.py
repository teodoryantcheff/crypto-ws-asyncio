import asyncio
import json
from operator import itemgetter

from arbi import TickerObserver
from base import CryptoExchange
from sortedcollection import SortedCollection


class BitFinex(CryptoExchange):
    url = 'wss://api.bitfinex.com/ws/2'

    all_markets = ['btc_usd', 'ltc_usd', 'ltc_btc', 'eth_usd', 'eth_btc', 'etc_btc', 'etc_usd', 'rrt_usd',
                   'rrt_btc', 'zec_usd', 'zec_btc', 'xmr_usd', 'xmr_btc', 'dash_usd', 'dash_btc', 'btc_eur',
                   'btc_jpy', 'xrp_usd', 'xrp_btc', 'iota_usd', 'iota_btc', 'iota_eth', 'eos_usd', 'eos_btc',
                   'eos_eth', 'san_usd', 'san_btc', 'san_eth', 'omg_usd', 'omg_btc', 'omg_eth', 'bch_usd',
                   'bch_btc', 'bch_eth', 'neo_usd', 'neo_btc', 'neo_eth', 'etp_usd', 'etp_btc', 'etp_eth',
                   'qtum_usd', 'qtum_btc', 'qtum_eth', 'avt_usd', 'avt_btc', 'avt_eth', 'edo_usd', 'edo_btc',
                   'edo_eth', 'btg_usd', 'btg_btc', 'data_usd', 'data_btc', 'data_eth', 'qash_usd', 'qash_btc',
                   'qash_eth', 'yoyow_usd', 'yoyow_btc', 'yoyow_eth', 'gnt_usd', 'gnt_btc', 'gnt_eth', 'snt_usd',
                   'snt_btc', 'snt_eth', 'iota_eur', 'bat_usd', 'bat_btc', 'bat_eth', 'mana_usd', 'mana_btc',
                   'mana_eth', 'fun_usd', 'fun_btc', 'fun_eth', 'zrx_usd', 'zrx_btc', 'zrx_eth', 'tnb_usd',
                   'tnb_btc', 'tnb_eth', 'spank_usd', 'spank_btc', 'spank_eth', 'trx_usd', 'trx_btc', 'trx_eth',
                   'rcn_usd', 'rcn_btc', 'rcn_eth', 'rlc_usd', 'rlc_btc', 'rlc_eth', 'aid_usd', 'aid_btc',
                   'aid_eth', 'sngls_usd', 'sngls_btc', 'sngls_eth', 'rep_usd', 'rep_btc', 'rep_eth', 'elf_usd',
                   'elf_btc', 'elf_eth', 'btc_gbp', 'eth_eur', 'eth_jpy', 'eth_gbp', 'neo_eur', 'neo_jpy', 'neo_gbp',
                   'eos_eur', 'eos_jpy', 'eos_gbp', 'iota_jpy', 'iota_gbp', 'iost_usd', 'iost_btc', 'iost_eth',
                   'aio_usd', 'aio_btc', 'aio_eth', 'req_usd', 'req_btc', 'req_eth', 'rdn_usd', 'rdn_btc',
                   'rdn_eth', 'lrc_usd', 'lrc_btc', 'lrc_eth', 'wax_usd', 'wax_btc', 'wax_eth', 'dai_usd',
                   'dai_btc', 'dai_eth', 'cfi_usd', 'cfi_btc', 'cfi_eth', 'agi_usd', 'agi_btc', 'agi_eth',
                   'bft_usd', 'bft_btc', 'bft_eth', 'mtn_usd', 'mtn_btc', 'mtn_eth', 'ode_usd', 'ode_btc',
                   'ode_eth', 'ant_usd', 'ant_btc', 'ant_eth', 'dth_usd', 'dth_btc', 'dth_eth', 'mit_usd',
                   'mit_btc', 'mit_eth', 'storj_usd', 'storj_btc', 'storj_eth', 'xlm_usd', 'xlm_eur', 'xlm_jpy',
                   'xlm_gbp', 'xlm_btc', 'xlm_eth', 'xvg_usd', 'xvg_eur', 'xvg_jpy', 'xvg_gbp', 'xvg_btc', 'xvg_eth',
                   'bci_usd', 'bci_btc', 'mkr_usd', 'mkr_btc', 'mkr_eth', 'ven_usd', 'ven_btc', 'ven_eth',
                   'knc_usd', 'knc_btc', 'knc_eth', 'poa_usd', 'poa_btc', 'poa_eth']

    def __init__(self, markets: list, ticker_observer: TickerObserver):
        super().__init__(markets, ticker_observer)
        self.mapping = {}  # maps pairs to bitfinex channel ids

        for m in markets:
            self.order_books[m] = {
                'bids': SortedCollection(key=itemgetter(0)),
                'asks': SortedCollection(key=itemgetter(0))
            }

    async def subscribe_ticker(self):
        # https://docs.bitfinex.com/v2/reference#ws-public-order-books
        book_reqs = []
        # [{
        #     "event": "subscribe",
        #     "channel": "book",
        #     "prec": "P0",
        #     "len": 25,  # 100 is the max
        #     "symbol": pair
        # } for pair in self.pairs]

        ticker_reqs = [{
            "event": "subscribe",
            "channel": "ticker",
            "symbol": market
        } for market in self.markets_native]

        subscribe_futures = [self._ws.send(json.dumps(req)) for req in book_reqs + ticker_reqs]
        await asyncio.gather(*subscribe_futures)

    def _update_books(self, symbol, order):
        bidbook: SortedCollection = self.order_books[symbol]['bids']
        askbook: SortedCollection = self.order_books[symbol]['asks']

        price, count, amount = [float(pca) for pca in order]

        book = bidbook
        if amount < 0:
            book = askbook
            amount = -amount

        try:
            el = book.find(price)
            if count == 0:
                book.remove(el)
        except ValueError:
            book.insert([price, amount])

    def on_orderbook_snapshot(self, market: str, snapshot: list):
        for order in snapshot:
            self._update_books(market, order)

    def on_orderbook_l2update(self, market: str, book_update: list):
        self._update_books(market, book_update)

    async def on_message(self, json_payload):
        try:
            # print('< ', json_payload)
            chan_id, data = int(json_payload[0]), json_payload[1]
            market = self._market_names_map[self.mapping[chan_id]]

            # it's a list, since the index lookup has not failed
            if data == 'hb':
                self.on_heartbeat(market, json_payload)
            else:
                if len(data) == 3:
                    self.on_orderbook_l2update(market, data)
                elif len(data) == 10:
                    await self.on_ticker(market, data)
                else:
                    self.on_orderbook_snapshot(market, data)
        except KeyError:  # json_payload is really a dict, not a list
            if json_payload.get('event', '').lower() == "subscribed":
                chan_id = int(json_payload['chanId'])
                market = json_payload['pair']
                self.mapping[chan_id] = market

        # todo ? info messages

    async def on_ticker(self, market, data):
        await self.update_ticker(
            market=market,
            best_bid=float(data[0]),
            bid_size=float(data[1]),
            best_ask=float(data[2]),
            ask_size=float(data[3]),
            last_price=float(data[5]),
            volume=float(data[7]),
        )

    def on_heartbeat(self, market, json_payload):
        pass
