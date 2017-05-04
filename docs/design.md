[TOC]

# 基本功能构思

## 自动化安装
 需要考虑：
 1. 是否有必要采用golang重构

## 批量同步
 1. 需要考虑采用协成
## 批量获取
 1. 同上
## 批量执行
 1. 同上
## 批量检查
 1. 同上

# 逻辑架构设计
## 程序入口

 ```
 python Console -y
 ```
## 流程

```flow

st=>start: Console.py
e=>end: End
op1=>operation: Batch or Solo
sub1=>subroutine: My Subroutine
cond=>condition: Yes or No?
io=>inputoutput: catch something...
st->op1->cond
cond(yes)->io->e
cond(no)->sub1(right)->op1

```

# 数据库设计

* basic_info:

| col      | sample value                             |
| -------- | ---------------------------------------- |
| id       | 1                                        |
| hostname | hadoop001                                |
| kernel   | 2.6.32-431.el6.x86_64                    |
| os       | Red Hat Enterprise Linux Server-6.5-Santiago |
| time     | CST-2017-03-02 10:38:03                  |

* network_info

| col        | sample value   |
| ---------- | -------------- |
| id         | 1              |
| hostname   | hadoop001      |
| netwk_ip_1 | 10.221.158.55  |
| netwk_ip_2 | 10.221.157.133 |

* disk_info

| col      | sample value            |
| -------- | ----------------------- |
| id       | 1                       |
| hostname | hadoop001               |
| disk_1   | /=total-used(20%)=avail |
| disk_2   | /data=3.3T-46G(2%)=3.1T |


* cpu_info

| col                   | sample value |
| --------------------- | ------------ |
| id                    | 1            |
| hostname              | hadoop001    |
| core                  | 24           |
| hyperthreading_enable | off          |



* software_info

| col      | sample value |
| -------- | ------------ |
| id       | 1            |
| hostname | hadoop001    |

# json结构设计

```
	{
	"sys_info":{
	    "hostname": "hadoop001",
	    "kernel": "2.6.32-431.el6.x86_64",
	    "mem"："128G",
	    "time": "CST-2017-03-02 10:38:03"
	    "os":"Red Hat Enterprise Linux Server-6.5-Santiago",
	
	},
	"network_info":{
	    "hostname": "hadoop001",
	    "netwk_ip_1":"10.221.158.22",
	    "netwk_ip_1" : "10.221.157.122"
	
	},
	"disk_info":{
	    "hostname": "hadoop001",
	    "disk_1": "/data1=3.3T-46G(2%)=3.1T",
	    "disk_2": "/data2=3.3T-46G(2%)=3.1T"
	},
	"cpu_info": {
	    "hostname": "hadoop001",
	    "core": "24"
	},
	"software_info":{
	    "hostname": "hadoop001",
	    "jdk":"",
	    "openssl":"",
	    "openssh":""
	},
	"requires_info":{
	    "iptable_status": "",
	    "selinux_status": "",
	    ""
		}
	}

```


# Bug

* 当安装包被改名后，python解释器会找不到

```

```