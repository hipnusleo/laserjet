#!/usr/bin/env python
#coding:utf-8
import logging
import shlex
import subprocess
import re

LOG = logging.getLogger()


def _exec_command(command, shell, use_pipe):
    command = command.strip()
    if not command:
        return True
    LOG.info('exec: "%s"' % command)
    if shell:
        mycmd = command
    elif type(command) == str:
        mycmd = shlex.split(command)

    if use_pipe:
        p = subprocess.Popen(mycmd,
                             stdout=subprocess.PIPE,
                             stdin=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             shell=shell)
        (stdoutdata, stderrdata) = p.communicate()
        if stdoutdata:
            LOG.info('executing %s, %s' % (command, stdoutdata))
        if stderrdata:
            LOG.error('executing %s, return code(%s), %s'
                      % (command, str(p.returncode), stderrdata))
            return False
        else:
            return True
    else:
        p = subprocess.Popen(mycmd, shell=shell)
        p.communicate()
        return str(p.returncode) is '0'


def _exec_commands(commands, shell, use_pipe):
    LOG.info('batch exec: \n"%s"\n==================' % (commands) )
    if isinstance(commands, basestring):
        commands = re.split(r"\n|;", commands)
    else:  # Array
        commands = commands

    for cmd in commands:
        _exec_command(cmd, shell, use_pipe)


def execute_commands(command, shell=True, use_pipe=False):
    _exec_commands(command, shell, use_pipe)


def execute_command(command, shell=True, use_pipe=False):
    _exec_command(command, shell, use_pipe)