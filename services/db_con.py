#! usr/bin/env/python3
# coding:utf-8
# @Time: 2019-07-09 13:51
# Author: turpure

from config.conf import info
import pymysql
import logging


class DataBase(object):

    def __init__(self):
        self.con = None

    def connect(self):
        try:
            if not self.con:
                self.con = pymysql.connect(**info['database']['mysql'])
                logging.info('success to connect mysql')
        except Exception as why:
            logging.error('fail to connect mysql cause of {} '.format(why))

    def close(self):
        try:
            if self.con:
                self.con.close()
            logging.info('success to close mysql')
        except Exception as why:
            logging.error('fail to close mysql cause of {}'.format(why))
        finally:
            self.con = None






