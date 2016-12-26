#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
    @Create:        2016MMDD
    @LastUpdate:    2016MMDD HH:MM:SS
    @Version:       0.0
"""
from os.path import abspath, sep, join, exists
from os import mkdir
from sys import argv, stdout
from platform import release, linux_distribution
from subprocess import Popen, PIPE
from json import dump, dumps
from collections import OrderedDict
from platform import node

"""Summary of script 'inspect.py'.

        self._check_kernel()
        self._check_cpu()
        self._check_disk()
        self._check_umask()
        self._check_hostname()
        self._check_ip()
        # self._check_connectivity()
"""

__version__ = "0.0"
__all__ = []
__author__ = "yyg"


class ToolBox(object):

    @classmethod
    def _convert2kilobyte(cls, num):
        return (num / 1024)

    @classmethod
    def _convert2megabyte(cls, num):
        return cls._convert2kilobyte(num) / 1024

    @classmethod
    def _convert2gigabyte(cls, num):
        return cls._convert2megabyte(num) / 1024

    @classmethod
    def _convert2terabyte(cls, num):
        return cls._convert2gigabyte(num) / 1024

    @classmethod
    def convert(cls, num):
        if cls._convert2terabyte(num) > 1:
            return str(cls._convert2terabyte(num)) + "T"
        elif cls._convert2gigabyte(num) > 1:
            return str(cls._convert2gigabyte(num)) + "G"
        elif cls._convert2megabyte(num) > 1:
            return str(cls._convert2megabyte(num)) + "MB"
        elif cls._convert2kilobyte(num) > 1:
            return str(cls._convert2kilobyte(num)) + "KB"
        else:
            return str(num) + "B"

    @classmethod
    def isnotcomment(cls, line):
        if not line.strip().startswith("#"):
            return True
        else:
            return False


class Inspector(object):

    def __init__(self, hostname):
        self._report = OrderedDict()
        self._hostname = hostname

    def _check_kernel(self):
        """
        :return
            self._report["KernelVersion"] = "2.6.18-194.3.1.el5"
        """
        self._report["KernelVersion"] = release()

    def _check_os(self):
        """
        :return 
            self._report["OS"] = "Centos-6.5"
        """
        self._report["OS"] = "-".join(linux_distribution())

    def _check_memory(self):
        """
        :return
            self._report["Memory"] = "128G"
            self._report["SwapEnable"] = "off"
        """
        with open("/proc/meminfo") as meminfo:
            for line in meminfo:
                if ToolBox.isnotcomment(line) and "MemTotal" in line:
                    self._report["Memory"] = ToolBox.convert(
                        int(line.split(":")[1].strip().split()[0]) * 1024
                    )
                elif ToolBox.isnotcomment(line) and "SwapCached" in line:
                    if int(line.split(":")[1].strip().split()[0]) > 0:
                        self._report["SwapEnable"] = "on"
                    else:
                        self._report["SwapEnable"] = "off"
            pass

    def _check_cpu(self):
        """
        : return
            self._report["Processor"] = 32  # logic processors
            self._report["Cores"] = 16  # physical cores
            self._report["Siblings"] = 16  # siblings
            self._report["HyperThreadingEnable"] = "on"
        """
        self._report["Processor"] = 0
        self._report["Cores"] = 0
        self._report["Siblings"] = 0
        self._report["HyperThreadingEnable"] = None

        with open("/proc/cpuinfo") as cpu_info:
            for line in cpu_info:
                if ToolBox.isnotcomment(line):
                    if "processor" in line:
                        self._report["Processor"] += 1
                    if "cpu cores" in line:
                        self._report["Cores"] = line.split(":")[1].strip()
                    if "siblings" in line:
                        self._report["Siblings"] = line.split(":")[1].strip()
        if self._report["Siblings"] == self._report["Cores"]:
            self._report["HyperThreadingEnable"] = "on"
        else:
            self._report["HyperThreadingEnable"] = "off"

    def _check_disk(self):
        """
        : return
            self._report["MountPoint_1"] = "/data1"
        """
        _cmd = "df -h"
        _index = 1
        _disk = Popen(args=_cmd, shell=True, stdout=PIPE, stderr=PIPE)
        _stdout = _disk.stdout.readlines()
        _stderr = _disk.stderr.readlines()
        for line in _stdout:
            if ToolBox.isnotcomment(line) and "/dev/" in line:
                self._report["MountPoint_%d" % _index] = line.split()[5]
                _index += 1

    def _check_io(self):
        """
        : return
            self._report["MountPoint_1_IO"] = "200MB/s"
        """
        pass
        # for each disk mount, test its I/O

    def _check_ip(self):
        """
        : return
            self._report[""]
        """
        _cmd = "ip a"
        _index = 1
        _ifconfig = Popen(args=_cmd, shell=True, stdout=PIPE, stderr=PIPE)
        _stdout = _ifconfig.stdout.readlines()
        _stderr = _ifconfig.stderr.readlines()
        for line in _stdout:
            if "inet" in line and "inet6" not in line:
                line = line.split()
                for col in line:
                    if "/" in col:
                        self._report["IP_%d" % _index] = col.split("/")[0]

    def _check_connectivity(self):
        """
        : return
            self._report["FailureConnectivity"] = "110.222.222.22,
             111.22.223.22"
        """
        with open("/etc/hosts") as host_list:
            pass

    def _check_bandwidth(self):
        """
        : return
            self._reprot[""]
        """
        pass

    def _check_umask(self):
        _cmd = "su - root -c 'umask'"
        _umask = Popen(args=_cmd, stdout=PIPE, stderr=PIPE, shell=True)
        _stdout = _umask.stdout.readlines()
        _stderr = _umask.stderr.readlines()
        self._report["Umask"] = _stdout[0].strip()

    def _check_hostname(self):
        """
        : return
            self._report["Hostname"] = "hadoop001"
        """
        self._report["Hostname"] = node()

    def _check_iptables(self):
        """
        Turn off iptable before check
        : return
            self._report["IptableStatus"] = "off"
        """
        _cmd_turnoff = ["service iptables stop", "chkconfig iptables off"]
        _result = Popen(_cmd_turnoff, shell=True, stdout=PIPE, stderr=PIPE)
        print("run 'service iptables stop'")
        print("run 'chkconfig iptables off'")
        _cmd = "service iptables status"
        _iptables_status = Popen(_cmd, shell=True, stdout=PIPE)
        for line in _iptables_status.stdout.readlines():
            if "running" not in line:
                self._report["IptableStatus"] = "off"
            else:
                self._report["IptableStatus"] = "on"

    def _check_selinux(self):
        """
        : return 
            self._report["SelinuxStatus"] = "disabled"
        """
        _cmd_selinux = "sestatus"
        _result = Popen(_cmd_selinux, shell=True, stdout=PIPE)
        for line in _result.stdout.readlines():
            self._report["SelinuxStatus"] = line.split(":")[1].strip()

    def _collect(self):
        self._check_kernel()
        self._check_os()
        self._check_memory()
        self._check_cpu()
        self._check_disk()
        # self._check_io()
        self._check_ip()
        # self._check_connectivity()
        # self._check_bandwidth()
        self._check_umask()
        self._check_hostname()
        self._check_iptables()
        self._check_selinux()

    def run(self, path):
        self._collect()
        path = abspath(path)
        if exists(path) is False:
            mkdir(path)
        _report_path = join(path, (self._hostname + ".json"))
        _report_file = open(_report_path, "w")
        dump(self._report, _report_file, encoding='utf-8')
        print dumps(self._report, indent=1)
        _report_file.close()

if __name__ == "__main__":
    inspector = Inspector(argv[1])
    inspector.run(argv[2])