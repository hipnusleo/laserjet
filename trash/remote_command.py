#!/usr/bin/env python
#coding:utf-8

import params
import remote_helper

_action_name = "remote command"


class RemoteCommand(remote_helper.SRemote):
    def __init__(self, host, options):
        remote_helper.SRemote.__init__(self, host, _action_name)
        self.options = options

    def getCommands(self, filename):
        cmds = []
        for line in open(filename):
            line = line.strip()
            if line:
                if not line.startswith('#'):
                    cmds.append(line)
        return cmds

    def action(self, remote):
        if self.options.commands_file:
            filename = self.options.commands_file
        else:
            filename = params.remote_command_conf_file
        cmds = self.getCommands(filename)
        return remote.exec_commands(cmds)


class MRemoteCommand(remote_helper.MRemote):
    def __init__(self):
        remote_helper.MRemote.__init__(self, _action_name)

    def customOptions(self, parser):
        parser.add_option("-c",
                          "--commands-file",
                          dest="commands_file",
                          default="",
                          help="a file that contains commands that need executed on remote hosts. "
                               "Default is conf/remote-command.conf. "
                               "Commands must be separated by ';' or one line one command"
        )

    def getSRemote(self, host):
        return RemoteCommand(host, self.options)

if __name__ == '__main__':
    MRemoteCommand().action()