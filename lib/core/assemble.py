#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    @Author:        yyg
    @Create:        2017MMDD
    @LastUpdate:    2017-02-14 HH:MM:SS
    @Version:       0.0.0-Beta
"""

# Import
import sqlite3
from logging import getLogger
from os import walk, mkdir
from os.path import join, isdir
from shutil import rmtree

from params import (LOGGER_NAME, INSPECT_COLLECT_DIR, SQLITE_DB_DIR)
from utils import json_deserialize

# Basic info
__version__ = "0.0.0-Beta"
__all__ = []
__author__ = "yyg"

# Add logger

logger = getLogger(LOGGER_NAME)

# Exceptions


# main code

class Assembler(object):
    """
        Generate formated inspect outcome
        - step1: reverse-serialize
        - step2: re-range data
        - step3: generate tables
            - collect table cols
                - table(disk_info) = > disk_***
                - table(network_info) = > netwk_**

        tables = [u"basic_info", u"disk_info", u"netwk_info"]
        table struct:
         - disk
         id|hostname/ip|disk_num|disk_1         | disk_2        |
         1 |10.10.10.10|2       |/data1=100G+10%|/data2=200G+20%|
    """

    def __init__(self):
        self.db = "laserjet.db"
        self.conn = None
        self.data = list()
        self.tables = {
            # "xxx" : [[cols],sql_create_table, [data], [sql_insert_rows]]
            "basic_info": [[], None, [], []],
            "disk_info": [[], None, [], []],
            "netwk_info": [[], None, [], []]
        }

    # steps

    def start(self):
        self.create_db()
        self.deserialize()
        self.create_tables()
        self.insert_rows()

    def create_db(self):
        if not isdir(SQLITE_DB_DIR):
            mkdir(SQLITE_DB_DIR)
        else:
            rmtree(SQLITE_DB_DIR)  # clean up existing laserjet.db
            mkdir(SQLITE_DB_DIR)
        self.conn = sqlite3.connect(join(SQLITE_DB_DIR, self.db))

    def deserialize(self):
        total_cols = set()
        logger.info("Start deserialize")
        for file in Assembler.__jfiles():
            with open(file) as j_content:
                j_content_dict = json_deserialize(j_content)
                self.data.append(j_content_dict)
                total_cols = total_cols | set(j_content_dict.keys())
        tmp = self.__filter_cols(total_cols, "disk_")
        self.tables["disk_info"][0] = tmp[1].append("hostname")
        self.tables["disk_info"][1] = Assembler.sql_crt_tb("disk_info", tmp[1])
        tmp = self.__filter_cols(tmp[0], "netwk_")
        self.tables["netwk_info"][0] = tmp[1]
        self.tables["netwk_info"][1] = Assembler.sql_crt_tb("netwk_info", tmp[1])
        self.tables["basic_info"][0] = tmp[0]
        self.tables["basic_info"][1] = Assembler.sql_crt_tb("basic_info", tmp[0])
        logger.info("Table disk_info contains columns: %s" % self.tables["disk_info"][0])
        logger.info("Table disk_info use sql: %s" % self.tables["disk_info"][1])
        logger.info("Table netwk_info contains columns: %s" % self.tables["netwk_info"][0])
        logger.info("Table netwk_info use sql: %s" % self.tables["netwk_info"][1])
        logger.info("Table basic_info contains columns: %s" % self.tables["basic_info"][0])
        logger.info("Table basic_info use sql: %s" % self.tables["basic_info"][1])

    def create_tables(self):
        for tb in self.tables.values():
            # excute each sql to create corresponding tables

            self.conn.execute(tb[1])

    def categorize_data(self):
        """
            self.tables["disk_info"][3].append({})
            self.tables["netwk_info"][3].append({})
            self.tables["basic_info"][3].append({})
        """
        for element in self.data:
            disk_info = dict()
            netwk_info = dict()
            basic_info = dict()
            for k, v in element.iteritems():
                if k.startswith("disk_") or k == "hostname":
                    disk_info[k] = v
                elif k.startswith("netwk_") or k == "hostname":
                    netwk_info[k] = v
                else:
                    basic_info[k] = v
            self.tables["disk_info"][2].append(disk_info)
            self.tables["netwk_info"][2].append(netwk_info)
            self.tables["basic_info"][2].append(basic_info)

    def insert_rows(self):
        self.categorize_data()
        for k, v in self.tables.iteritems():
            # k = "disk_info"
            # v = [[cols],sql_create_table, [{data},{data}], [sql_insert_rows]]
            for data in v[2]:
                self.conn.execute(Assembler.sql_insert_rows(k, data))
        self.conn.commit()
        self.conn.close()

    # private methods
    @staticmethod
    def sql_insert_rows(tb, data):
        cols = []
        values = []
        for k, v in data.iteritems():
            cols.append(k)
            values.append(v)
        cols = ",".join(cols)
        values = map(Assembler.addquotation, values)
        values = ",".join(values)
        sql = "INSERT INTO {0} ({1}) VALUES ({2});".format(tb, cols, values)
        logger.info("SQL = %s" % sql)
        return sql

    @staticmethod
    def addquotation(a):
        return "'" + str(a) + "'"

    @staticmethod
    def sql_crt_tb(tb, cols):
        """

        :param tb: str
        :param cols: list
        :return: sql: str
        """
        col_style = " VARCHAR(20)"
        for col in cols:
            # col col_style,
            cols[cols.index(col)] = col + col_style
        columns = ",".join(cols)
        return "CREATE TABLE {0} ( {1} );".format(tb, columns)

    @staticmethod
    def __jfiles():
        """
        : () => ["/**/.../**.json", "/**/.../**.json", ...]
        """
        return [join(INSPECT_COLLECT_DIR, file) for file in walk(INSPECT_COLLECT_DIR).next()[2] if
                file.endswith(".json")]

    @staticmethod
    def __filter_cols(data, label):
        """
        : (list, str) => [[rest],[filtered]]
        """
        return [[i for i in data if not i.startswith(label)], [i for i in data if i.startswith(label)]]


if __name__ == "__main__":
    pass
