#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    @Author:        yyg
    @Create:        2016MMDD
    @LastUpdate:    2016-12-15 HH:MM:SS
    @Version:       0.0
        #
"""
import inspect
from logging import getLogger
from multiprocessing import (Manager, Pool, TimeoutError, cpu_count,
                             current_process)
from os import getpid
from Queue import Empty
from sys import argv, stderr
from time import clock

from paramiko import AutoAddPolicy, SSHClient

from actions import action_options, batch_conf
from loggers import LaserjetLogger
from params import LOGGER_NAME
from assemble import Assembler
from utils import StopWatch

logger = getLogger(LOGGER_NAME)
action_options = action_options
batch_conf = batch_conf


class MTerminal(object):
    """
    By putting all ssh accessing authentication information into _host_queue,
    allows worker processes in worker_pool to handle each remote server.
    """

    def __init__(self):
        self._batch_options = None
        self._host_queue = None
        self._batch_conf = None
        self.hosts = None
        self.logger = LaserjetLogger()

    def _setup(self):
        self._batch_options = action_options
        self._host_queue = Manager().JoinableQueue()
        self._batch_conf = batch_conf
        self.hosts = self._batch_conf.batch_hosts_generator()
        logger.info("Done MTerminal setup")

    def _load_hosts_queue(self):
        host_list = list()
        host_num = 0
        for each in self.hosts:
            self._host_queue.put_nowait(each)
            logger.debug("Put host%d [%s] to host queue" % (host_num,
                                                            each["hostname"]))
            host_num += 1
            host_list.append(each["hostname"])
        logger.info("Batch process on {0} hosts: \n{1}".format(
            host_num, host_list))
        return host_num

    def run(self):
        self._setup()
        if not argv[1:]:
            logger.info(batch_conf.get_laserjet_host())
            self._batch_options.get_help()
            logger.info("You forget to add batch option! "
                        "Plz use \"-h\" to see available options")
        else:
            worker_pool = Pool()
            logger.info(
                "Pool(%d/%d) activated" % (cpu_count(), cpu_count()))
            host_len = self._load_hosts_queue()
            _action_funcs = self._batch_options.get_actions()
            _action_names = self._batch_options.get_action_name()
            continue_enable = raw_input(
                "Are you sure to launch remote tasks"
                " on above hosts?(press \"y\" for yes:)"
            )
            if continue_enable is 'y':
                try:
                    _timer = StopWatch()
                    logger.info("Worker pool start working %8s" % ("###"))
                    for cpu in xrange(host_len):
                        worker_pool.apply_async(
                            action_dispatcher,
                            args=(self._host_queue, _action_funcs,)
                        )
                    worker_pool.close()
                    logger.debug("worker_pool closed")
                    worker_pool.join()
                    if "inspect" in _action_names:
                        # do assemble
                        assembler = Assembler()
                        assembler.start()
                    logger.info("Mission accomplished in %s seconds" %
                                (_timer.timer()))
                except (KeyboardInterrupt, SystemExit):
                    raise
                except TimeoutError:
                    logger.exception(
                        "Worker process timeout, worker pool terminated")
                except:
                    logger.exception("MTermial.run() encounters errors")

            else:
                logger.info("Task Canceled ... ")

    def pull(self):
        pass


def action_dispatcher(host_queue, action_funcs):
    try:
        logger.debug("Trying to get ssh client from host queue")
        host_info = host_queue.get()
        for action_func in action_funcs:
            logger.debug("action_func = %s" % action_func)
            action_func(host_info)
        host_queue.task_done()
        logger.debug("process %s has done its task" % getpid())
    except (KeyboardInterrupt, SystemExit):
        raise
    except Empty:
        logger.exception("host_queue is Empty")
    except:
        logger.exception("action_dispatcher encounters error")


if __name__ == "__main__":
    pass
