#! usr/bin/env/python3
# coding:utf-8
# @Time: 2019-07-04 17:32
# Author: turpure

import requests
from celery import Celery
from config.conf import info
import redis
from services.db_con import DataBase
import datetime

app = Celery('product_tasks', broker=info['redis']['broker'], backend=info['redis']['backend'])
rd = redis.Redis(**info['redis']['task'])
db = DataBase()
db.connect()
con = db.con
cur = con.cursor()


def save(rows):
    global con, cur
    sql = ('insert ignore into joom_product (productId,proCreatedDate, reviewsCount)'
           ' values (%s, %s, %s)')
    cur.execute(sql, rows)
    con.commit()


# @app.task
def get_joom_product_by_id(product_id, *args):
    base_url = 'https://api.joom.com/1.1/products/{}?currency=USD&language=en-US&_=jxo1mc9e'.format(product_id)
    headers = info['headers']
    for _ in range(3):
        try:
            ret = requests.get(base_url, headers=headers)
            payload = ret.json()['payload']
            reviews_count = int(payload['reviewsCount']['value'])
            created_date = payload['variants'][0]['createdTimeMs']
            created_date = datetime.datetime.utcfromtimestamp(created_date / 1000)
            save((product_id, created_date, reviews_count))
            break
        except Exception as why:
            print(why)


if __name__ == '__main__':
    res = get_joom_product_by_id('5b7bc04a1436d40177ce3b26')
    print(res)



