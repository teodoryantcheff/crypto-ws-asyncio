import asyncio
import time
from collections import deque


class Counter(object):
    cnt = dict()

    # in millis
    SAMPLE_PERIOD = 500
    QUEUE_LEN = 5

    # def register(self, key):
    #     self.cnt[key] = 0, 0, _now_ts()

    def tick(self, key):
        now = _now_ts()
        try:
            count, rate, last_ts, q = self.cnt[key]
            count += 1
            since = now - last_ts
            if since >= Counter.SAMPLE_PERIOD:
                rate = (count / since) * 1000.0
                q.append(rate)
                last_ts = now
                count = 0
            self.cnt[key] = count, rate, last_ts, q
        except KeyError:
            self.cnt[key] = 1, 0, now, deque(list(), maxlen=Counter.QUEUE_LEN)


c = Counter()


async def rates_monitor():
    while True:
        print('=== Message rates ==================================================')
        global_rate = 0
        for key, val in c.cnt.items():
            _, _, last_ts, q = val
            rate = sum(q) / len(q) if len(q) > 0 else 0
            q_str = ' '.join(['{:7.1f}'.format(samp) for samp in reversed(q)])
            print(f'{key:10s} | {rate:7.1f}/s | {last_ts:12d} | {q_str}')
            global_rate += rate
        print('Global rate  {:7.1f}/s'.format(global_rate))

        await asyncio.sleep(2 * Counter.SAMPLE_PERIOD / 1000.0)  # niquist :)


def _now_ts():
    return int(time.time() * 1000)
