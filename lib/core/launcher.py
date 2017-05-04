#!/usr/bin/env python
#-*- coding: utf-8 -*-

from terminals import MTerminal
from sys import argv

"""Summary of module 'launcher' here.

This is a entry of entire laserjet program

class Launcher launches 'Batch' task or 'Play' task depends on options.
- Batch options (e.g.:'-exec', '-sync', '-fetch', '-inspect') which accomplish
  tasks on every remote nodes.
- Play options (e.g.: '-deploy') which conditionally execute actions following
   a playbook.
"""

__version__ = "0.1"
__author__ = "yyg"
__all__ = []

# Exceptions


class NoneOptionException(Exception):
    """Exception raised by Launcher._get_option()."""
    pass


class WrongOptionException(Exception):
    """Exception raise by Launcher._get_option()"""
    pass


class Launcher(object):

    def __init__(self):
        self.laserjet_terminal = MTerminal()

    def _get_option(self):
        pass
