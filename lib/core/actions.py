#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
    @Author:        yyg
    @Create:        2016-MM-DD
    @LastUpdate:    2016-12-DD HH:MM:SS
    @Version:       0.0
"""
import inspect
from logging import getLogger

from paramiko import SFTPClient, SSHClient

from options import BatchOption
from params import (INSPECT_COLLECT_DIR, INSPECT_DIR, INSPECT_SCRIPT,
                    LASERJET_HOST, LOGGER_NAME, BatchConf)
from utils import record_log, sftp_conn, ssh_conn
from os.path import join
logger = getLogger(LOGGER_NAME)
action_options = BatchOption()
batch_conf = BatchConf()
laserjet_host = batch_conf.get_laserjet_host()
laserjet_host = laserjet_host.strip()


@action_options.add_method("inspect")
def _batch_inspect(host_info):
    hostname = host_info["hostname"]
    _ssh_client = ssh_conn(host_info)
    _sftp_client = _ssh_client.open_sftp()
    _sftp_client.mkdir(INSPECT_COLLECT_DIR)
    _sftp_client.put(INSPECT_SCRIPT, INSPECT_DIR)
    _stdin, _stdout, _stderr = _ssh_client.exec_command(
        "python %s %s" % (INSPECT_SCRIPT, hostname))
    _sftp_client.get(join(INSPECT_DIR, (hostname + "json")),
                     INSPECT_COLLECT_DIR)


@action_options.add_method("distribute")
def _batch_distribute(host_info):
    _sftp_client = sftp_conn(ssh_client[0])
    if isinstance(_sftp_client, SFTPClient):
        pass


@action_options.add_method("sync")
def _batch_sync(host_info):
    _sftp_client = sftp_conn(host_info)
    if isinstance(_sftp_client, SFTPClient):
        hostname = host_info["hostname"]
        logger.info("Start Syncing @%s " % hostname)
        for file_for_sync in batch_conf.get_batch_sync():
            try:
                local = file_for_sync["localpath"]
                remote = file_for_sync["remotepath"]
                skip = (hostname == laserjet_host) and (local == remote)
                logger.info("skip = {0}".format(skip))
                if skip:
                    logger.info("Sync task skipped on % s, since copy local \"%s\""
                                " to local \"%s\"" %
                                (laserjet_host, local, remote))
                    continue
                logger.info(
                    "Done copy from \"{0}\" to  @{2}:\"{1}".format(
                        file_for_sync["localpath"],
                        file_for_sync["remotepath"],
                        hostname
                    )
                )
                _sftp_client.put(local, remote)
                _sftp_client.close()
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                break
                logger.exception("Batch sync encounters error")
        logger.info(
            "Done Syncing files @{0}".format(hostname))
        logger.debug("Close sftp_client")
    else:
        logger.error(
            "while running {0}# found input {1} is not an instance of paramiko SSHClient".format(
                inspect.currentframe().f_code.co_name,
                ssh_client)
        )


@action_options.add_method("exec")
def _batch_exec(host_info):
    _ssh_client = ssh_conn(host_info)
    if isinstance(_ssh_client, SSHClient):
        hostname = host_info["hostname"]
        logger.debug("Start Executing commands @%s" % hostname)
        for cmd in batch_conf.get_batch_cmds():
            try:
                cmd_stdin, cmd_stdout, cmd_stderr = _ssh_client.exec_command(
                    cmd)
                logger.debug("Done executing \"%s\" on @ %s" % (cmd, hostname))
                logger.info("command result is blow:\n {0}".format(
                    cmd_stdout.read()))
            except:
                logger.exception("Batch exec encounters error")
        _ssh_client.close()
        logger.info(
            "Done executing commands, ssh connection to %s closed" % hostname)
    else:
        logger.error(
            "Method [{0}] found input \"1\" isn't"
            " an instance of SSHClient".format(
                inspect.currentframe().f_code.co_name,
                ssh_client)
        )


@action_options.add_method("fetch")
def _batch_fetch(host_info):
    _sftp_client = sftp_conn(host_info)
    if isinstance(_sftp_client, SFTPClient):
        hostname = host_info["hostname"]
        for file_for_fetch in batch_conf.get_batch_fetch():
            try:
                _remote = file_for_fetch["remotepath"]
                _local = str(file_for_fetch["localpath"] + "." + hostname)
                _sftp_client.get(_remote, _local)
                _sftp_client.close()
                logger.info("Done fetch from {0} @{1} to local \"{2}\"".format(
                    hostname, _remote, _local))
            except:
                logger.exception("Batch fetch encounters error")
                raise SystemExit
        logger.info("Done fetching @{0}".format(
            hostname
        ))
        _sftp_client.close()
        logger.info("Close sftp client")
    else:
        logger.error(
            "while running method [{0}] found input \"1\" is not an instance of paramiko SSHClient".format(
                inspect.currentframe().f_code.co_name,
                ssh_client))
