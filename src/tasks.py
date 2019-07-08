#! usr/bin/env/python3
# coding:utf-8
# @Time: 2019-07-04 17:32
# Author: turpure

import requests
from celery import Celery
import json


app = Celery('tasks', broker='redis://''@47.88.7.50:6380/1', backend='redis://''@127.0.0.1:6379/5')


@app.task
def get_joom_product(category_id):
    base_url = 'https://api.joom.com/1.1/search/products?currency=USD&language=en-US&_=jxo2h958'
    headers = {
        'Authorization': 'Bearer SEV0001MTU0NjY1Mzc2M3xTSU9XdUJFbFU4NDJ5VHVndk8tV3ROem8yYVFCV0QtYjE2aTBDM3FNLWZkbVFyX01aTFJUek05REJZUVZnWVNmOE5TanlCWXhYRk84MWFINHZDTE5UVUJGb0ZSTmFWLXlkZlRCem9YRVg4R21GSEEwVHNQeHJIUWZKMmJ5dWd2VmpKNkZ4Q0V6VS1JdF9EZzF1UGtyb1NzcVQ5VDlQLTRwNnJ4Nl9yaHZTUkEzUmRfZUI0ZFB1TGxXejFFTkNzNm1PUzZoY1BScXI1YVhEWGlWdmVwODJIOVhxTnlZcGYxSVdDQzJXY1RTQjMyUjRWc09FVVU9fJgmguEcQE9NGiD_vYv4ymZpnsmOBH4btJX1l56WY4V7',
        'X-API-Token': 'p5F3VmqeHtMfBcvvpwTNVm9mRJuzHzx6',
        'Content-Type': 'application/javascript'
    }

    try:
        request_data = {"filters":
                            [{"id": "categoryId",
                              "value": {"type": "categories",
                                        "items": [{"id": category_id}]}}], "count": 36}
        request_data = json.dumps(request_data)
        ret = requests.post(base_url, headers=headers, data=request_data)
        return (ret.json()['payload']['items'])
    except Exception as why:
        print(why)


if __name__ == '__main__':
    # print(get_joom_product('1473502940450448049-189-2-118-805240694'))
    res = get_joom_product.delay('1473502940450448049-189-2-118-805240694')



