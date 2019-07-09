#! usr/bin/env/python3
# coding:utf-8
# @Time: 2019-07-04 17:32
# Author: turpure

import requests
from celery import Celery
import json
from config.conf import info
import redis


app = Celery('tasks', broker=info['redis']['broker'], backend=info['redis']['backend'])
rd = redis.Redis(**info['redis']['task'])


@app.task
def get_joom_product_by_category(category_id, page_token=''):
    global rd
    base_url = 'https://api.joom.com/1.1/search/products?currency=USD&language=en-US&_=jxo2h958'
    headers = info['headers']
    try:
        request_data = {"filters":[
            {"id": "categoryId",
             "value": {"type": "categories",
                       "items": [{"id": category_id}]}}], "count": 36, 'pageToken': page_token}
        for i in range(4):
            try:
                request_data = json.dumps(request_data)
                ret = requests.post(base_url, headers=headers, data=request_data)
                payload = ret.json()['payload']
                page_token = payload.get('nextPageToken', '')
                break
            except:
               pass
        rd.lpush('joom_task', ','.join([category_id, page_token]))
        return ':'.join([category_id, page_token])
    except Exception as why:
        return 'fail to get result cause of {}'.format(why)


if __name__ == '__main__':
    # print(get_joom_product('1473502940450448049-189-2-118-805240694'))
    res = get_joom_product_by_category.delay('1473502940450448049-189-2-118-805240694', '')
    print(res)



