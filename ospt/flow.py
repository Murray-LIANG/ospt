import logging
import time
from multiprocessing import dummy as multithread

from ospt import utils

LOG = logging.getLogger()


class Flow(object):
    def __init__(self, func, pattern=None):
        self.func = func
        self.pattern = pattern

    def map(self, data, threads_num=None):
        def _wrapper(index, tup):
            if not self.pattern:
                time.sleep(index * self.pattern)
            return self.func(*tup)

        number = len(data) if threads_num is None else threads_num
        threads = multithread.Pool(number)

        with utils.timer() as t:
            result = threads.map(_wrapper, enumerate(data))
        LOG.info('Total time: %s, %s', self.func.__name__, t.interval)
        return result
