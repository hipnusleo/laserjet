#!/usr/bin/env python
# coding=utf-8

import os
from remote_helper import SRemote, MRemote
from params import scan_script_src, scan_script_dst, LASERJET_HOST, utils_dst_dir, scan_result_bucket_dir, outcome_pofix

_action_name = "scan"


class RemoteScan(SRemote):
    def __init__(self, host, options):
        self.options = options
        SRemote.__init__(self, host, _action_name)

    def copy_script_to_remote(self, remote):
        result = False
        if self.options.scan_script:
            src, dst = self.options.scan_script.split(':').strip()
            result = result or remote.put(src, dst)
        else:
            result = result or remote.put(scan_script_src, scan_script_dst)
        return result

    def execute_script(self, remote):
        result = False
        exec_script = 'python {} {}'.format(scan_script_dst, self.host)
        result = result or remote.exec_commands(exec_script)
        return result

    def gather_remote_result(self, remote):
        result = False
        local_file = os.path.join(scan_result_bucket_dir, self.host + '.json')
        remote_file = os.path.join(utils_dst_dir, self.host + '.json')
        result = result or remote.get(remote_file, local_file)
        return result

    def action(self, remote):
        result = self.copy_script_to_remote(remote)
        if result is False:
            return result
        else:
            result = self.execute_script(remote)
            if result is True:
                result = self.gather_remote_result(remote)
            else:
                return result
        return result


class MRemoteScan(MRemote):
    def __init__(self):
        MRemote.__init__(self, _action_name)

    def customOptions(self, parser):
        parser.add_option("-scan", dest="scan_script", default="",
                          help=" src & dest location for <sycheck.py>, separates by ':' "
                               " Example /abs/path/to/src.py:/abs/path/to/dst.py")

    def getSRemote(self, host):
        return RemoteScan(host, self.options)


if __name__ == "__main__":
    MRemoteScan().action()
