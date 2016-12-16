#!/usr/bin/env python
# coding:utf-8
import ConfigParser
import getpass
import logging
import re
import socket
import sys
from os.path import join, pardir, split, realpath, abspath

import z_logging


def get_ambari_server_host(filename):
    for line in open(filename):
        line = line.strip()
        if line:
            if not line.startswith('#'):
                return line


def getHosts(filename):
    hosts = []
    passwds = {}
    for line in open(filename):
        line = line.strip()
        if line:
            if not line.startswith('#'):
                if len(line.split(',')) > 1:
                    t = line.split(',')
                    host = t[0].strip()
                    passwd = t[1].strip()
                    hosts.append(host)
                    passwds[host] = passwd
                else:
                    hosts.append(line)
    return hosts, passwds


def set_server_soft(filename):
    properties = []
    urlp = 'j.*?url=(.*)/'

    for line in open(filename):
        line = line.rstrip()
        if line:
            if re.match(urlp, line):
                line = re.sub('=(.*)/', '=' + _software_url, line)
        properties.append(line + '\n')

    fw = open(filename, 'w')
    fw.writelines(properties)
    fw.close()


# init logger
z_logging.ZLogging().initLogger()
LOG = logging.getLogger()

# configuration's base directory


project_root_dir = abspath(join(split(realpath(sys.argv[0]))[0], pardir, pardir, pardir))
print("project_root_dir = {0}".format(project_root_dir))
conf_root_dir = join(project_root_dir, 'conf')
resource_root_dir = join(project_root_dir, 'src/core/resources')

# get configuration parameters
cfg = ConfigParser.ConfigParser()
cfgfile = '{0:s}/hcontrol-deploy.ini'.format(conf_root_dir)
cfgfile = abspath(realpath(cfgfile))
print ("cfgfile = {0}".format(cfgfile))
LOG.debug('hcontrol-deploy configuration file: %s' % cfgfile)
cfg.read(cfgfile)

section = 'hcontrol_deploy'
host_username = 'root'
_host_password = None
_software_url = None

if cfg.has_option(section, 'host_password'):
    _host_password = cfg.get(section, 'host_password')

if cfg.has_option(section, 'software_url'):
    _software_url = cfg.get(section, 'software_url')


def get_password(host):
    global _host_password
    hosts, passwds = getHosts('conf/cluster-hosts.conf')
    if host in passwds:
        return passwds[host]
    if _host_password is not None:
        return _host_password
    else:
        _host_password = getpass.getpass("Enter the root password: ")
        return _host_password


def get_softurl():
    global _software_url
    if _softwar_url is not None:
        return _software_url
    else:
        _software_url = getpass.getpass("Enter the software url: ")
        return _software_url


ambari_repo_address = cfg.get(section, 'ambari_repo_address')
print ambari_repo_address
cluster_hosts_conf_file = 'cluster-hosts.conf'
files_need_sync_conf_file = 'files-need-sync.conf'
remote_command_conf_file = 'remote-command.conf'

# update configuration file path
cluster_hosts_conf_file = join(conf_root_dir, cluster_hosts_conf_file)
files_need_sync_conf_file = join(conf_root_dir, files_need_sync_conf_file)
remote_command_conf_file = join(conf_root_dir, remote_command_conf_file)

# retrieve data from configuration file
ambari_server_host = get_ambari_server_host(cluster_hosts_conf_file)

# update resource file path
#
# local resource of ambari agent configuation file
ambari_agent_config_file = join(resource_root_dir, 'ambari-agent.ini')
# local resource of ambari server configuation file
ambari_server_properties_file = join(resource_root_dir, 'ambari.properties')
set_server_soft(ambari_server_properties_file)

# util scripts Config
# 
utils_src_dir = join(project_root_dir, 'src/utils')
utils_dst_dir = '/tmp/laserjet/script'
scan_result_bucket_dir = '/tmp/laserjet/results'
scan_result_dir = '/tmp/laserjet/result'
scan_script = 'syscheck.py'
outcome_pofix = '*.json'
scan_script_src = join(utils_src_dir, scan_script)
scan_script_dst = join(utils_dst_dir, scan_script)
LASERJET_HOST = socket.gethostbyname(socket.gethostname())
