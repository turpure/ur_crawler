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


app = Celery('cate_tasks', broker=info['redis']['broker'], backend=info['redis']['backend'])
rd = redis.Redis(**info['redis']['task'])
db = DataBase()
db.connect()
con = db.con
cur = con.cursor()


# @app.task
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
                save(rows)
                break
            except:
               pass
        if page_token != 'last':
            rd.lpush('joom_task', ','.join(['cate', category_id, page_token]))
        items['products'] = products
    except Exception as why:
        print('fail to get result cause of {}'.format(why))

    return items


def parse(rows, cate_id):
    for row in rows:
        yield (cate_id, row['id'], row['name'], row['price'],
               row['mainImage']['images'][-1]['url'],
               row.get('rating', '0'), row['storeId'])


def save(rows):
    global con, cur
    sql = ('insert ignore into joom_cateProduct (cateId, productId,productName,price,mainImage,'
           'rating,storeId,taskCreatedTime, taskUpdatedTime)'
           ' values (%s, %s, %s,%s,%s,%s,%s,now(),now())')
    cur.executemany(sql, rows)
    con.commit()


if __name__ == '__main__':
    res = get_joom_product_by_category('1473502940450448049-189-2-118-805240694')
    print(res)



