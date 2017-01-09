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
from utils import record_log, sftp_conn, ssh_conn, unicode_list_normalize

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
        logger.info("Waiting 2s for result zzz zzz ")
        _stdout = unicode_list_normalize(_stdout.readlines())
        _stderr = unicode_list_normalize(_stderr.readlines())
        if _stdout:
            logger.info("run '%s' : %s" % (_mkdir, _stdout))
        if _stderr:
            logger.error("run '%s' : %s" % (_mkdir, _stderr))
        logger.info("Done mkdir '%s'" % _mkdir)
        _sftp_client.put(INSPECT_SCRIPT, INSPECT_SCRIPT_REMOTE)
        _run_script = "python %s %s %s" % (
            INSPECT_SCRIPT_REMOTE, hostname, INSPECT_DIR)
        _stdin, _stdout, _stderr = _ssh_client.exec_command(_run_script)
        _stdout = unicode_list_normalize(_stdout.readlines())
        _stderr = unicode_list_normalize(_stderr.readlines())
        if _stdout:
            logger.info("run %s :\n%s" % (_run_script, _stdout))
        if _stderr:
            logger.error("run %s :\n%s" % (_run_script, _stderr))
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
    try:
        _sftp_client = sftp_conn(host_info)
        hostname = host_info["hostname"]
        for file_for_sync in batch_conf.get_batch_sync():
            logger.info("Syncing @%s " % hostname)
            _local = file_for_sync["localpath"]
            _remote = file_for_sync["remotepath"]
            skip = (hostname == laserjet_host) and (_local == _remote)
            logger.debug("skip = {0}".format(skip))
            if skip:
                logger.info("Sync action skipped on %s" % hostname)
                continue
            _sftp_client.put(_local, _remote)
            logger.info(
                "Sync from local \"%s\" to  remote @%s:%s" % (
                    _local, hostname, _remote))
        _sftp_client.close()
        logger.info("sftp conn closed")
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception as e:
        logger.exception("Sync failed since  \n%s" % e)


@action_options.add_method("exec")
def _batch_exec(host_info):
    try:
        _ssh_client = ssh_conn(host_info)
        hostname = host_info["hostname"]
        logger.debug("Start Executing commands @%s" % hostname)
        for cmd in batch_conf.get_batch_cmds():
            cmd_stdin, cmd_stdout, cmd_stderr = _ssh_client.exec_command(
                cmd)
            logger.debug("Done executing \"%s\" on @ %s" % (cmd, hostname))
            cmd_stdout = unicode_list_normalize(cmd_stdout.readlines())
            cmd_stderr = unicode_list_normalize(cmd_stderr.readlines())
            if len(cmd_stdout):
                logger.info("Command result@%s is :\n%s" %
                            (hostname, cmd_stdout))
            if len(cmd_stderr):
                logger.error("Failed in executing %s" % cmd)
                logger.error("%s: \n%s" % (hostname, cmd_stdout))
        _ssh_client.close()
        logger.info("Done executing commands @%s" % hostname)
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception as e:
        logger.exception("Exec failed since \n%s" % e)


@action_options.add_method("fetch")
def _batch_fetch(host_info):
    try:
        _sftp_client = sftp_conn(host_info)
        hostname = host_info["hostname"]
        for file_for_fetch in batch_conf.get_batch_fetch():
            _remote = file_for_fetch["remotepath"]
            logger.debug("_remote = %s" % _remote)
            _local = "".join([file_for_fetch["localpath"], ".", hostname])
            logger.debug("_local = %s" % _local)
            _sftp_client.get(_remote, _local)
            logger.info("Done fetch from {0} @{1} to local \"{2}\"".format(
                hostname, _remote, _local))
            logger.exception("Batch fetch encounters error")
        _sftp_client.close()
        logger.info("Done fetching from @%s" % hostname)
        logger.debug("Close sftp client")
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception as e:
        logger.exception("Fetch failed since \n%s" % e)
