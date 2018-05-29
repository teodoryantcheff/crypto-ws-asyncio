#!/usr/bin/env python

import asyncio
import random

from arbi import TickerObserver
from bitfinex import BitFinex
from gdax import GDAX
from binance import Binance
from bitmex import BitMEX

from counters import rates_monitor

# TODO :
# kraken
# - bitmex
# - gdax
# - bitfinex
# - binance

obs = TickerObserver()

Exchanges = [
    # BitFinex(ticker_observer=obs, markets=BitFinex.all_markets),
    # BitMEX(ticker_observer=obs, markets=BitMEX.all_markets),
    BitMEX(ticker_observer=obs, markets=['btc_usd', 'eth_btc', 'ltc_btc']),
    BitFinex(ticker_observer=obs, markets=['btc_usd', 'eth_btc', 'btc_eur', 'eth_usd']),

    GDAX(ticker_observer=obs, markets=['btc_usd', 'btc_eur', 'eth_eur', 'eth_usd', 'eth_btc']),

    # GDAX(ticker_observer=obs, markets=GDAX.all_markets),
    # Binance(ticker_observer=obs, markets=Binance.all_markets),

    Binance(ticker_observer=obs, markets=['eth_btc', 'ltc_btc', ]),

    # Binance(markets=['eth_btc', ])#, 'bnb_btc', 'eos_btc']),
    # BitMEX(markets=['btc_usd'], ticker_observer=obs)#, 'ada_btc', 'bch_btc', 'xrp_btc', 'btc_usd', 'eth_btc', 'ltc_btc']),

    # Binance(markets=['eth_btc', ])
    # GDAX(markets=['ltc_usd', ]),
    # CryptoExchange(url="wss://api.bitfinex.com/ws/", symbol="BTCUSD"),
]


async def closer():
    while True:
        await asyncio.sleep(5)
        exchange = random.choice(Exchanges)
        name = exchange.__class__.__name__
        print('>>> closing', name)
        await exchange.close()
        print('CLOSED', name)


def main():
    # logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    # loop.set_debug(True)
    try:
        run_all = [exchange.run() for exchange in Exchanges] + [rates_monitor()]  # + [closer()]
        asyncio.gather(*run_all)
        loop.run_forever()
    except KeyboardInterrupt:
        loop.stop()
        # Find all running tasks:
        pending = asyncio.Task.all_tasks()
        # Run loop until tasks done:
        loop.run_until_complete(asyncio.gather(*pending))

        print("Shutdown complete ...")
    finally:
        loop.close()


if __name__ == '__main__':
    main()
