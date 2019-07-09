#! usr/bin/env/python3
# coding:utf-8
# @Time: 2019-07-09 14:18
# Author: turpure


import unittest
from services.db_con import DataBase


class TestCon(unittest.TestCase):

    def test_con(self):
        db = DataBase()
        db.connect()
        self.assertIsNotNone(db.con, 'con  is not none')

    def test_close(self):
        db = DataBase()
        db.connect()
        self.assertIsNotNone(db.con, 'con  is not none')
        db.close()
        self.assertIsNone(db.con, 'con  is not none')


if __name__ == '__main__':
    unittest.main()


