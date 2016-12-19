#!/usr/bin/env python
# coding:utf-8
import threading
from multiprocessing import Pool
import paramiko
import time
import sys

while True:
    try:
        time.sleep(3)
        comd = raw_input('请输入你要批量分发的命令(输入1传送文件)：')
    except:
        sys.exit()
    else:
        # 哪果输入为exit就退出系统
        if comd == 'exit':
            sys.exit()

        # 如果输入为1就进行交互
        if comd == '1':
            try:
                yuan = raw_input('请输入你源服务器文件文件的路径，如/opt/test.txt：')
                mb = raw_input('请输入你目标服务器存放文件的路径：如/opt/test1.txt：')
            except:
                sys.exit()
        # 日志文件
        succ = '/opt/log.txt'
        err = '/opt/error.txt'

        def run(n):
            # 输入Key的路径
            private_key_path = '/root/.ssh/id_rsa'
            # 获得key
            key = paramiko.RSAKey.from_private_key_file(private_key_path)
            # 获取连接ssh方法
            ssh = paramiko.SSHClient()
            # 允许连接不在know_hosts文件中的主机
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # 把局部变量设为全局变量
            global yuan
            global mb
            # 如果值等于1就传送文件
            if comd == '1':
                # 三台机器的IP地址
                ip = '192.168.200.%s' % n
                t = paramiko.Transport((ip, 22))
                t.connect(username='root', pkey=key)
                sftp = paramiko.SFTPClient.from_transport(t)
                result = sftp.put(yuan, mb)
                return result
                t.close()

            else:
                # 三台机器的IP地址
                ip = '192.168.200.%s' % n
                # 连接相关信息
                ssh.connect(hostname=ip, port=22, username='root', pkey=key)
                # 执行命令
                stdin, stdout, stderr = ssh.exec_command(comd)
                # 获取执行命令的时间
                sj = time.strftime('%Y-%m-%d %H:%M:%S')
                # 打开正确和错误日志文件
                f = open(succ, 'ab')
                e = open(err, 'ab')
                # 读进正确和错误信息
                result_out = stdout.read()
                result_err = stderr.read()
                # 把正确和错误信息写到日志文件
                if result_err:
                    e.write(sj + '\n')
                    e.write(result_err + '\n')
                    e.close
                else:
                    f.write(sj + '\n')
                    f.write(result_out + '\n')
                    f.close
                # 输出正确和错误信息
                return result_out
                return result_err
                # 关闭ssh连接
                ssh.close()
        # 最大同时执行的进程数为3
        pool = Pool(processes=3)
        # 创建一个空列表
        res_list = []
        # 创建三个进程
        if __name__ == '__main__':
            for i in range(10, 13):
                res = pool.apply_async(run, [i, ])
                # 往空列表添加值
                res_list.append(res)
            # 启动多进程
            for r in res_list:
                print r.get()
