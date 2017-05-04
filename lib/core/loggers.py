#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    @Author:        yyg
    @Create:        2016MMDD
    @LastUpdate:    2016-12-15 HH:MM:SS
    @Version:       0.0
"""
from json import load
from logging import (Formatter, _defaultFormatter, exception,
                     getLogger, FileHandler, basicConfig, StreamHandler)
from cloghandler import ConcurrentRotatingFileHandler
from params import (LOG_CONF_FILE, LOG_LVL, LOGGER_NAME,
                    LOG_FILE, LOG_DAT_FMT, LOG_FMT)


class LaserjetLogger(object):
    """
    Compatible to python 2.6+

    """

    def __init__(self):
        self.fmt = LOG_FMT
        self.datefmt = LOG_DAT_FMT
        self._start()

    def _start(self):
        logger = getLogger(LOGGER_NAME)
        log_handler = ConcurrentRotatingFileHandler(LOG_FILE)
        log_formatter = Formatter(self.fmt, self.datefmt)
        log_handler.setFormatter(log_formatter)
        console_handler = StreamHandler()
        console_handler.setFormatter(log_formatter)
        logger.setLevel(LOG_LVL)
        logger.addHandler(log_handler)
        logger.addHandler(console_handler)
        logger.info("Logger activated")


def print_func(anything_str):
    log = getLogger(LOGGER_NAME)
    log.info(anything_str)


if __name__ == "__main__":
    logger = LaserjetLogger()
    test_pool = Pool()
    for i in range(5):
        test_pool.apply_async(print_func, args=(i,))
    test_pool.close()
    test_pool.join()
