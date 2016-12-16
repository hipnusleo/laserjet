#!/usr/bin/env python
# coding=utf-8

import unittest
import json
import os
import sys
from laserjet.src.core.python.z_remote import Remote

_cfg_file = open(os.path.join(os.path.split(os.path.realpath(sys.argv[0]))[0], 'test_conf.json'))
_cfg = json.load(_cfg_file)
_cfg_file.close()


class TestRemote(unittest.TestCase):
    def setUp(self):
    #    f = open(os.path.join(os.path.split(os.path.realpath(sys.argv[0]))[0], 'test_conf.json'))
    #    self.config = json.load(f)
    #    f.close()
        self.config = _cfg
        self.remote = Remote(
            self.config['hostname'],
            self.config['username'],
            self.config['password'],
            self.config['ssh_port']
        )

    def tearDown(self):
        self.remote = None

    def testget(self):
        self.assertTrue(self.remote.get(
            self.config['remote_file'], self.config['local_path']
            )
        )


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestRemote("testget"))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
