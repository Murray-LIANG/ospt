import functools
import logging
from logging import handlers
import time
from contextlib import contextmanager

from ospt import exceptions as ospt_ex

LOG = logging.getLogger()


def setup_log(file_path=None, level=logging.INFO, to_stdout=True,
              max_bytes=104857600, max_file_count=5):
    fmt_str = ('%(asctime)-15s %(name)-8s %(threadName)s '
               '%(levelname)-4s %(message)s')
    fmt = logging.Formatter(fmt_str)
    # Set root logger to `level` or it would be warning which will
    # suppress logs lower than warning.
    root = logging.getLogger()
    root.setLevel(level)
    if to_stdout:
        console = logging.StreamHandler()
        console.setLevel(level)
        console.setFormatter(fmt)
        root.addHandler(console)
    if file_path:
        file_handler = handlers.RotatingFileHandler(
            filename=file_path, maxBytes=max_bytes, backupCount=max_file_count)
        file_handler.setLevel(level)
        file_handler.setFormatter(fmt)
        root.addHandler(file_handler)


@contextmanager
def timer():
    class _Time(object):
        def __init__(self, time_start):
            self.start = time_start
            self.end = None

        @property
        def interval(self):
            return self.end - self.start

    _timer = _Time(time.time())
    try:
        yield _timer
    finally:
        _timer.end = time.time()


def to_str(resource):
    if isinstance(resource, list) or isinstance(resource, tuple):
        return ':'.join(to_str(each) for each in resource)

    from ospt.control import Resource as OsptRes
    if isinstance(resource, OsptRes):
        return str(resource)

    from storops.lib.resource import Resource as StoropsRes
    if isinstance(resource, StoropsRes):
        return 'id={},name={}'.format(resource.get_id(), resource.name)

    return str(resource)


def timeit(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        LOG.info('%s: %s.', func.__name__, to_str(args))
        with timer() as t:
            result = func(*args, **kwargs)
        LOG.info('TIME: %s, %s: %s.', t.interval, func.__name__, to_str(args))
        return result

    return _wrapper


def wait_until(res_manager, res_id, criteria, timeout=1200):
    start_point = time.time()
    while True:
        if time.time() - start_point > timeout:
            raise ospt_ex.TimeoutError(
                'Timeout before {} becoming {}. {} sec passed.'.format(
                    res_id, criteria, timeout))
        time.sleep(1)
        try:
            res = res_manager.get(res_id)
        except Exception as ex:
            if isinstance(ex, criteria):
                break

        if res.status == criteria:
            break


def sort_by_name(resources):
    return sorted(resources, key=lambda x: x.name)
