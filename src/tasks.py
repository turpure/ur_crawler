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
from celery.contrib import rdb


platforms.C_FORCE_ROOT = True
app = Celery()
app.config_from_object("celeryconfig")

rd = redis.Redis(**info['redis']['task'])
res_rd = redis.Redis(**info['redis']['result'])
res_cache = redis.Redis(**info['redis']['cache'])
db = DataBase()
db.connect()
con = db.con
cur = con.cursor()


def get_token():
    """
    获取最新的joom token
    缓存放redis里面，过期从mysql里面取
    :return:
    """
    name = 'joom_token'

    if not res_cache.get(name):
        sql = 'select token as x_api_token, bearerToken, x_versionfrom urTools.sys_joom_token'
        cur.execute(sql)
        ret = cur.fetchone()
        res_cache.set(name, ','.join(ret))
        # 设置过期时间为1天
        res_cache.expire(name, 60 * 60 * 24)

    else:
        ret = res_cache.get(name).decode('utf-8').split(',')
    return ret


@app.task
def get_joom_product_by_category(category_id, page_token=''):
    global rd
    base_url = 'https://api.joom.com/1.1/search/products?currency=USD&language=en-US&_=jxo2h958'
    headers = info['headers']
    items = {'cateId': category_id}
    try:
        token = get_token()
        x_api_token, bearer_token, x_version = token
        headers['Authorization'] = bearer_token
        headers['X-API-Token'] = x_api_token
        headers['X-Version'] = x_version

        request_data = {
            "sorting": [{"fieldName": "age", "order": "asc"}],
            "filters": [
            {"id": "categoryId",
             "value": {"type": "categories",
                      "items": [{"id": category_id}]}}], "count": 36, 'pageToken': page_token}

        # 错误重试
        for i in range(4):
            try:
                request_data = json.dumps(request_data)
                ret = requests.post(base_url, headers=headers, data=request_data)
                payload = ret.json()['payload']
                page_token = payload.get('nextPageToken', 'last')
                products = payload.get('items', [])
                rows = parse(products, category_id)
                for row in rows:
                    res = {'result_type': 'cate', 'cateId': row[0], 'productId': row[1],
                           'productName': row[2], 'price': row[3],
                           'mainImage': row[4], 'rating': row[5], 'storeId': row[6]}
                    res_rd.lpush('joom_result', json.dumps(res))
                    rd.lpush('joom_task', ','.join(['product', row[1], '']))
                    rd.lpush('joom_task', ','.join(['reviews', row[1], '']))
                break
            except:
                pass
        if page_token != 'last':
            rd.lpush('joom_task', ','.join(['cate', category_id, page_token]))
        # items['products'] = products
    except Exception as why:
        print('fail to get result cause of {}'.format(why))

    return items


@app.task
def get_joom_product_by_id(product_id, *args):
    global res_rd
    base_url = 'https://api.joom.com/1.1/products/{}?currency=USD&language=en-US&_=jxo1mc9e'.format(product_id)
    headers = info['headers']
    for _ in range(3):
        try:
            # 取最新headers
            token = get_token()
            x_api_token, bearer_token, x_version = token
            headers['Authorization'] = bearer_token
            headers['X-API-Token'] = x_api_token
            headers['X-Version'] = x_version

            ret = requests.get(base_url, headers=headers)
            payload = ret.json()['payload']
            reviews_count = int(payload['reviewsCount']['value'])
            created_date = payload['variants'][0]['publishedTimeMs']
            created_date = str(datetime.datetime.fromtimestamp(created_date / 1000))
            row = {'result_type': 'product', 'created_date': created_date,
                   'product_id': product_id,
                   'reviews_count': reviews_count}
            row = json.dumps(row)
            res_rd.lpush('joom_result', row)
            return product_id, created_date
        except Exception as why:
            print(why)
    return 'fail get product {}'.format(product_id)


@app.task
def get_joom_reviews(product_id, page_token=''):
    base_url = 'https://api.joom.com/1.1/products/{}/reviews?filter_id=all&count=200'.format(product_id)
    params = {'pageToken': page_token}
    headers = info['headers']
    items = None
    for _ in range(3):
        try:
            ret = requests.get(base_url, headers=headers, params=params)
            payload = ret.json()['payload']
            items = payload['items']
            page_token = payload.get('nextPageToken', 'last')
        except:
            pass
    if items:
        for row in items:
            res = {
                'result_type': 'reviews',
                'id': row['id'], 'productId': row['productId'],
                'starRating': row['starRating'],
                'reviewCreatedDate': datetime.datetime.fromtimestamp(row['createdTimeMs'] / 1000)
            }
            res_rd.lpush('joom_result', json.dumps(res))
        return 'get review  successfully'
    if page_token != 'last':
        rd.lpush('joom_task', ','.join(['reviews', product_id, page_token]))
    return 'fail to get {}, {}'.format(product_id,page_token)


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
    try:
        cur.execute(sql, rows)
        con.commit()
    except Exception as why:
        print(why)


def review_save(row):
    global con, cur
    sql = ('insert ignore into joom_reviews (reviewId, productId,starRating,reviewCreatedDate)'
           ' values (%s, %s, %s,%s)')
    try:
        cur.execute(sql, row)
        con.commit()
    except Exception as why:
        print(why)


if __name__ == '__main__':
    # res = get_joom_reviews('5b3774191436d4014721ed20','1-gaNyYXeTy0D4aqAAAAAAy0J2kp60QMAAuDVjMzc5MmVjNTZiNzYzMzgwMWMzNGNmYQ')
    # res = get_joom_product_by_id('5ad3c6e2efa3711361b82a9a')
    print(get_token())



