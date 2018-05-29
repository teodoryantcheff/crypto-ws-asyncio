import asyncio
import time
from datetime import datetime

import dateutil.parser as dp

from arbi import TickerObserver

try:
    import ujson as json
except:
    import json

import websockets

from counters import c  # fixme: this is ugly


class CryptoExchange(object):
    url: str = 'Exchange WS url goes in here'

    all_markets = []

    need_common_names = False

    common_currencies = {
        # Forward mapping
        'XBT': 'BTC',
        'M18': 'BTC',
        'BCC': 'BCH',
        'DRK': 'DASH',
        # Reverse mapping
        'BTC': 'XBT',
        'BCH': 'BCC',
        'DASH': 'DRK',
    }

    def __init__(self, markets: list, ticker_observer: TickerObserver = None):
        """
        :param markets: list of crypto pairs, this will stream data for. 'base_quote' format
        """
        # TODO list pairs in norm format?
        # List of market names in crypto-exchange naming format
        self.markets_native: list = list()

        # save all markets in normalized format
        self.markets_norm = markets.copy()

        # Maps from both pairs in norm format ('xxx_yyy') to exchange format ('XXXYYY') and back ('XXXYYY' => 'xxx_yyy')
        self._market_names_map = dict()

        # normalized_market_name as a key here
        self.ticker = {}

        # list all the markets in exchange native format
        for market in markets:
            d_market_name = self.denormalize_market_name(market)
            self.markets_native.append(d_market_name)
            self._market_names_map.update({
                market: d_market_name,  # forward mapping
                d_market_name: market})  # and reverse mapping
            self.ticker[market] = dict()

        # Orderbook, normalized_pair_name used as a key as well
        self.order_books = {}

        self._ws: websockets.WebSocketClientProtocol = None

        self.observer = ticker_observer
        if self.observer:
            self.observer.register(self)

    async def subscribe_ticker(self):
        raise NotImplemented('Can only be called on a subclass')

    # def update_orderbook(self, symbol, bids, asks):

    def update_ticker(self, market, best_bid, best_ask, bid_size=0, ask_size=0, last_price=None, volume=None,
                      timestamp=None):
        # todo add more data from ccxt's dict, like so
        # return {
        #     'symbol': symbol,
        #     'timestamp': timestamp,
        #     'datetime': self.iso8601(timestamp),
        #     'high': None,
        #     'low': None,
        #     'bid': bid,
        #     'bidVolume': None,
        #     'ask': ask,
        #     'askVolume': None,
        #     'vwap': None,
        #     'open': None,
        #     'close': last,
        #     'last': last,
        #     'previousClose': None,
        #     'change': None,
        #     'percentage': None,
        #     'average': None,
        #     'baseVolume': self.safe_float(ticker, 'volume'),
        #     'quoteVolume': None,
        #     'info': ticker,
        # }
        # updates the ticker cache dict
        ts = int(time.time() * 1000)
        self.ticker[market] = {
            # 'local_timestamp': int(datetime.utcnow().timestamp() * 1000),
            'local_timestamp': ts,
            'best_bid': best_bid,
            'best_ask': best_ask,
            'bid_size': bid_size,
            'ask_size': ask_size,
            'last_price': last_price,
            'volume': volume,
            'timestamp': timestamp,
        }

        # print(f'\n\n\n\n\n\n=== {ts} ========================================================================')

        # print('{:10s} {}: {}'.format(
        #     self.__class__.__name__, market,
        #     'b {bid_size:>{widht}.{prec}f} @ {best_bid:<{widht}.{prec}f} '
        #     'a {ask_size:>{widht}.{prec}f} @ {best_ask:<{widht}.{prec}f} {ts}'.format(widht=15, prec=4, ts=ts,
        #                                                                               bid_size=bid_size,
        #                                                                               ask_size=ask_size,
        #                                                                               best_bid=best_bid,
        #                                                                               best_ask=best_ask)))

        # call whoever is interested in those updates
        if self.observer:
            self.observer.notify()

    def on_ticker(self, market: str, data):
        # Called on ticker messages
        raise NotImplemented('Can only be called on a subclass')

    def on_heartbeat(self, market: str, data):
        """

        :param market: in normalized ('btc_usd') format
        :param data: all the json in the message, since heartbeat messages are quite different
        :return:
        """
        # Called on heasrtbeat messages
        raise NotImplemented('Can only be called on a subclass')

    def on_message(self, json_payload):
        # Called on successfully json.loads()ed message
        raise NotImplemented('Can only be called on a subclass')

    def on_recv(self, data):
        c.tick(self.__class__.__name__)

        # Called on any messages from the websocket
        # assuming most of the exchanges will use json, we parse it at the base
        # class level and pass to on_message for dispatch
        try:
            msg = json.loads(data)
            # print(self.__class__.__name__ , '<', msg)
        except ValueError as e:
            # not a json decodable object
            print(f"Error JSON decoding payload '{data}'")
            raise
            # logger.error(f"Error JSON decoding payload '{data}'")

        self.on_message(msg)

    async def connect(self, custom_url=None):
        url = custom_url or self.url
        self._ws = await websockets.connect(url)
        print(self.__class__.__name__, 'connected')

    async def close(self):
        await self._ws.close()
        print(self.__class__.__name__, 'closed')

    async def recv_all(self):
        try:
            while True:
                data = await self._ws.recv()
                self.on_recv(data)
        except websockets.ConnectionClosed as exc:
            print(f' !!! Connection to {self.__class__.__name__} closed: code:{exc.code} reason:"{exc.reason}"')
            asyncio.ensure_future(self.run())

    async def run(self):
        await self.connect()
        await self.subscribe_ticker()
        await self.recv_all()
        await self.close()

    # #  By default it is assumed the exchange uses XXXYYY symbol notation
    # def normalize_pair_name(self, pair_name: str):
    #     # XXXYYY -> xxx_yyy
    #     # Exchange specific to normalized
    #     return '{}_{}'.format(pair_name[:3], pair_name[3:]).lower()

    @staticmethod
    def iso8601_to_ts(dt: datetime):
        return int(dp.parse(dt).timestamp() * 1000)

    @classmethod
    def denormalize_market_name(cls, market_name: str):
        # xxx_yyy -> XXXYYY
        # Normalized to Exchange specific
        return ''.join(market_name.split('_')).upper()

    def print_orderbook(self):
        market = list(self._market_names_map.keys())[0]  # todo, only takes the first pair

        bids = self.order_books[market].get('bids', [])
        asks = self.order_books[market].get('asks', [])
        print('b', len(bids), bids[-1],
              'a', len(asks), asks[0],
              '||| b ', self.ticker[market]['best_bid'],
              '||| a ', self.ticker[market]['best_ask'],
              )
        for a in reversed(asks[:10]):
            print('{:6.2f}  {:6.2f}'.format(*a))
        print('======================= ')
        for b in list(reversed(bids))[:10]:
            print('{:6.2f}  {:6.2f}'.format(*b))
