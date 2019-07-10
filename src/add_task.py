#! usr/bin/env/python3
# coding:utf-8
# @Time: 2019-07-08 16:02
# Author: turpure

from config.conf import info
from tasks import get_joom_product_by_category
import redis


def add_task(cate_id, page_token):
    res = get_joom_product_by_category.delay(cate_id, page_token)


def get_task():
    rd = redis.Redis(**info['redis']['task'])
    while True:
        task = rd.blpop('joom_task', 30)
        if not task:
            continue
        print('get task {} from task queue'.format(task[1]))
        task_info = task[1].decode('utf-8').split(',')
        print(task_info)
        cate_id = task_info[0]
        page_token = task_info[1]
        add_task(cate_id, page_token)


if __name__ == '__main__':
    get_task()


