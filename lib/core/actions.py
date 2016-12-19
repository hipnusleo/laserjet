#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
    @Author:        yyg
    @Create:        2016MMDD
    @LastUpdate:    2016MMDD HH:MM:SS
    @Version:       0.0
"""
import inspect
from logging import getLogger

from paramiko import SSHClient

from options import BatchOption
from params import LOGGER_NAME, BatchConf, LASERJET_HOST

logger = getLogger(LOGGER_NAME)
action_options = BatchOption()
batch_conf = BatchConf()
laserjet_host = batch_conf.get_laserjet_host()
laserjet_host = laserjet_host.strip()


@action_options.add_method("sync")
def _batch_sync(ssh_client, host_info):
    if isinstance(ssh_client[0], SSHClient):
        hostname = host_info["hostname"]
        _ssh_client = ssh_client[0]
        _ssh_client.connect(**ssh_client[1])
        _sftp_client = _ssh_client.open_sftp()
        logger.info(
            "############ Start syncing file @{0} ".format(
                hostname
            ))
        for file_for_sync in batch_conf.get_batch_sync():
            # !!! a path check must take when localpath == remotepath
            # Since when batch sync launched, it will cover node where
            # laserjet locates, otherwise O bytes will sync to other nodes
            local = file_for_sync["localpath"]
            remote = file_for_sync["remotepath"]
            try:
                if (hostname == laserjet_host) and (local == remote):
                    logger.info("Sync task skipped on % s, since copy local \"%s\""
                                " to local \"%s\"" %
                                (laserjet_host, local, remote))
                    continue
                _sftp_client.put(local, remote)
                logger.info(
                    "Done copy from \"{0}\" to  @{2}:\"{1}".format(
                        file_for_sync["localpath"],
                        file_for_sync["remotepath"],
                        hostname
                    )
                )
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                logger.exception("Batch sync encounters error")

        logger.info(
            "######## Done syncing files @{0}".format(hostname))
        _sftp_client.close()
        logger.debug("Close sftp_client")
    else:
        logger.error(
            "while running method <{0}# found input {1} is not an instance of paramiko SSHClient".format(
                inspect.currentframe().f_code.co_name,
                ssh_client)
        )


@action_options.add_method("exec")
def _batch_exec(ssh_client, host_info):
    if isinstance(ssh_client[0], SSHClient):
        _ssh_client = ssh_client[0]
        _ssh_client.connect(**ssh_client[1])
        hostname = host_info["hostname"]
        logger.debug("Start executing commands @%s" % hostname)
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
def _batch_fetch(ssh_client, host_info):
    if isinstance(ssh_client[0], SSHClient):
        hostname = host_info["hostname"]
        _ssh_client = ssh_client[0]
        _ssh_client.connect(*ssh_client[1])
        _sftp_client = _ssh_client.open_sftp()
        # !!! a path check must take when localpath == remotepath
        # Since when batch sync launched, it will cover node where
        # laserjet locates, otherwise O bytes will sync to other nodes
        logger.info(
            "############ Start fetching @{0}".format(
                hostname
            ))
        for file_for_fetch in batch_conf.get_batch_fetch():
            try:
                _sftp_client.get(
                    file_for_fetch["remotepath"],
                    file_for_fetch["localpath"]
                )
                logger.info("Done fetch from \"{0}\"@{1} to \"{2}\"".format(
                    hostname,
                    file_for_fetch["remotepath"],
                    file_for_fetch["localpath"]
                ))
            except:
                _sftp_client.close()
                logger.exception("Batch fetch encounters error")
                raise SystemExit
        logger.info("############ Done fetching @{0}".format(
            hostname
        ))
        _sftp_client.close()
        logger.info("Close sftp client")
    else:
        logger.error(
            "while running method [{0}] found input \"1\" is not an instance of paramiko SSHClient".format(
                inspect.currentframe().f_code.co_name,
                ssh_client))
