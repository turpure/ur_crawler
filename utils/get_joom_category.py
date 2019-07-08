#! usr/bin/env/python3
# coding:utf-8
# @Time: 2019-07-08 13:15
# Author: turpure

import requests
import pymysql
import json
from config.conf import info


def get_category():
    base_url = 'https://api.joom.com/1.1/categoriesHierarchy?currency=USD&language=en-US&levels=1&_=jxo1mc94'
    headers = info['headers']
    ret = requests.get(base_url, headers=headers)
    res = ret.json()
    rows = parse(res)
    save(rows)


def parse(data):
    cats = data['payload']['children']
    for ct in cats:
        yield (ct['name'], ct['id'])


def save(rows):
    con = pymysql.connect(**info['database']['mysql'])
    cur = con.cursor()
    sql = 'insert into joom_category (cateName, cateId) values (%s, %s)'
    cur.executemany(sql, rows)
    con.commit()
    cur.close()
    con.close()


if __name__ == '__main__':
    get_category()
