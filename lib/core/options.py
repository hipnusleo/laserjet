#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
    @Author:        yyg
    @Create:        2016MMDD
    @LastUpdate:    2016MMDD HH:MM:SS
    @Version:       0.0
        #
"""

from argparse import ArgumentParser
from params import SingletonBaseClass, LOGGER_NAME, VERSION
from logging import getLogger


logger = getLogger(LOGGER_NAME)


class BatchOption(SingletonBaseClass):

    def __init__(self):
        """ class BatchOption
        :arg ArgumentParser
        """
        super(BatchOption, self).__init__()
        self._args = ArgumentParser(description=VERSION)
        self._action_options = dict()
        self._args.add_argument(
            "-sync",
            "-s",
            action='store_true',
            help="Sync files.",
        )
        self._args.add_argument(
            "-fetch",
            "-f",
            action="store_true",
            help="Fetch files."
        )
        self._args.add_argument(
            "-exec",
            "-e",
            action="store_true",
            help="Execute commands."
        )
        self._args.add_argument(
            "-inspect",
            "-i",
            action="store_true",
            help="Inspect remote servers."
        )
        self._args.add_argument(
            "-distribute",
            "-d",
            action="store_true",
            help="Distribute files, unsupported in Version 0.0 !!"
        )

    def add_option(self):
        """ add in subclass
            self._args.add_argument()
        """
        pass

    def get_options(self):
        return self._args.parse_args().__dict__

    def get_help(self):
        return self._args.print_help()

    def option_match_generator(self):
        return (action_name for (action_name, value)
                in self._args.parse_args().__dict__.items() if value is True)

    def add_method(self, options_name):
        _options = str(options_name)

        def _register_options(func):
            self._action_options[_options] = func
            return func
        return _register_options

    def get_action_options(self):
        return self._action_options

    def get_action(self, action_name):
        return self._action_options[action_name]

    def get_actions(self):
        tmp = list()
        for action_name in self.option_match_generator():
            logger.debug("action_name = {0}".format(action_name))
            tmp.append(self.get_action(action_name))
        return tmp

    def get_action_name(self):
        tmp = list()
        for action_name in self.option_match_generator():
            tmp.append(action_name)
        return tmp

if __name__ == "__main__":
    test = BatchOption()
    for action_name in test.option_match_generator():
        print action_name
    print test.get_action_options()
