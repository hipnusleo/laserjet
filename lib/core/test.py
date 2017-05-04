#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
    @Author:        yyg
    @Create:        2016MMDD
    @LastUpdate:    2016MMDD HH:MM:SS
    @Version:       0.0
"""

from loggers import LaserjetLogger
from multiprocessing import Manager, Pool, Queue
from logging import getLogger
import sys

def print_func(queue):
    while true:
        info = queue.get_nowait()
        #logger = getLogger(LOGGER_NAME)
        sys.stderr.write("info = {0}".format(info))
    queue.task_done()


if __name__ == "__main__":
    init_logger = LaserjetLogger()
    logger = getLogger(LOGGER_NAME)
    m = Manager()
    info_queue = m.Queue()
    s = Queue()
    s.empty()
    for i in range(100):
        info_queue.put_nowait(i)
        logger.info(i)
    info_queue.join()
    pro_pool = Pool()
    pro_pool.apply_async(print_func, (info_queue,))
    pro_pool.close()
    pro_pool.join()