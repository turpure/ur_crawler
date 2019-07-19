#! usr/bin/env/python3
# coding:utf-8
# @Time: 2019-07-18 17:32
# Author: turpure

import requests
from celery import Celery, platforms
import json
from config.conf import info
import redis
from services.db_con import DataBase
import datetime

platforms.C_FORCE_ROOT = True
app = Celery()
app.config_from_object("celeryconfig")

rd = redis.Redis(**info['redis']['task'])
db = DataBase()
db.connect()
con = db.con
cur = con.cursor()


@app.task
def get_joom_product_by_category(category_id, page_token=''):
    global rd
    base_url = 'https://api.joom.com/1.1/search/products?currency=USD&language=en-US&_=jxo2h958'
    headers = info['headers']
    items = {'cateId': category_id}
    products = []
    try:
        request_data = {"filters": [
            {"id": "categoryId",
             "value": {"type": "categories",
                      "items": [{"id": category_id}]}}], "count": 36, 'pageToken': page_token}

        for i in range(4):
            try:
                request_data = json.dumps(request_data)
                ret = requests.post(base_url, headers=headers, data=request_data)
                payload = ret.json()['payload']
                page_token = payload.get('nextPageToken', 'last')
                products = payload.get('items', [])
                rows = parse(products, category_id)
                for row in rows:
                    rd.lpush('joom_task', ','.join(['product', row[1], '']))
                    rd.lpush('joom_task', ','.join(['reviews', row[1], '']))
                cate_save(rows)
                break
            except:
               pass
        if page_token != 'last':
            rd.lpush('joom_task', ','.join(['cate', category_id, page_token]))
        items['products'] = products
    except Exception as why:
        print('fail to get result cause of {}'.format(why))

    return items


@app.task
def get_joom_product_by_id(product_id, *args):
    base_url = 'https://api.joom.com/1.1/products/{}?currency=USD&language=en-US&_=jxo1mc9e'.format(product_id)
    headers = info['headers']
    for _ in range(3):
        try:
            ret = requests.get(base_url, headers=headers)
            created_date = ret.json()['payload']['variants'][0]['createdTimeMs']
            created_date = datetime.datetime.utcfromtimestamp(created_date / 1000)
            product_save((product_id, created_date))
            break
        except Exception as why:
            print(why)


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
                res = (row['id'], row['productId'], row['starRating'], datetime.datetime.utcfromtimestamp(row['createdTimeMs'] / 1000))
                review_save(res)
            break
        except:
            pass

    if page_token != 'last':
        rd.lpush('joom_task', ','.join(['reviews', product_id, page_token]))


def parse(rows, cate_id):
    for row in rows:
        yield (cate_id, row['id'], row['name'], row['price'],
               row['mainImage']['images'][-1]['url'],
               row.get('rating', '0'), row['storeId'])


def cate_save(rows):
    global con, cur
    sql = ('insert ignore into joom_cateProduct (cateId, productId,productName,price,mainImage,'
           'rating,storeId,taskCreatedTime, taskUpdatedTime)'
           ' values (%s, %s, %s,%s,%s,%s,%s,now(),now())')
    cur.executemany(sql, rows)
    con.commit()


def product_save(rows):
    global con, cur
    sql = ('insert ignore into joom_product (productId,proCreatedDate)'
           ' values (%s, %s)')
    cur.execute(sql, rows)
    con.commit()


def review_save(row):
    global con, cur
    sql = ('insert ignore into joom_reviews (reviewId, productId,starRating,reviewCreatedDate)'
           ' values (%s, %s, %s,%s)')
    cur.execute(sql, row)
    con.commit()


if __name__ == '__main__':
    res = get_joom_product_by_category.delay('1473502940450448049-189-2-118-805240694')
    print(res.status)



