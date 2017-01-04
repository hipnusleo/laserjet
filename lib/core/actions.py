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
from os.path import isfile, join
from time import sleep
from paramiko import SFTPClient, SSHClient

from options import BatchOption
from params import (INSPECT_COLLECT_DIR, INSPECT_DIR, INSPECT_SCRIPT,
                    INSPECT_SCRIPT_REMOTE, LASERJET_HOST, LOGGER_NAME,
                    BatchConf)
from utils import record_log, sftp_conn, ssh_conn

logger = getLogger(LOGGER_NAME)
action_options = BatchOption()
batch_conf = BatchConf()
laserjet_host = batch_conf.get_laserjet_host()
laserjet_host = laserjet_host.strip()


@action_options.add_method("inspect")
def _batch_inspect(host_info):
    try:
        hostname = host_info["hostname"]
        _ssh_client = ssh_conn(host_info)
        _sftp_client = _ssh_client.open_sftp()
        _mkdir = "mkdir -p %s" % INSPECT_COLLECT_DIR  # /tmp/laserjet/cluster
        _stdin, _stdout, _stderr = _ssh_client.exec_command(_mkdir)
        logger.info("Waiting for result zzz zzz ")
        sleep(3)
        logger.info("run '%s' : %s" % (_mkdir, _stdout.readlines()))
        logger.error("run '%s' : %s" % (_mkdir, _stderr.readlines()))
        logger.info("Done mkdir '%s'" % _mkdir)
        # /tmp/laserjet/inspect.py
        _sftp_client.put(INSPECT_SCRIPT, INSPECT_SCRIPT_REMOTE)
        _run_script = "python %s %s %s" % (
            INSPECT_SCRIPT_REMOTE, hostname, INSPECT_DIR)
        _stdin, _stdout, _stderr = _ssh_client.exec_command(_run_script)
        logger.info("run script '%s'" % (_run_script))
        for each in _stdout.readlines():
            logger.info("%s" % each)
        for each in _stderr.readlines():
            if each:
                logger.error("%s" % (each))
        logger.info("Done running inspect.py: '%s'" % _run_script)
        _remote_report = join(INSPECT_DIR, (hostname + ".json"))
        _local_report = join(INSPECT_COLLECT_DIR, (hostname + ".json"))
        _sftp_client.get(_remote_report, _local_report)
        logger.info("Get Report %s from remote @%s" %
                    (_remote_report, hostname))
    except (KeyboardInterrupt, SystemExit):
        raise

    except:
        logger.exception("Failed in 'inspect': ")


@action_options.add_method("sync")
def _batch_sync(host_info):
    _sftp_client = sftp_conn(host_info)
    if isinstance(_sftp_client, SFTPClient):
        hostname = host_info["hostname"]
        logger.info("Start Syncing @%s " % hostname)
        for file_for_sync in batch_conf.get_batch_sync():
            try:
                _local = file_for_sync["localpath"]
                _remote = file_for_sync["remotepath"]
                skip = (hostname == laserjet_host) and (local == remote)
                logger.info("skip = {0}".format(skip))
                if skip:
                    logger.info("Sync task skipped on %s" % hostname)
                    continue
                logger.info(
                    "Done copy from \"%s\" to  @%s:%s" % (
                        _local, hostname, _remote))
                _sftp_client.put(_local, _remote)
                _sftp_client.close()
                logger.info("sftp conn closed")
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                logger.exception("Batch sync encounters error")
        logger.info(
            "Done Syncing @%s" % (hostname))
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
                if len(cmd_stdout.readlines()) > 0:
                    logger.info("command result is: %s" % (
                        cmd_stdout.readlines()))
                if len(cmd_stderr.readlines()) > 0:
                    logger.error("command throws : %s" %
                                 (cmd_stderr.readlines()))
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
                logger.debug("_remote = %s" % _remote)
                _local = "".join([file_for_fetch["localpath"], ".", hostname])
                logger.debug("_local = %s" % _local)
                _sftp_client.get(_remote, _local)
                logger.info("Done fetch from {0} @{1} to local \"{2}\"".format(
                    hostname, _remote, _local))
                _sftp_client.close()
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                break
                logger.exception("Batch fetch encounters error")
        logger.info("Done fetching @{0}".format(
            hostname
        ))
        logger.info("Close sftp client")
    else:
        logger.error(
            "while running method [{0}] found input \"1\" is not an instance of paramiko SSHClient".format(
                inspect.currentframe().f_code.co_name,
                ssh_client))
