#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
    @Author:        yyg
    @Create:        2016MMDD
    @LastUpdate:    2016MMDD HH:MM:SS
    @Version:       0.0
"""

from terminals import action_options
from terminals import *
from options import BatchOption

class Flask(object):
    def __init__(self):
        self.url_map = dict()
    
    def add_url(self, rul):

        def wrap(func):
            self.url_map[url] = func
            return func
        return wrap
        
     @self.add_url("index")
     def index(self):
         print "index"

     def home(self):
         print "home"



if __name__ == "__main__":