import ujson
import json
from operator import itemgetter
import random

from sortedcollection import SortedCollection

import time


class MyTimer():

    def __init__(self):
        self.start = time.time()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end = time.time()
        runtime = end - self.start
        msg = 'The function took {time} millis to complete'
        print(msg.format(time=runtime * 1000))


symbol = 'test'  # self._pair_names_map[data['product_id']]
order_books = dict()
order_books[symbol] = dict()


def on_orderbook_snapshot(data):
    order_books[symbol]['bids'] = SortedCollection(
        [[float(pq) for pq in bid]
         for bid in data['bids']], key=itemgetter(0)
    )

    order_books[symbol]['asks'] = SortedCollection(
        [[float(pq) for pq in ask]
         for ask in data['asks']], key=itemgetter(0)
    )


def l2update(data):
    side, p, q = data
    p, q = float(p), float(q)

    book = order_books[symbol]['asks'] if side == 'sell' else order_books[symbol]['bids']

    try:
        el = book.find(p)
        if q == 0:  # delete from orderbook
            book.remove(el)  # delete order at price level p
    except ValueError:
        book.insert([p, q])


if __name__ == '__main__':
    with open('data.json', 'r') as f:
        ftext = f.read()
        jsdata = json.loads(ftext)
        on_orderbook_snapshot(jsdata)
        # with MyTimer():
        #     for _ in range(100):
        with MyTimer():
            for _ in range(10000):
                l2update([
                    random.choice(['sell', 'buy']),  # side
                    random.random() * 1000.0,  # price
                    random.random() * 10.0,  # quantity
                ])
