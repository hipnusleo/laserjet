#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    syscheck.py
    ~~~~~~~~~~~~~~

    :Description: Some probe

    :copyright: (c) 2016 by YYG
    :license: Apache, see LICENSE for more details.
gg"""

import platform
import socket
import subprocess
import re
import time
import json
import os
import sys
import copy
import argparse

global HOSTNAME
HOSTNAME = platform.node()
parser = argparse.ArgumentParser()
parser.add_argument('filename', help='give me name of result file')
RESULT_FNAME = parser.parse_args().filename


class Probe(object):
    def __init__(self):

        """ registered funcs """
        self.probe_funcs = dict()
        self.probe_returns = dict()

    def register(self, registration_name):
        def wrap_func(f):
            self.probe_funcs[registration_name] = f
            return f

        return wrap_func

    def get_probe_funcs(self):
        return self.probe_funcs

    def get_probe_func_returns(self):
        for name in self.probe_funcs:
            self.probe_returns[name] = self.probe_funcs[name]()
        print(self.get_probe_func_returns)
        return self.probe_returns

    def dump_probe_returns_2file(self, dump_dir):
        """ dump to <dump_dir/HOSTNAME.json> """
        if not os.path.exists(dump_dir):
            os.mkdir(dump_dir)
        # self.get_probe_func_returns()
        f = open(dump_dir + RESULT_FNAME + '.json', 'w')
        json.dump(self.get_probe_func_returns(), f, encoding='utf-8')
        f.close()


probe = Probe()


class Beamer(object):
    """
    @params:

    @method: 

    
    """

    def __init__(self):
        self.bad_conn_dict = dict()
        self.os_info_dict = dict()
        self.clock_info_dict = dict()
        self.cpu_info_dict = dict()
        self.disk_info_dict = dict()
        self.fs_info_dict = dict()
        self.network_info_dict = dict()
        self.ram_info_dict = dict()

        self.check_list = (
            self.bad_conn_dict,
            self.os_info_dict,
            self.clock_info_dict,
            self.cpu_info_dict,
            self.disk_info_dict,
            self.fs_info_dict,
            self.network_info_dict,
            self.ram_info_dict,
        )

    def get_merged_info(self):
        return merge_dicts(self.check_list)

    def get_jsonified_merged_info(self):
        # tmp = merge_dicts(self.check_list)
        return json.dumps(merge_dicts(self.check_list), indent=1)
        # return json.dumps(tmp, indent=2)

    def dump_merged_info_to_disk(self, dump_dir):
        if not os.path.exists(dump_dir):
            os.makedirs(dump_dir)
        if RESULT_FNAME is not None:
            path = os.path.join(dump_dir, RESULT_FNAME + '.json')
        else:
            path = os.path.join(dump_dir, HOSTNAME + '.json')
        f = open(path, 'w')
        json.dump(self.get_merged_info(), f, encoding='utf-8')
        f.close()

    def run(self):
        self.render_ram_info()
        self.render_disk_info()
        self.render_network_info()
        self.render_fs_info()
        self.render_os_info()
        self.render_clock_info()
        self.render_bad_conn_info()
        self.render_cpu_info()

    @probe.register('OS')
    def render_os_info(self):
        # self.os_info_dict = dict()
        linux_distribution = platform.linux_distribution()
        linux_distribution = '-'.join(linux_distribution)
        machine_arch = platform.machine()
        self.os_info_dict['dist'] = linux_distribution
        self.os_info_dict['instruct_set'] = machine_arch
        self.os_info_dict['hostname'] = HOSTNAME
        return self.os_info_dict

    @probe.register('NETWORK')
    def render_network_info(self):
        # network_info_dict = dict()
        cmd = 'ifconfig'
        try:
            if_config = subprocess.Popen(
                cmd,
                close_fds=True,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            cmd_oput = if_config.stdout.readlines()
            cmd_error = if_config.stderr.readlines()
        except Exception, e:
            print('Has an except %s' % e)
        pattern_inet = re.compile(r'(^inet\D+?\d+.\d+.\d+.\d+)')
        index = 1
        for line in cmd_oput:
            line = line.strip()
            tmp_find_inet = pattern_inet.findall(line)
            if not tmp_find_inet:
                continue
            key = 'ipv4_' + str(index)
            self.network_info_dict[key] = tmp_find_inet[0]
            index += 1
        self.network_info_dict['hostname_resolved_ip'] = socket.gethostbyname(socket.gethostname())
        self.network_info_dict['hostname'] = HOSTNAME
        return self.network_info_dict

    @probe.register('CPU')
    def render_cpu_info(self):
        f = open('/proc/cpuinfo')
        lines = f.readlines()
        f.close()
        pattern_cpuinfo = re.compile('processor')
        processor_num = 0
        for line in lines:
            if pattern_cpuinfo.search(line):
                processor_num += 1
        self.cpu_info_dict[''.join('processor_num')] = processor_num
        self.cpu_info_dict['hostname'] = HOSTNAME
        return self.cpu_info_dict

    @probe.register('DISK')
    def render_disk_info(self):
        # disk_info_dict = dict()
        f_MTab = open('/etc/fstab')
        lines = f_MTab.readlines()
        f_MTab.close()
        pattern_dev = re.compile('/dev/\wd[a-z]+?\d*')
        cmd = 'df -h'
        try:
            df_h = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            cmd_oput = df_h.stdout.readlines()
            cmd_error = df_h.stderr.readlines()
        except Exception, e:
            print e
            print cmd_error
        mtpoint_list = list()
        for line in cmd_oput:
            if pattern_dev.search(line):
                mtpoint_list.append(line.split()[5])
        index_i = 1
        for mtpoint in mtpoint_list:
            partial_key = 'mt' + str(index_i)
            self.disk_info_dict[partial_key] = mtpoint
            self.disk_info_dict[''.join(['if_', partial_key, '_absent'])] = if_not_found(mtpoint)[mtpoint]
            self.disk_info_dict[partial_key + '_free_cap'] = cal_disksize_fromvfs(mtpoint)['free_cap']
            index_i += 1
        self.disk_info_dict['disk_number'] = len(mtpoint_list)
        self.disk_info_dict['hostname'] = HOSTNAME
        return self.disk_info_dict

    @probe.register('RAM')
    def render_ram_info(self):
        # mem_info_dict = dict()
        f = open('/proc/meminfo')
        line = f.next()
        f.close()
        key = line.split(':')[0].strip()
        value = str(line.split(':')[1].strip().strip('kB').strip())
        self.ram_info_dict['hostname'] = HOSTNAME
        value = int(value)
        value2tb = value / 1024 / 1024 / 1024
        value2gb = value / 1024 / 1024
        if value2tb > 1:
            self.ram_info_dict['mem_total'] = str(value2tb) + 'T'
        else:
            self.ram_info_dict['mem_total'] = str(value2gb) + 'G'
        return self.ram_info_dict

    @probe.register('CLOCK')
    def render_clock_info(self):
        self.clock_info_dict['time'] = time.strftime("%Z-%Y-%m-%d %H:%M:%S", time.localtime())
        self.clock_info_dict['hostname'] = HOSTNAME
        return self.clock_info_dict

    @probe.register('FS')
    def render_fs_info(self):
        umask = os.popen('umask')
        self.fs_info_dict['umask'] = umask.readlines()[0].strip()
        self.fs_info_dict['hostname'] = HOSTNAME
        return self.fs_info_dict

    @probe.register('BAD_CONN')
    def render_bad_conn_info(self):
        f = open('/etc/hosts')
        lines = f.readlines()
        f.close()
        fail_index = 1
        for line in lines:
            if len(line) > 2:
                continue
            elif line.startswith('#'):
                continue
            elif line.startswith('') and line.endswith(''):
                continue
            else:
                ip = line.split()[0].strip()
                hostname = line.split()[1].strip()
                if not try_connect(ip):
                    self.bad_conn_dict['fail host ' + str(fail_index)] = ip
                    fail_index += 1
        return self.bad_conn_dict


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ==============================================================================

def merge_dict(*args):
    if len(args) < 1:
        return args
    else:
        dict1 = copy.deepcopy(args[0])
        dict2 = copy.deepcopy(args[1])
        dict1.update(dict2)
        return dict1


def merge_dicts(args):
    final_dict = dict()
    for each in args:
        if isinstance(each, dict):
            final_dict.update(each)
    return final_dict


def cal_disksize_fromvfs(path):
    try:
        os.path.isdir(path)
        vfs = os.statvfs(path)
        #        vfs_dict = {
        #            'f_bsize': vfs[0],
        #            'f_frsize': vfs[1],
        #            'f_blocks': vfs[2],
        #            'f_bfree': vfs[3],
        #            'f_bavail': vfs[4],
        #            'f_bfiles': vfs[5],
        #            'f_ffree': vfs[6],
        #            'f_ffavail': vfs[7],
        #            'f_flag': vfs[8],
        #            'f_namemax': vfs[9]
        #        }
        total_cap = vfs.f_bsize * vfs.f_blocks
        free_cap = vfs.f_bsize * vfs.f_bfree
        str_total_cap = 'TotalCap of ' + path
        str_free_cap = 'FreeCap of ' + path
        disk_cap = {
            #            str_total_cap: byte_convert(total_cap),
            'total_cap': byte_convert(total_cap),
            #            str_free_cap: byte_convert(free_cap)
            'free_cap': byte_convert(free_cap)
        }
        return disk_cap
    except Exception, e:
        print('Method[%s] encouters {%s}' % (sys._getframe().f_code.co_name, e))


def try_connect(ip):
    cmd = ["ping -c 5 -w 20 %s" % ip]
    all_packets_sent = re.compile('0% packet loss')
    try:
        p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        cmd_oput = p.stdout.readlines()
        cmd_error = p.stderr.readlines()
        connection_is_stable = all_packets_sent.findall(cmd_oput)
        if connection_is_stable:
            return True
        else:
            return False
    except Exception, e:
        print e
        print cmd_error


def byte_convert(value):
    BYTE2KB = 1024
    BYTE2MB = 1048576
    BYTE2GB = 1073741824
    BYTE2TB = 1099511627776L
    BYTE2PB = 1125899906842624L
    try:
        value = int(value)
        if value >= BYTE2PB:
            return str(value / BYTE2PB) + 'PB'
        elif value >= BYTE2TB:
            return str(value / BYTE2TB) + 'TB'
        elif value >= BYTE2GB:
            return str(value / BYTE2GB) + 'GB'
        elif value >= BYTE2MB:
            return str(value / BYTE2MB) + 'MB'
        elif value >= BYTE2KB:
            return str(value / BYTE2KB) + 'KB'
        else:
            return str(value) + 'B'

    except Exception, e:
        print e


def if_not_found(keyword):
    f = open('/etc/fstab')
    content = f.readlines()
    f.close()
    for line in content:
        if keyword in line:
            return {keyword: 'No'}
    return {keyword: 'Yes'}


if __name__ == '__main__':
    beamer = Beamer()
    beamer.run()
    beamer.dump_merged_info_to_disk('/tmp/laserjet/result')
