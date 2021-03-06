#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
    @Create:        2016MMDD
    @LastUpdate:    2016MMDD HH:MM:SS
    @Version:       0.0
"""
from os.path import abspath, sep, join, exists
from os import mkdir, statvfs
from sys import argv, stdout
from platform import release, linux_distribution
from subprocess import Popen, PIPE
from json import dump, dumps
from collections import OrderedDict
from platform import node
from time import localtime, strftime
from re import compile

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
        self.__report = None
        self.__hostname = hostname

    @property
    def report(self):
        return self.__report

    @property
    def hostname(self):
        return self.__hostname

    @hostname.setter
    def hostname(self, hostname):
        self.__hostname = hostname

    def setup(self):
        self.__report = {
            "id": self.hostname,
            "linux_info": OrderedDict(),
            "netwk_info": OrderedDict(),
            "disk_info": OrderedDict(),
            "cpu_info": OrderedDict(),
            "memory_info": OrderedDict(),
            "software_info": OrderedDict()
        }

    def _check_kernel(self):
        """
        :return
            self.__report["linux_info"]["kernel"] = "2.6.18-194.3.1.el5"
        """
        self.__report["linux_info"]["kernel"] = release()

    def _check_os(self):
        """
        :return
            self.__report["linux_info"]["os"] = "Centos-6.5"
        """
        self.__report["linux_info"]["os"] = "-".join(linux_distribution())

    def _check_memory(self):
        """
        :return
            self.__report["memory_info"]["memory"] = "128G"
            self.__report["memory_info"]["swap_enable"] = "off"
        """
        with open("/proc/meminfo") as meminfo:
            for line in meminfo:
                if ToolBox.isnotcomment(line) and "MemTotal" in line:
                    self.__report["memory_info"]["memory"] = ToolBox.convert(
                        int(line.split(":")[1].strip().split()[0]) * 1024
                    )
                elif ToolBox.isnotcomment(line) and "SwapCached" in line:
                    if int(line.split(":")[1].strip().split()[0]) > 0:
                        self.__report["memory_info"]["swap_enable"] = "on"
                    else:
                        self.__report["memory_info"]["swap_enable"] = "off"
            pass

    def _check_cpu(self):
        """
        : return
            self.__report["cpu_info"]["Processor"] = 32  # logic processors
            self.__report["cpu_info"]["cores"] = 16  # physical cores
            self.__report["cpu_info"]["siblings"] = 16  # siblings
            self.__report["cpu_info"]["HyperThreadingEnable"] = "on"
        """

        self.__report["cpu_info"]["processors"] = 0
        self.__report["cpu_info"]["cores"] = 0
        self.__report["cpu_info"]["siblings"] = 0
        self.__report["cpu_info"]["hyperthreading_enable"] = None

        with open("/proc/cpuinfo") as cpu_info:
            for line in cpu_info:
                if ToolBox.isnotcomment(line):
                    if "processor" in line:
                        self.__report["cpu_info"]["processors"] += 1
                    if "cpu cores" in line:
                        self.__report["cpu_info"]["cores"] = line.split(":")[1].strip()
                    if "siblings" in line:
                        self.__report["cpu_info"]["siblings"] = line.split(":")[1].strip()
        self.__report["cpu_info"]["processors"] = str(
            self.__report["cpu_info"]["processors"])
        if self.__report["cpu_info"]["siblings"] == self.__report["cpu_info"]["cores"]:
            self.__report["cpu_info"]["hyperthreading_enable"] = "on"
        else:
            self.__report["cpu_info"]["hyperthreading_enable"] = "off"

    def _check_disk(self):
        """
        : () = >
            self.__report["disk_1"] = ("/data1","20%", "100G")
            self.__report["mt_num"] = 10
        """
        _cmd = "df -h"
        _index = 1
        _disk = Popen(args=_cmd, shell=True, stdout=PIPE, stderr=PIPE)
        _stdout = _disk.stdout.readlines()
        _stderr = _disk.stderr.readlines()
        for line in _stdout:
            if ToolBox.isnotcomment(line) and "/dev/" in line:
                line = line.split()
                self.__report["disk_info"]["disk_%d" % _index] = (
                    "%s=%s-%s(%s)=%s" % (line[5], line[1], line[2], line[4], line[3])
                )
                _index += 1
        self.__report["disk_info"]["disk_num"] = _index - 1

    def _check_io(self):
        """
        : return
            self.__report["disk_1_io"] = "200MB/s"
        """
        pass
        # for each disk mounted, test its I/O

    def _check_ip(self):
        """
        : return
            self.__report["netwk_*"] =
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
                    if "/" in col and "127" not in col:
                        self.__report["netwk_info"]["netwk_ip_%d" % _index] = col.split("/")[0]
                        _index += 1

    def _check_connectivity(self):
        """
        : return
            self.__report["netwk_info"]["FailureConnectivity"] = "110.222.222.22,
             111.22.223.22"
        """
        pass

    def _check_bandwidth(self):
        """
        : return
            self._report["netwk_info"]["netwk_ip_1_bandwidth"]
        """
        pass

    def _check_umask(self):
        _cmd = "su - root -c 'umask'"
        _umask = Popen(args=_cmd, stdout=PIPE, stderr=PIPE, shell=True)
        _stdout = _umask.stdout.readlines()
        _stderr = _umask.stderr.readlines()
        self.__report["linux_info"]["umask"] = _stdout[0].strip()

    def _check_hostname(self):
        """
        : return
            self.__report["hostname"] = "hadoop001"
        """
        self.__report["linux_info"]["hostname"] = node()

    def _check_iptables(self):
        """
        Turn off iptable before check
        : return
            self.__report["IptableStatus"] = "off"
        """
        _cmd_turnoff = ["service iptables stop", "chkconfig iptables off"]
        _result = Popen(_cmd_turnoff, shell=True, stdout=PIPE, stderr=PIPE)
        print("run 'service iptables stop'")
        print("run 'chkconfig iptables off'")
        _cmd = "service iptables status"
        _iptables_status = Popen(_cmd, shell=True, stdout=PIPE)
        for line in _iptables_status.stdout.readlines():
            if "Firewall is not running" in line:
                self.__report["linux_info"]["iptable_status"] = "off"
            else:
                self.__report["linux_info"]["iptable_status"] = "on"

    def _check_selinux(self):
        """
        : return
            self.__report["SelinuxStatus"] = "disabled"
        """
        _cmd_selinux = "getenforce"
        _result = Popen(_cmd_selinux, shell=True, stdout=PIPE)
        self.__report["linux_info"]["selinux_status"] = _result.stdout.readlines()[0].strip()

    def _check_desktop(self):
        """
        : return
            self.__report["DesktopStatus"] = "off"
        """
        with open("/etc/inittab") as init:
            if (ToolBox.isnotcomment(line) and "3" in line for line in init):
                self.__report["linux_info"]["desktop_status"] = "off"
            else:
                self.__report["linux-info"]["desktop_status"] = "on"

    def _check_openssh(self):
        """
        : return
            self.__report[
                "openssh"] = "openssh-clients-5.3p1-118.1.el6_8.x86_64"
            openssh-clients-5.3p1-118.1.el6_8.x86_64
            openssh-server-5.3p1-118.1.el6_8.x86_64
            openssh-5.3p1-118.1.el6_8.x86_64
        """
        cmd = "rpm -qa|grep openssh"
        pattern = compile(r"openssh-\d.*")
        _result = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        for line in _result.stdout.readlines():
            if pattern.match(line):
                self.__report["software_info"]["openssh"] = line.strip("\n")

    def _check_openssl(self):
        cmd = "rpm -qa|grep openssl"
        pattern = compile(r"openssl-\d.*")
        _result = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        for line in _result.stdout.readlines():
            if pattern.match(line):
                self.__report["software_info"]["openssl"] = line.strip("\n")

    def _check_jdk(self):
        """
        :return
            self.__report["jdk"] = "java version "1.7.0_67"
            java version "1.7.0_67"
            Java(TM) SE Runtime Environment (build 1.7.0_67-b01)
            Java HotSpot(TM) 64-Bit Server VM (build 24.65-b04, mixed mode)
        """
        _jdk = "java -version"
        _result = Popen(_jdk, shell=True, stderr=PIPE, stdout=PIPE)
        self.__report["software_info"]["jdk"] = "None"
        for line in _result.stdout.readlines():
            if "java version" in line:
                self.__report["software_info"]["jdk"] = line.split()[2].strip("\"")

    def _check_clock(self):
        """
        : return
            self.__report["Time"] = "2016/12/5 20:19:22"
        """
        self.__report["linux_info"]["time"] = strftime("%Z-%Y-%m-%d %H:%M:%S", localtime())

    def _check_nofile(self):
        """
        : return
            self.__report["openfile"] = 65536
        """
        cmd = "ulimit -n"
        _result = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        self.__report["linux_info"]["nofile"] = _result.stdout.readlines()[0].strip("\n")

    def _check_nproc(self):
        """
        :return
            self.__report["linux_info"]["nproc"] = 1024
        """
        cmd = "ulimit -u"
        _result = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        self.__report["linux_info"]["nproc"] = _result.stdout.readlines()[0].strip("\n")

    def _check_hugetable(self):
        """
        : return
            self.__report["linux_info"]["hugetable"] = "off"
        """
        pass

    def _collect(self):
        self.setup()
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
        self._check_desktop()
        self._check_openssh()
        self._check_openssl()
        self._check_jdk()
        self._check_clock()
        self._check_nofile()
        self._check_nproc()
        # self._check_hugetable()

    def run(self, path):
        self._collect()
        path = abspath(path)
        if exists(path) is False:
            mkdir(path)
        _report_path = join(path, (self.__hostname + ".json"))
        with open(_report_path, "w") as _report_file:
            dump(self.__report, _report_file, encoding='utf-8')
            print(dumps(self.__report, indent=1))

if __name__ == "__main__":
    inspector=Inspector(argv[1])
    inspector.run(argv[2])
