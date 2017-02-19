## LaserJet Beta

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
 * Mysql-python (弃用)


### 使用说明

---

#### 1. 安装


在安装之前必须要先配置好yum源，linux依赖需通过 ``rpm`` 安装::

```
tar zxvf laserjet**.tar.gz & cd laserjet & python setup.py install
```
    

安装完成后通过， 下面的方式查看依赖是否已满足::

```
python Console.py -h
```

#### 2. 使用


在使用之前需要完成一些最基本的参数配置,均为必填::

```
 ~conf/laserjet_conf.ini

 [AccountInfo]
 #远程主机的用户名密码
 username = root
 password = qwe123

 [LaserjetHost]
 #Laserjet所在节点的主机名或者IP地址，这取决于 conf/hosts_batch.conf 中配置的是IP还是主机名，必须统一
 host = host3
```

#### 3. 其他

~ conf/hosts_batch.conf ::

```
直接填写 主机名 或者 IP
或者 主机名 用户 密码，
例如：
host001
or
10.221.158.55
or
host001 hdfs Qwer!234
```

~conf/exec_batch.conf ::

```
    每行一条非交互式linux命令，例如
    service httpd start
    yum install vim -y
```

~conf/sync_batch.conf ::
    
```
/tmp/src.txt , /tmp/dest.txt    
源文件绝对路径， 远程目标文件绝对路径
用 "," 隔开，需注意此处的cp和linux下的cp有不同，必须为一个完整真正的文件名，不允许包含"*"或者
其他任何正则符号，正确的格式如下：
/tmp/text.txt, /etc/text.txt
远程目标可以与源文件不一样，例如：
/tmp/text.txt, /etc/centent.txt
```

~conf/fetch_batch.conf ::

```
与sync同理，必须填写绝对路径
/tmp/src.txt, /tmp/dest.txt
例如：
/etc/hosts, /tmp/hosts
最终文件会放在laserjet节点/tmp/目录下，以dest.txt开头，主机名结尾
/tmp/hosts.10.221.158.117
```
    

#### 4. 命令解析：

```
python Console.py [-option]
-h  -help           查看所有命令
-e  -exec           批量执行
-s  -sync           同步
-i  -inspect        环境检查
-f  -fetch          收集远程文件
注意： option 可以放在一起执行，例如：`python Console.py -es` 但执行顺序是无序的。
```

#### 5. 环境检查功能
```
-inspect:
成功执行完 python Console.py -i，
通过执行sqlite3 /tmp/laserjet/db/laserjet.db 进入sqlite3 shell
select * from disk_info;        //查看磁信息
select * from basic_info;       //查看基本环境信息
```

#### 6. 字段清单：
* disk_info
    * disk_num => 磁盘数量
    * disk_1 => /data1=13%+100G: 磁盘挂载/data1 已使用13%，还剩余100G
    * disk_2 => 同上
* basic_info
    * "cores": "1",
    * "desktop_status": "off",
    * "hostname": "bch132001",
    * "hyperthreading_enable": "on",
    * "iptable_status": "off",
    * "jdk": "None",
    * "kernel_version": "2.6.32-642.el6.x86_64",
    * "memory": "7G",
    * "netwk_1": "10.139.5.118",
    * "nproc": "31388",
    * "openfile": "1024",
    * "openssh": "openssh-5.3p1-117.el6.x86_64",
    * "os": "Red Hat Enterprise Linux Server-6.8-Santiago",
    * "processors": "4",
    * "selinux_status": "Disabled",
    * "siblings": "1",
    * "swap_enable": "off",
    * "time": "CST-2017-02-19 17:09:55",
    * "umask": "0022"
