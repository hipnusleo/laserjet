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

logger = getLogger(LOGGER_NAME)
action_options = action_options
batch_conf = batch_conf


class MTerminal(object):
    """
    By putting all ssh accessing authentication information into _host_queue,
    allows worker processes in worker_pool to handle each remote server.
    """

    def __init__(self):
        # self._batch_options = BatchOption()
        self._batch_options = action_options
        self._host_queue = Manager().JoinableQueue()
        self._batch_conf = batch_conf
        self.hosts = self._batch_conf.batch_hosts_generator()
        self.logger = LaserjetLogger()

    def _load_hosts_queue(self):
        host_list = list()
        host_num = 1
        for each in self.hosts:
            self._host_queue.put_nowait(each)
            logger.debug(
                "Put host{0} [{1}] to host queue ".format(
                    host_num,
                    each["hostname"])
            )
            host_num += 1
            host_list.append(each["hostname"])
            # self._host_queue.join()
            logger.debug("worker_pool join")
        logger.info("Batch process on {0} hosts: {1}".format(
            (host_num - 1),
            host_list))
        return (host_num - 1)

    def run(self):
        if not argv[1:]:
            logger.info(batch_conf.get_laserjet_host())
            self._batch_options.get_help()
            logger.info("You forget to add batch option! "
                        "Plz use \"-h\" to see available options")
        else:
            worker_pool = Pool()
            logger.info(
                "A multiprocessing pool with size of "
                "%d has been activated" % cpu_count())
            _action_funcs = self._batch_options.get_actions()
            host_len = self._load_hosts_queue()
            continue_enable = raw_input(
                "Are you sure to launch remote tasks"
                " on above hosts?(press \"y\" for yes:)"
            )
            if continue_enable is 'y':
                try:
                    start_time = clock()
                    logger.info("Worker pool start working %8s" % ("###"))
                    for cpu in xrange(host_len):
                        worker_pool.apply_async(
                            action_dispatcher,
                            args=(self._host_queue, _action_funcs,)
                        )
                    end_time = clock()
                    logger.info("Total Time: %ds" % (start_time - end_time))
                    worker_pool.close()
                    logger.debug("worker_pool closed")
                    worker_pool.join()
                    logger.debug("worker_pool done apply_async !!")
                except (KeyboardInterrupt, SystemExit):
                    raise
                except TimeoutError:
                    logger.exception(
                        "Worker process timeout, worker pool terminated")
                except:
                    logger.exception("MTermial.run() encounters errors")

            else:
                logger.info("Task Canceled ... ")


# def get_ssh_client(host):
#    _ssh_client = SSHClient()
#    logger.debug("Get host info = {0}".format(host))
#    _ssh_client.load_system_host_keys()
#    logger.debug("Done loading system host keys")
#    _ssh_client.set_missing_host_key_policy(AutoAddPolicy())
#    logger.debug("Done setting missing host key policy")
#    _ssh_client.connect(**host)
#   return _ssh_client
def get_ssh_client(host):
    _ssh_client = SSHClient()
    logger.debug("Get host info = {0}".format(host))
    _ssh_client.load_system_host_keys()
    logger.debug("Done loading system host keys")
    _ssh_client.set_missing_host_key_policy(AutoAddPolicy())
    logger.debug("Done setting missing host key policy")
#    _ssh_client.connect(**host)
    return [_ssh_client, host]


def action_dispatcher(host_queue, action_funcs):
    try:
        logger.debug("Trying to get ssh client from host queue")
        host_info = host_queue.get()
        _ssh_client = get_ssh_client(host_info)
        for action_func in action_funcs:
            logger.info("action_func = %s" % action_func)
            action_func(_ssh_client, host_info)
        host_queue.task_done()
        logger.info(
            "process %s has done its task" % getpid())
    except (KeyboardInterrupt, SystemExit):
        raise
    except Empty:
        logger.info("host_queue is Empty now")
    except:
        logger.exception("action_dispatcher encounters error")


if __name__ == "__main__":
    pass
