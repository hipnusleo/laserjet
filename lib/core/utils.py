#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
    @Author:        yyg
    @Create:        2016MMDD
    @LastUpdate:    2016MMDD HH: MM: SS
    @Version:       0.0
"""
from time import clock

from paramiko import AutoAddPolicy, SFTPClient, SSHClient, Transport
from os.path import abspath, split, sep
from json import load

"""Summary of module 'utils' here.

    "class": [StopWatch, ],
    "class_decorator": []
    "method": [ssh_conn, sftp_conn],
    "method_decorator": [stopwatch, ]"
"""

__version__ = "0.0"
__all__ = ["StopWatch", "ssh_conn", "sftp_conn",
           "iscomment", "json2dict", "record_log"]
__author__ = "yyg"


class StopWatch(object):

    def __init__(self):
        self._start = clock()
        print "start time = ", self._start
        self._end = None
        self._total_time = None
        self._hour_hand = 0
        self._minute_hand = 0
        self._second_hand = 0

    def _time_format(self):
        if self._total_time > 3600:
            self._hour_hand = self._total_time / 3600
            self._minute_hand = (self._total_time % 3600) / 60
            self._second_hand = (self._total_time % 3600) % 60
        elif self._total_time > 60:
            self._minute_hand = self._total_time / 60
            self._second_hand = self._total_time % 60
        else:
            self._second_hand = self._total_time

    def timer(self):
        self._end = clock()
        self._total_time = self._end - self._start
        self._time_format()
        return "{0[0]}hr,{0[1]}min,{0[2]}sec".format(
            map(int, (self._hour_hand, self._minute_hand, self._second_hand))
        )


# methods
def ssh_conn(host_info):
    _ssh_client = SSHClient()
    _ssh_client.load_system_host_keys()
    _ssh_client.set_missing_host_key_policy(AutoAddPolicy())
    _ssh_client.connect(**host_info)
    return _ssh_client


def sftp_conn(host_info):
    trans = Transport(host_info["hostname"], 22)
    trans.connect(username=host_info["username"],
                  password=host_info["password"])
    return SFTPClient.from_transport(trans)


def iscomment(line):
    # verify if it is a comment line, used in loading conf file
    if line.strip().startswith('#'):
        return True
    elif line.strip() == '':
        return True
    else:
        return False


def json_deserialize(json_content):
    """
    Load content from a **.json file then encode("utf-8") 
    """
    return _json_deserialize(load(json_content, object_hook=_json_deserialize))


def _json_deserialize(data):
    if isinstance(data, unicode):
        return data.encode("utf-8")
    elif isinstance(data, list):
        return (_json_deserialize(element) for element in data)
    elif isinstance(data, dict):
        return dict((_json_deserialize(key), _json_deserialize(value))
                    for key, value in data.iteritems())
    else:
        return data

        # method decorator


def record_log(logger):
    def _record(fn):
        def _wrap():
            _start = StopWatch()
            func_name = fn.__name__
            try:
                fn()
                logger.debug("Method %s accomplished in %s" %
                             (func_name, _start.timer()))
            except:
                logger.exception("Method %s encountered an error" % func_name)
                raise SystemExit
        return _wrap
    return _record


if __name__ == "__main__":
    test()
