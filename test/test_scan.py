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

import json
import unittest
from os.path import join, dirname, pardir, split, realpath, abspath
import sys
sys.path.insert(0, abspath(join(dirname("__file__"), 'src/core/python')))

print(sys.path)
from scan import RemoteScan
from z_remote import Remote

_cfg_file = open(join(split(realpath(sys.argv[0]))[0], 'test_conf.json'))
_cfg = json.load(_cfg_file)
_cfg_file.close()


class TestClassRemoteScan(unittest.TestCase):
    def setUp(self):
        self.config = _cfg
        self.remote_scan = RemoteScan(self.config['hostname'], self.config['options'])
        self.remote = Remote(self.config['hostname'], self.config['username'], self.config['password'])

    def tearDown(self):
        pass

    def test_copy_script_to_remote(self):
        self.assertEqual(self.remote_scan.copy_script_to_remote(self.remote), True)

    def test_execute_script(self):
        self.assertEqual(self.remote_scan.execute_script(self.remote), True)

    def test_gather_remote_result(self):
        self.assertEqual(self.remote_scan.gather_remote_result(self.remote), True)

#    def test_action(self):
#        self.assertEqual(self.remote_scan.action(self.remote), True)

if __name__ == '__main__':
    unittest.main()


