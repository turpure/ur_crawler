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


def get_token():
    """
    获取最新的joom token
    缓存放redis里面，过期从mysql里面取
    :return:
    """
    name = 'joom_token'

    if not res_cache.get(name):
        db = DataBase()
        db.connect()
        con = db.con
        cur = con.cursor()
        sql = 'select token as x_api_token, bearerToken, x_version from urTools.sys_joom_token'
        cur.execute(sql)
        ret = cur.fetchone()
        db.close()
        res_cache.set(name, ','.join(ret))
        # 设置过期时间为1天
        res_cache.expire(name, 60 * 60 * 2)

    else:
        ret = res_cache.get(name).decode('utf-8').split(',')

    return ret


@app.task
def get_joom_product_by_category(category_id, parent_id, page_token=''):
    global rd
    base_url = 'https://api.joom.com/1.1/search/products?currency=USD&language=en-US&_=jxo2h958'
    headers = info['headers']
    items = {'cateId': category_id, 'parent_id': parent_id, 'page_token': page_token}
    try:
        token = get_token()
        x_api_token, bearer_token, x_version = token
        headers['Authorization'] = bearer_token
        headers['X-API-Token'] = x_api_token
        headers['X-Version'] = x_version

        request_data = {
            # "sorting": [{"fieldName": "salesCount", "order": "desc"}],
            "sorting": [{"fieldName": "age", "order": "asc"}],
            "filters": [
            {"id": "categoryId",
             "value": {"type": "categories",
                      "items": [{"id": category_id}]}}], "count": 36, 'pageToken': page_token}
        # 代理
        proxies = get_proxy()

        # 错误重试
        next_page = None
        for _ in range(2):
            try:
                request_data = json.dumps(request_data)
                ret = requests.post(base_url, headers=headers, data=request_data, proxies=proxies)
                payload = ret.json()['payload']
                next_page = payload.get('nextPageToken', 'last')
                products = payload.get('items', [])
                rows = parse(products, parent_id)
                for row in rows:
                    res = {'result_type': 'cate', 'cateId': row[0], 'productId': row[1],
                           'productName': row[2], 'price': row[3],
                           'mainImage': row[4], 'rating': row[5], 'storeId': row[6]}
                    res_rd.lpush('joom_result', json.dumps(res))
                    rd.lpush('joom_task', ','.join(['product', row[1], '']))
                break
            except Exception as why:
                next_page = None
                print(f'failed to get cat cause of {why}')

        # 如果获取到下一页
        if next_page:
            if next_page != 'last':
                rd.lpush('joom_task', ','.join(['cate', category_id, parent_id, next_page]))
            else:
                print('this is the last page!')
        # 如果获取失败，重新传入当前页
        else:
            rd.lpush('joom_task', ','.join(['cate', category_id, parent_id, page_token]))

    except Exception as why:
        print('fail to get result cause of {}'.format(why))

    return items


@app.task
def get_joom_product_by_store(store_name, store_id, page_token=''):
    global rd
    base_url = 'https://api.joom.com/1.1/search/content?currency=USD&language=en-US&_=k1smqse0'
    headers = info['headers']
    items = {'storeName': store_name, 'storeId': store_id, 'pageToken': page_token}
    try:
        token = get_token()
        x_api_token, bearer_token, x_version = token
        headers['Authorization'] = bearer_token
        headers['X-API-Token'] = x_api_token
        headers['X-Version'] = x_version

        request_data = {
            "origin":
                {"source": "store", "storeId": store_id}, "count": 36, "pageToken": ""}
        # 代理
        proxies = get_proxy()

        # 错误重试
        next_page = None
        for _ in range(2):
            try:
                request_data = json.dumps(request_data)
                ret = requests.post(base_url, headers=headers, data=request_data, proxies=proxies)
                payload = ret.json()['payload']
                next_page = payload.get('nextPageToken', 'last')
                products = payload.get('items', [])
                rows = store_parse(products, store_name)
                for row in rows:
                    res = {'result_type': 'store', 'storeName': row[0], 'productId': row[1],
                           'productName': row[2], 'price': row[3],
                           'mainImage': row[4], 'rating': row[5], 'storeId': row[6]}
                    res_rd.lpush('joom_result', json.dumps(res))
                    rd.lpush('joom_task', ','.join(['product', row[1], '']))
                break
            except Exception as why:
                next_page = None
                print(f'failed to get cat cause of {why}')

        # 如果获取到下一页
        if next_page:
            if next_page != 'last':
                rd.lpush('joom_task', ','.join(['store', store_name, store_id, next_page]))
            else:
                print('this is the last page!')
        # 如果获取失败，重新传入当前页
        else:
            rd.lpush('joom_task', ','.join(['store', store_name, store_id, page_token]))

    except Exception as why:
        print('fail to get result cause of {}'.format(why))

    return items


@app.task
def get_joom_product_by_id(product_id, *args):
    global res_rd
    base_url = 'https://api.joom.com/1.1/products/{}?currency=USD&language=en-US'.format(product_id)
    headers = info['headers']

    # 代理
    proxies = get_proxy()

    for _ in range(3):
        try:
            # 取最新headers
            token = get_token()
            x_api_token, bearer_token, x_version = token
            headers['Authorization'] = bearer_token
            headers['X-API-Token'] = x_api_token
            headers['X-Version'] = x_version

            ret = requests.get(base_url, headers=headers, proxies=proxies)
            payload = ret.json()['payload']
            reviews_count = int(payload['reviewsCount']['value'])
            created_date = payload['variants'][0]['createdTimeMs']
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
def update_joom_product_by_id(product_id, *args):
    global res_rd
    base_url = 'https://api.joom.com/1.1/products/{}?currency=USD&language=en-US'.format(product_id)
    headers = info['headers']

    # 代理
    proxies = get_proxy()

    for _ in range(2):
        try:
            # 取最新headers
            token = get_token()
            x_api_token, bearer_token, x_version = token
            headers['Authorization'] = bearer_token
            headers['X-API-Token'] = x_api_token
            headers['X-Version'] = x_version

            ret = requests.get(base_url, headers=headers, proxies=proxies)
            payload = ret.json()['payload']
            reviews_count = int(payload['reviewsCount']['value'])
            price = payload['lite']['price']
            rating = payload['lite'].get('rating', 0)
            created_date = payload['variants'][0]['createdTimeMs']
            created_date = str(datetime.datetime.fromtimestamp(created_date / 1000))
            updated_date = str(datetime.datetime.now())[:10]
            row = {'result_type': 'update',
                   'created_date': created_date,
                   'product_id': product_id,
                   'reviews_count': reviews_count,
                   'price': price,
                   'rating': rating,
                   'updated_date': updated_date,
                   }
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
    return 'fail to get {}, {}'.format(product_id, page_token)


def parse(rows, cate_id):
    for row in rows:
        yield (cate_id, row['id'], row['name'], row['price'],
               row['mainImage']['images'][-1]['url'],
               row.get('rating', '0'), row['storeId'])


def store_parse(rows, store_name):
    for row in rows:
        row = row['content']['product']
        yield (store_name, row['id'], row['name'], row['price'],
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


def get_proxy():
    # 代理服务器
    proxy_host = "http-dyn.abuyun.com"
    proxy_port = "9020"

    # 代理隧道验证信息
    proxy_user = info['proxy']['user']
    proxy_pass = info['proxy']['pass']

    proxy_meta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
        "host": proxy_host,
        "port": proxy_port,
        "user": proxy_user,
        "pass": proxy_pass,
    }

    proxies = {
        "http": proxy_meta,
        "https": proxy_meta,
    }

    return proxies


if __name__ == '__main__':
    get_joom_product_by_store.delay('YHMen', '1507714387304326627-56-3-709-4035548807', '')
    # res = get_joom_product_by_store('YHMen', '1507714387304326627-56-3-709-4035548807')
    # print(res)



