#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""Summary of script setup.py
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
- rpm
    - python
    - python-devel
    - python-setuptools
    - python-setuptools-devel
    - gcc
    - libffi-devel
    - openssl-devel

"""
from subprocess import Popen, PIPE
from platform import python_version_tuple
from os.path import abspath, join

__version__ = "0.0"
__author__ = "yyg"
__all__ = []

PYTHON_VERSION = python_version_tuple()
PYPI_DIR = "./resource/pypi/"
RPM = [
    #    "python",
    "python-devel",
    "python-setuptools",
    "python-setuptools-devel",
    "gcc",
    "libffi-devel",
    "openssl-devel"
]
EGG = {
    "python2.6": [
        "ConcurrentLogHandler-0.9.1-py2.6.egg",
        "pyasn1-0.1.9-py2.6.egg"
    ],
    "python2.7": [
        "ConcurrentLogHandler-0.9.1-py2.7.egg",
        "pyasn1-0.1.9-py2.7.egg"
    ],
}
TARBALL = [
    "pycparser-2.17",
    "argparse-1.4.0",
    "cffi-1.9.1",
    "ordereddict-1.1",
    "enum34-1.1.6",
    "idna-2.2",
    "ipaddress-1.0.17",
    "six-1.10.0",
    "cryptography-1.7.1",
    "paramiko-2.1.1",
]
# -----------------


def unicode_list_normalize(value):
    if isinstance(value, list):
        tmp = list()
        for element in value:
            if isinstance(element, unicode):
                tmp.append(element.encode("utf-8"))
            else:
                tmp.append(element)
        return ''.join(tmp)
    else:
        return "This is not a list"


class ShellCLI(object):

    def __init__(self, cmd):
        self._result = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        self._stdout = unicode_list_normalize(self._result.stdout.readlines())
        self._stderr = unicode_list_normalize(self._result.stderr.readlines())

# Install rpm ----------------------------------------------------------


# def install_rpm():
#    rpm = " ".join(RPM)
#    cmd = "yum install %s -y" % rpm
#    print "run '%s'" % cmd
#    print "This may take a while, please wait ... ..."
#    cli = ShellCLI(cmd)
#    if cli._stdout:
#        print cli._stdout
#    if cli._stderr:
#        print cli._stderr
#        print "Setup terminated"
#        raise SystemExit


def install_rpm():
    for rpm in RPM:
        cmd = "yum install %s -y" % rpm
        print "run '%s'" % cmd
        print "This may take a while, please wait ... ..."
        cli = ShellCLI(cmd)
        if cli._stdout:
            print cli._stdout
            print "+Done install %s +++++++++++" % rpm
        if cli._stderr:
            print cli._stderr
            print "Failed in installing %s -----------" % rpm
            print "Setup terminated"
            raise SystemExit

# Install egg ----------------------------------------------------------


def install_egg(version):
    if version == 6:
        egg = EGG["python2.6"]
    elif version == 7:
        egg = EGG["python2.7"]
    for egg_pack in egg:
        path = abspath(join(PYPI_DIR, egg_pack))
        cmd = "easy_install %s" % path
        print cmd
        cli = ShellCLI(cmd)
        if cli._stdout:
            print cli._stdout
            print "+Done install %s +++++++++++" % egg_pack
        if cli._stderr:
            print cli._stderr
            print "Failed in installing %s -----------" % egg_pack
            print "Setup terminated"
            raise SystemExit
# Install source -------------------------------------------------------


def install_source():
    for source_pack in TARBALL:
        path = abspath(join(PYPI_DIR, source_pack))
        cmd = "cd %s && python setup.py install" % path
        print cmd
        cli = ShellCLI(cmd)
        if cli._stdout:
            print cli._stdout
            print "+Done install %s +++++++++++" % source_pack
        if cli._stderr:
            print cli._stderr
            print "Failed in installing %s -----------" % source_pack
            print "Setup terminated"
            raise SystemExit

# setup ----------------------------------------------------------------


def setup():
    install_rpm()
    if int(PYTHON_VERSION[0]) == 2 and int(PYTHON_VERSION[1]) == 6:
        install_egg(6)
    elif int(PYTHON_VERSION[0]) == 2 and int(PYTHON_VERSION[1]) == 7:
        install_egg(7)
    else:
        print("incorrect python version")
        print "Setup terminated"
        raise SystemExit
    install_source()
#    if len(argv) == 3 and argv[2].lower() == "+mysql":
#        path = abspath(join(PYPI_DIR, "MySQL-python-1.2.5"))
#        cmd = "cd %s && python setup.py install" % path
#        print cmd
#        cli = ShellCLI(cmd)
#        if cli._stdout:
#            print cli._stdout
#            print "+Done install MySQL-python-1.2.5 +++++++++++"
#        if cli._stderr:
#            print cli._stderr
#            print "Failed in installing MySQL-python-1.2.5 -----------"
#            print "Setup terminated"
#            raise SystemExit
#    print "Done"


if __name__ == "__main__":
    from sys import argv
    if len(argv) < 4 and len(argv) > 1 and argv[1] == "install":
        print "Yum Service is a MUST here, please make sure it is valid"
        yum = raw_input("Yum Service valid? [y/n]: ")
        if yum == "y":
            setup()
        else:
            print "Setup Canceled"
    else:
        print"use 'python setup install'"
