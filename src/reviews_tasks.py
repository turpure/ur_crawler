#! usr/bin/env/python3
# coding:utf-8
# @Time: 2019-07-04 17:32
# Author: turpure

import requests
from celery import Celery
import json
from config.conf import info
import redis
from services.db_con import DataBase
import datetime

app = Celery('tasks', broker=info['redis']['broker'], backend=info['redis']['backend'])
rd = redis.Redis(**info['redis']['task'])
db = DataBase()
db.connect()
con = db.con
cur = con.cursor()


@app.tasks
def get_joom_reviews(product_id, page_token=''):
    base_url = 'https://api.joom.com/1.1/products/{}/reviews?filter_id=all&count=200'.format(product_id)
    params = {'pageToken': page_token}
    headers = info['headers']
    for _ in range(3):
        try:
            ret = requests.get(base_url, headers=headers, params=params)
            payload = ret.json()['payload']
            items = payload['items']
            page_token = payload.get('nextPageToken', 'last')
            for row in items:
                res = (row['id'], row['productId'], row['starRating'], datetime.datetime.utcfromtimestamp(row['createdTimeMs'] / 1000))
                save(res)
            break
        except:
            pass

    if page_token != 'last':
        rd.lpush('joom_task', ','.join(['reviews', product_id, page_token]))


def save(row):
    global con, cur
    sql = ('insert ignore into joom_reviews (reviewId, productId,starRating,reviewCreatedDate)'
           ' values (%s, %s, %s,%s)')
    cur.execute(sql, row)
    con.commit()


if __name__ == '__main__':
    res = get_joom_reviews('5b7bc04a1436d40177ce3b26', '')
    print(res)



