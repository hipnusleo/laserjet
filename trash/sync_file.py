#!/usr/bin/env python
#coding:utf-8

import params
import remote_helper

_action_name = "sync files"


class SyncFile(remote_helper.SRemote):
    def __init__(self, host, options):
        remote_helper.SRemote.__init__(self, host, _action_name)
        self.options = options

    def action(self, remote):
        result = True
        if self.options.paths:
            groups = self.options.paths.split('?')
            for group in groups:
                src, dst = group.split(',')
                result = result and remote.put(src, dst)
        else:
            files_need_sync = self.get_files_need_sync(params.files_need_sync_conf_file)
            for src, dst in files_need_sync.items():
                result = result and remote.put(src, dst)
        return result

    @staticmethod
    def get_files_need_sync(filename):
        files = {}
        for line in open(filename):
            line = line.strip()
            if line:
                if not line.startswith('#'):
                    items = line.split(',')
                    items[0] = items[0].strip()
                    items[1] = items[1].strip()
                    if items[0] and items[1]:
                        files[items[0]] = items[1]
        return files


class MSyncFile(remote_helper.MRemote):
    def __init__(self):
        remote_helper.MRemote.__init__(self, _action_name)

    def customOptions(self, parser):
        parser.add_option("-p",
                          "--paths",
                          dest="paths",
                          default="",
                          help="String of source file path and its destination full path. "
                               "You can assign multiple group. "
                               "Source file path and its destination full path are separated by ','. "
                               "Groups are separated by '?'. "
                               "Example:src1,dst1?src2,dst2?src3,dst3"
        )

    def getSRemote(self, host):
        return SyncFile(host, self.options)


if __name__ == '__main__':
    MSyncFile().action()