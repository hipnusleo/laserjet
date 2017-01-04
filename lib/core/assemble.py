#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    @Author:        yyg
    @Create:        2016MMDD
    @LastUpdate:    2016-12-15 HH:MM:SS
    @Version:       0.0
"""
from json import load
from logging import getLogger
from os import mkdir, remove, walk
from os.path import abspath, exists, isdir, isfile, join
import sqlite3
from shutil import rmtree
from params import INSPECT_COLLECT_DIR, LOGGER_NAME, SQLITE_DB_DIR
from utils import json_deserialize

"""Summary of Module 'assemble'

"""
__version__ = "0.0"
__all__ = []
__author__ = "yyg"


logger = getLogger(LOGGER_NAME)


class WrongDataBaseException(Exception):
    """Raise when neither sqlite nor mysql is chosen."""
    pass


class Assembler(object):

    def __init__(self, batch_params):
        """
        :args BatchParams batch_params
        """
        self._db_type = batch_params.get_db()
        self._conn = None
        self._dbname = "laserjet"
        self._table = "inspect_info"
        self._info = list()
        self._cols = set()

    def start(self):
        self._load_json()
        if self._db_type == "sqlite":
            if (exists(SQLITE_DB_DIR) and isdir(SQLITE_DB_DIR)):
                rmtree(SQLITE_DB_DIR)
                logger.info("Rmdir %s" % SQLITE_DB_DIR)
                mkdir(SQLITE_DB_DIR)
                logger.info("Make dir %s" % SQLITE_DB_DIR)
            else:
                mkdir(SQLITE_DB_DIR)
                logger.info("Make dir %s" % SQLITE_DB_DIR)

            self._sqlite_do_create_db(
                join(SQLITE_DB_DIR, self._dbname + ".db"))
            self._conn.execute(self._sqlite_sql_create_table())
            for sql in (self._sqlite_sql_insert_rows()):
                self._conn.execute(sql)
            self._conn.commit()
        elif self._db_type == "mysql":
            pass
        else:
            logger.error("db type is: %s" % self._db_type)
            raise WrongDataBaseException

    def _load_json(self):
        """
        :param str path
        """
        for file in walk(INSPECT_COLLECT_DIR).next()[2]:
            if file.endswith(".json"):
                with open(join(INSPECT_COLLECT_DIR, file)) as json_content:
                    json_content_dict = json_deserialize(json_content)
                    self._info.append(json_content_dict)
                    self._cols = self._cols | set(json_content_dict.keys())

    def _sqlite_do_create_db(self, dbpath):
        logger.info("connect to db %s" % dbpath)
        self._conn = sqlite3.connect(dbpath)

    def _sqlite_sql_create_table(self):
        self._cols = list(self._cols)
        head = "CREATE TABLE %s " % self._table
        col_style = " VARCHAR(16)"
        for col in self._cols:
            index = self._cols.index(col)
            self._cols[index] = "".join(["", col, col_style])
        sql = head + "(" + ",".join(self._cols) + ")"
        logger.info("sql : %s" % sql)
        return sql

    def _sqlite_sql_insert_rows(self):
        sqls = list()
        cols = list()
        rows = list()
        pairs = {
            "cols": cols,
            "rows": rows
        }
        for each in self._info:
            for key, value in each.iteritems():
                pairs["cols"].append(key)
                pairs["rows"].append("'%s'" % value)
            cols = ",".join(pairs["cols"])
            rows = ",".join(pairs["rows"])
            sql = "INSERT INTO %s (%s) VALUES (%s);" % (
                self._table, cols, rows)
            logger.info("INSERT SQL : \n %s" % sql)
            sqls.append(sql)
        return sqls

if __name__ == "__main__":
    from params import BatchParams
    b = BatchParams()
    a = Assembler(b)
