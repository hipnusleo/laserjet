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
import traceback
from multiprocessing import JoinableQueue, Pool, cpu_count, Manager
from sys import argv, stderr
from paramiko import AutoAddPolicy, SSHClient
from logging import getLogger
from loggers import LaserjetLogger
from options import BatchOption
from params import BatchConf, LOGGER_NAME
from os import getpid


logger = getLogger(LOGGER_NAME)
action_options = BatchOption()
batch_conf = BatchConf()


@action_options.add_method("sync")
def _batch_sync(ssh_client, hostname):
    if isinstance(ssh_client, SSHClient):
        _sftp_client = ssh_client.open_sftp()
        logger.info(">>>>>>>>>>>> Start syncing file <<<<<<<<<<<<")
        for file_for_sync in batch_conf.get_batch_sync():
            _sftp_client.put(
                file_for_sync["localpath"],
                file_for_sync["remotepath"]
                )
            logger.info(
                "Done copy from \"{0}\" to  @{2}:\"{1}\"".format(
                    file_for_sync["localpath"],
                    file_for_sync["remotepath"],
                    hostname
                )
                )
        logger.info(">>>>>>>> Done syncing files @{0} <<<<<<<<<<<<".format(hostname))
        _sftp_client.close()
        logger.debug("Close sftp_client")
    else:
        logger.error(
            "while running method <{0}> found input {1} is not an instance of paramiko SSHClient".format(
                  inspect.currentframe().f_code.co_name,
                  ssh_client)
                  )


@action_options.add_method("exec")
def _batch_exec(ssh_client, hostname):
    if isinstance(ssh_client, SSHClient):
        logger.info(">>>>>>>>>>>> Start executing commands <<<<<<<<<<<<")
        for cmd in batch_conf.get_batch_cmds():
            try:
                cmd_stdin, cmd_stdout, cmd_stderr = ssh_client.exec_command(cmd)
                logger.info("Done executing command-[{0}]@{1}".format(
                    cmd,
                    hostname
                ))
                logger.info("command result is: {0}".format(cmd_stdout.read()))
            except:
                logger.exception("Batch exec encounters error")
        logger.info(">>>>>>>>>>>> Done executing commands @{0} <<<<<<<<<<<<".format(
            hostname
        ))
        ssh_client.close()
        logger.debug("Close ssh_client")
    else:
        logger.error(
            "while running method [{0}] found input \"1\" is not an instance of paramiko SSHClient".format(
                inspect.currentframe().f_code.co_name,
                ssh_client)
        )


@action_options.add_method("fetch")
def _batch_fetch(ssh_client, hostname):
    if isinstance(ssh_client, SSHClient):
        try:
            _sftp_client = ssh_client.open_sftp()
            logger.info(">>>>>>>>>>>> Start fetching <<<<<<<<<<<<")
            for file_for_fetch in batch_conf.get_batch_fetch():
                _sftp_client.get(
                    file_for_fetch["remotepath"],
                    file_for_fetch["localpath"]
                )
                logger.info("Done fetch from \"{0}\"@{1} to \"{2}\"".format(
                    hostname,
                    file_for_fetch["remotepath"],
                    file_for_fetch["localpath"]
                ))
            logger.info(">>>>>>>>>>>> Done fetching @{0} <<<<<<<<<<<".format(
                hostname
            ))
            _sftp_client.close()
            logger.info("Close sftp client")
        except:
            logger.exception("Batch fetch encounters error")
    else:
        logger.error(
            "while running method [{0}] found input \"1\" is not an instance of paramiko SSHClient".format(
                  inspect.currentframe().f_code.co_name,
                  ssh_client)
                  )


class MTerminal(object):
    """
    By putting all ssh accessing authentication information into _host_queue,
    allows worker processes in worker_pool to handle each remote server.
    """
    def __init__(self):
        #self._batch_options = BatchOption()
        self._batch_options = action_options
        self._host_queue = Manager().JoinableQueue()
        self._batch_conf = batch_conf
        self.hosts = self._batch_conf.batch_hosts_generator()
        self.logger = LaserjetLogger()

    def _load_hosts_queue(self):
        host_list = list()
        for each in self.hosts:
            self._host_queue.put_nowait(each)
            logger.debug(
                "Put host [{0}] to host queue".format(each["hostname"])
                )
            logger.debug(type(each))
            host_list.append(each["hostname"])
        logger.info("Batch process on hosts: {0}".format(host_list))

    def run(self):
        if not argv[1:]:
            self._batch_options.get_help()
            logger.info("You forget to add batch option! ")
            logger.info("Plz use \"-h\" to see available options")
        else:
            worker_pool = Pool()
            logger.info(
                "Launch a worker_pool Pool with size of {0}".format(
                    cpu_count()
                    )
                )
            _action_funcs = self._batch_options.get_actions()
            self._load_hosts_queue()
            continue_enable = raw_input(
                "Only when \"y\" is pressed, job continues: "
                )
            if continue_enable == 'y':
                logger.debug("continue_enable is true")
                logger.debug("worker_pool start working ... ... ")
                worker_pool.apply_async(
                    action_dispatcher,
                    args=(self._host_queue, _action_funcs,)
                    )
                logger.debug("worker_pool done apply_async !!")
                self._host_queue.join()
                logger.debug("block host queue until its empty")
                worker_pool.close()
                logger.debug("worker_pool close")
                worker_pool.join()
                logger.debug("worker_pool join")
            else:
                logger.info("Task Canceled ... ")


def get_ssh_client(host):
    _ssh_client = SSHClient()
    logger.debug("Get host info = {0}".format(host))
    _ssh_client.load_system_host_keys()
    logger.debug("Done loading system host keys")
    _ssh_client.set_missing_host_key_policy(AutoAddPolicy())
    logger.debug("Done setting missing host key policy")
    _ssh_client.connect(**host)
    return _ssh_client


def action_dispatcher(host_queue, action_funcs):
    try:
        logger.debug("Trying to get ssh client from host queue")
        host_info = host_queue.get()
        _ssh_client = get_ssh_client(host_info)
        for action_func in action_funcs:
            logger.debug("action_func = {0}".format(action_func))
            action_func(_ssh_client, host_info["hostname"])
        host_queue.task_done()
        logger.debug("process[{0}] has done its task".format(getpid()))
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        logger.exception("action_dispatcher encounters error")

if __name__ == "__main__":
    test = BatchOption()
    print test.get_action_options()
    print action_options.get_action_options()