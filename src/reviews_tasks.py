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

app = Celery('reviews_tasks', broker=info['redis']['broker'], backend=info['redis']['backend'])
rd = redis.Redis(**info['redis']['task'])
db = DataBase()
db.connect()
con = db.con
cur = con.cursor()


@app.task
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
                res = (row['id'], row['productId'], row['starRating'], datetime.datetime.fromtimestamp(row['createdTimeMs'] / 1000))
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
    print('save putting {}'.format(row[1]))
    con.commit()


if __name__ == '__main__':
    res = get_joom_reviews('1521448224733469691-154-1-26193-4209136207', '')
    print(res)



