import json
from operator import itemgetter

from base import CryptoExchange
from sortedcollection import SortedCollection


class GDAX(CryptoExchange):
    url = "wss://ws-feed.gdax.com"

    all_markets = ['bch_btc', 'bch_usd', 'btc_eur', 'btc_gbp', 'btc_usd', 'eth_btc', 'eth_eur', 'eth_usd', 'ltc_btc',
                   'ltc_eur', 'ltc_usd', 'bch_eur']

    need_common_names = False

    async def subscribe_ticker(self):
        request = {
            'type': 'subscribe',
            'product_ids': [m for m in self.markets_native],
            'channels': ['ticker', 'heartbeat']
            # 'channels': ['ticker', 'level2', 'heartbeat']
        }
        await self._ws.send(json.dumps(request))

    def on_message(self, json_payload):
        msg_type = json_payload['type']
        try:
            market = self._market_names_map[json_payload['product_id']]

            if msg_type == 'l2update':
                self.on_orderbook_l2update(market, json_payload['changes'])
            elif msg_type == 'snapshot':
                self.on_orderbook_snapshot(market, json_payload)
            elif msg_type == 'heartbeat':
                self.on_heartbeat(market, json_payload)
            elif msg_type == 'ticker':
                self.on_ticker(market, json_payload)
        except Exception as e:
            pass

    def on_heartbeat(self, market, data):
        # self.print_orderbook()
        pass

    def on_orderbook_snapshot(self, symbol, data):
        self.order_books[symbol] = dict()

        self.order_books[symbol]['bids'] = SortedCollection(
            [[float(pq) for pq in bid]
             for bid in data['bids']], key=itemgetter(0)
        )

        self.order_books[symbol]['asks'] = SortedCollection(
            [[float(pq) for pq in ask]
             for ask in data['asks']], key=itemgetter(0)
        )

    def on_orderbook_l2update(self, symbol, data):
        for change in data:
            side, p, q = change
            p, q = float(p), float(q)

            book = self.order_books[symbol]['asks'] if side == 'sell' else self.order_books[symbol]['bids']

            try:
                el = book.find(p)
                if q == 0:  # delete from orderbook
                    book.remove(el)  # delete order at price level p
            except ValueError:
                book.insert([p, q])

    def on_ticker(self, market, data):
        self.update_ticker(
            market,
            best_bid=float(data['best_bid']),
            best_ask=float(data['best_ask']),
            last_price=float(data['price']),
            volume=float(data['volume_24h']),
        )

    @classmethod
    def denormalize_market_name(cls, market_name):
        # xxx_yyy -> XXX-YYY
        return '-'.join(market_name.split('_')).upper()
