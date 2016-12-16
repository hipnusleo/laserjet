#!/usr/bin/env python
#coding:utf-8

import logging
import logging.handlers
import os
import threading
import sys


class ZLogging:
    def __init__(self):
        self.inited = False
        self._logger_lock = threading.Lock()

    def initLogger(self):
        with self._logger_lock:
            if self.inited is True:
                return
            self.inited = True
            logdir = './logs'
            logfile = sys.argv[0][sys.argv[0].rfind(os.sep)+1:]
            if logfile.endswith('.py'):
                logfile = logfile[:len(logfile) - 3]
            logfile = '%s.log' % logfile
            logfile = os.path.join(logdir, logfile)
            logfile = os.path.abspath(logfile)
            # print 'log filename: ', logfile
            if not os.path.isdir(logdir):
                os.makedirs(logdir)

            logger = logging.getLogger()
            formatstr = "%(levelname)s %(asctime)s %(filename)s:%(lineno)d - %(message)s"
            formatter = logging.Formatter(formatstr)
            # create a handler to write log file
            rotateLog = logging.handlers.RotatingFileHandler(logfile, "a", 10000000, 25)
            rotateLog.setFormatter(formatter)
            logger.addHandler(rotateLog)
            # create a handler to write console
            console = logging.StreamHandler()
            console.setFormatter(formatter)
            logger.addHandler(console)

            logging.basicConfig(format=formatstr, level=logging.INFO, filename=logfile)
            logger.setLevel(logging.INFO)
