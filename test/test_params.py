#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
    @Author:        yyg
    @Create:        2016MMDD
    @LastUpdate:    2016MMDD HH:MM:SS
    @Version:       0.0
    @Description    
        #
"""

import unittest
from sys import path
import config
path.append(config.SRC_CODE_DIR)
from lib.core.params import *


class TestClusterBatchConf(unittest.TestCase):
    def setUp(self):
        self.clusterbatchconf = ClusterBatchConfBase()

    def tearDown(self):
        self.clusterbatchconf = None

    def test_getclusterhosts(self):
        test_host_list = [
            ['10.221.58.22', 'hipnus', 'Bx_9sx&2'],
            ['hadoopmaster', '', 'zhangsanfeng']
        ]
        self.assertEqual(self.clusterbatchconf.batch_hosts_generator(), test_host_list)

    def test_getbatchcmds(self):
        test_cmd_list = [
            "service iptables stop",
            "yum install sshpass -y",
            "python /tmp/syscheck.py",
            "sshpass -p qwe123 scp -o StrictHostKeyChecking=no /tmp/dir4json/*.json root@10.254.10.36:/tmp/dir4json/"
        ]
        self.assertEqual(self.clusterbatchconf.get_batch_cmds(), test_cmd_list)

    def test_getbatchsync(self):
        test_sync_list = [
            ['/app/hcontrol-workstation/file4sync/syscheck.py', '/tmp/syscheck.py']
        ]
        self.assertEqual(self.clusterbatchconf.get_batch_sync(), test_sync_list)

    def test_getbatchfetch(self):
        test_fetch_list = [
            ['/app/hcontrol-workstation/file4sync/syscheck.py', '/tmp/syscheck.py']
        ]
        self.assertEqual(self.clusterbatchconf.get_batch_fetch(), test_fetch_list)

    def test_ClusterParamsSingletonBase(self):
        a = BatchParamsSingletonBase()
        b = BatchParamsSingletonBase()
        self.assertEqual(id(a), id(b))

    def test_ClusterParams(self):
        a = BatchParams()
        b = BatchParams()
        self.assertEqual(id(a), id(b))


class TestClusterParams(unittest.TestCase):
    def setup(self):
        self.batch_params = BatchParams()

    def tearDown(self):
        self.batch_params = None

    def test_getaccountinfo(self):
        self.batch_params = BatchParams()
        self.assertEqual(self.batch_params.get_account_info(), [])

    def test_getyumrepoaddr(self):
        self.batch_params = BatchParams()
        self.assertEqual(self.batch_params.get_yum_repo_addr(), [])


if __name__ == '__main__':
    unittest.main()
