## Laserjet-Beta-0.0
-----
Laserjet is a radically simple batch automation tool. It handles file-syncing, file-fetching, shell-command-parallel-execution, multi-server inspection.

Read the documentation below.

### Design Principals
1. Have a simple setup process and minimal using curve;
2. Manage Machine very quickly and in parallel;

### Install Requests
- pypi
    - argparse
    - ConcurrenLogHandler
    - paramiko
        - cryptography
            - cffi
                - pycparser
            - idna
            - six
            - enum34
            - ipaddress
        - pyasn1
    - Mysql-python (optional)

- rpm
    - python
    - python-devel
    - python-setuptools
    - python-setuptools-devel
    - gcc
    - mysql-devel
    - libffi-devel
    - openssl-devel


### Quick Start
1. setup
    - `python setup.py install`
    - If you want to use mysql for inspection use `python setup.py install + mysql`
    - Once setup process accomplished use `python Console.py -h` to see if all modules have been installed 
    - conf/laserjet_conf.ini
        1. Edit "username" and "password" in section 'AccountInfo'.
        2. Edit "host" in section 'LaserjetHost', be aware of its format which completely depends on what was putted in 'conf/hosts_batch.conf'. Once you use actual ip address instead of a hostname in 'conf/hosts_batch.conf',making sure you did this to 'host' at the mean time.
        3. Edit "db_type" in section DataBase, choose either sqlite or mysql. In case mysql is used, please complete the information in section 'Mysql'. 
    - conf/hosts_batch.conf
        - Use either hostname or ip address;
        - Sometimes, remote machines have various user&password, in such case, use 'hostname/ip username password' instead;  
    - conf/exec_batch.conf
        - same as workstation
    - conf/sync_batch.conf
        - same as workstation
    - conf/fetch_batch.conf
        - same as workstation 
2. action:
    - Please make sure you are in directory ~/laserjet
    - `python Console.py -h`


---

### Next Version Features:
---
1. none root user (su - );
2. table display;
3. config file render and dispatch(BCH);
4. auto deploy;
5. IO, Network test;

