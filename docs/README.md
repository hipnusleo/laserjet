***************
LaserJet Beta
***************

顾名思义，激光打印机，为解决大规模集群并行操作需求而开发的简单工具。完全有python实现。目前支撑功能有：
 * 批量执行linux命令
 * 批量同步文件
 * 批量采集文件
 * 批量检查环境并输出至数据库

操作系统要求：
 * Centos/Redhat 6.5 or 6.8

Python版本要求：
 * Python 2.6.6 +

Linux 依赖包括：
 * python
 * python-devel
 * python-setuptools
 * python-setuptools-devel
 * gcc
 * mysql-devel
 * libffi-devel
 * openssl-devel

Python依赖要求：
 * argparse
 * ConcurrenLogHandler
 * paramiko
    * cryptography
    * cffi
        * ordereddict
        * pycparser
    * idna
    * six
    * enum34
    * ipaddress
    * pyasn1
 * Mysql-python (optional)


使用说明
===============

1. 安装
------------------

在安装之前必须要先配置好yum源，linux依赖需通过 ``rpm`` 安装::

    tar zxvf laserjet**.tar.gz & cd laserjet & python setup.py install

安装完成后通过， 下面的方式查看依赖是否已满足::

    python Console.py -h

2. 使用
------------------

在使用之前需要完成一些最基本的参数配置,均为必填::

    ~conf/laserjet_conf.ini

    [AccountInfo]
    #远程主机的用户名密码
    username = root
    password = qwe123

    [LaserjetHost]
    #Laserjet所在节点的主机名或者IP地址，这取决于 conf/hosts_batch.conf 中配置的是IP还是主机名，必须统一
    host = host3

    [DataBase]
    # sqlite/mysql
    # 选择批量检查结果汇总，如果选择mysql需要在安装时选择 ` python setup.py install + mysql `
    # 来安装mysql python驱动，也可以手动安装
    # ` cd ~resource/pypi/MySQL-python-1.2.5 & python setup.py install `
    db_type = sqlite
