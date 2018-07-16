import json

from base import CryptoExchange


class BitMEX(CryptoExchange):
    url = "wss://www.bitmex.com/realtime"

    all_markets = ['ada_btc', 'bch_btc', 'xrp_btc', 'btc_usd', 'eth_btc', 'ltc_btc']

    need_common_names = True
    # Thesse are all the BitMex supports, hence a static map
    # Also FIXME, this is messy
    names_map = {
        # bitmex to normal humans
        "ADAM18": 'ada_btc',
        "BCHM18": 'bch_btc',
        "XRPM18": 'xrp_btc',
        "XBTUSD": 'btc_usd',
        "ETHM18": 'eth_btc',
        "LTCM18": 'ltc_btc',
        # normal to bitmex
        "ada_btc": "ADAM18",
        'bch_btc': "BCHM18",
        'xrp_btc': "XRPM18",
        'btc_usd': "XBTUSD",
        'eth_btc': "ETHM18",
        'ltc_btc': "LTCM18",
    }

    # # {"op": "subscribe", "args":["instrument:ADAM18","instrument:XBTUSD"]}
    # def __init__(self, markets):
    #     super().__init__(markets)

    async def subscribe_ticker(self):
        # {"op": "subscribe", "args":["instrument:ADAM18","instrument:XBTUSD"]}
        # https://www.bitmex.com/app/wsAPI#Subscriptions
        request = {
            'op': 'subscribe',
            'args': ['quote:{}'.format(m) for m in self.markets_native]
        }
        await self._ws.send(json.dumps(request))

    async def on_message(self, json_payload):
        try:
            updates = json_payload['data']
            for ticker_msg in updates:
                market = self._market_names_map[ticker_msg['symbol']]
                await self.on_ticker(market, ticker_msg)
        except:
            pass

    async def on_ticker(self, market, data):
        timestamp = CryptoExchange.iso8601_to_ts(data['timestamp'])
        await self.update_ticker(
            market,
            best_bid=float(data['bidPrice']),
            bid_size=float(data['bidSize']),
            best_ask=float(data['askPrice']),
            ask_size=float(data['askSize']),
            timestamp=timestamp
        )

    @classmethod
    def denormalize_market_name(cls, market_name: str):
        # xxx_yyy -> XXXYYY
        # Normalized to Exchange specific
        return BitMEX.names_map[market_name]
