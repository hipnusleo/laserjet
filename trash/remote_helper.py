#!/usr/bin/env python
#coding:utf-8
import optparse
import traceback

from concurrent.futures import ThreadPoolExecutor

import params
import z_remote


class SRemote(object):
    def __init__(self, host, action_name):
        self.host = host.strip()
        self.usr = params.host_username
        self.pwd = params.get_password(self.host)
        self.action_name = action_name

    def do(self):
        if self.host:
            params.LOG.info('start %s on host: %s' % (self.action_name, self.host))
            try:
                remote = z_remote.Remote(self.host, self.usr, self.pwd)
                result = self.action(remote)
                params.LOG.info('end %s on host: %s' % (self.action_name, self.host))
                remote.close()
                return result
            except:
                params.LOG.error(
                    'failed to %s to host: %s. %s' % (self.action_name, self.host, str(traceback.format_exc())))
                # remote.close()
                return False

    def action(self, remote):
        raise 'SRemote.action'


class MRemote(object):
    def __init__(self, action_name):
        self.action_name = action_name
        self.options = None
        self.prompt = None

    def getSRemote(self, host):
        return SRemote(host, self.action_name)

    def customOptions(self, parser):
        """
        You can overwrite this function to custom options.

        :param parser: parser is already assigned(parser = parse.OptionParser())
        You can use parser.add_option to add new options
        """
        pass

    def action(self):
        parser = optparse.OptionParser(usage="")
        parser.add_option("-f",
                          "--hostname-file",
                          dest="file",
                          default="conf/cluster-hosts.conf",
                          help="Configuration file that contains hostname list. Default is conf/cluster-hosts.conf. "
                               "If --hostname-list assigned, ignore this option"
        )
        parser.add_option("-s",
                          "--hostname-list",
                          dest="hosts",
                          default="",
                          help="hostnames, separated by ','"
        )
        self.customOptions(parser)
        (self.options, args) = parser.parse_args()
        if self.options.hosts:
            hosts = self.options.hosts.split(',')
        else:
            hosts_conf_file = self.options.file
            hosts,passwds = params.getHosts(hosts_conf_file)
        params.LOG.info('remote hosts: \n%s\n' % str(hosts))
        if self.prompt:
            print self.prompt
            print
        ch = raw_input('Are you sure to %s on above hosts?(press "y" for yes:)' % self.action_name)
        if ch is not 'y':
            params.LOG.info('quit %s for pressed key is "%s"' % (self.action_name, ch))
            return

        threads = {}
        pool = ThreadPoolExecutor(len(hosts))
        for host in hosts:
            action = self.getSRemote(host)
            f = pool.submit(action.do)
            threads[host] = f

        successed = 0
        failed = 0
        failedHost = []
        for host in hosts:
            if threads[host].result():
                successed += 1
            else:
                failed += 1
                failedHost.append(host)
        if len(failedHost) > 0:
            msg = "Summary: %s done, successed(%s), failed(%s: %s)" \
                  % (self.action_name, str(successed), str(failed), str(failedHost))
        else:
            msg = "Summary: %s done, successed(%s), failed(%s)" \
                  % (self.action_name, str(successed), str(failed))
        params.LOG.info(msg)
        pool.shutdown()
