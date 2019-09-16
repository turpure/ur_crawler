#! usr/bin/env/python3
# coding:utf-8
# @Time: 2019-07-08 16:02
# Author: turpure

from config.conf import info
from src.tasks import get_joom_product_by_category, get_joom_reviews, get_joom_product_by_id
import redis


def add_task(*args):
    task_type = args[0]
    if task_type == 'product':
        item_id = args[1]
        res = get_joom_product_by_id.delay(item_id)

    if task_type == 'cate':
        item_id = args[1]
        parent_id = args[2]
        page_token = args[3]
        res = get_joom_product_by_category.delay(item_id, page_token, parent_id)

    if task_type == 'reviews':
        item_id = args[1]
        page_token = args[2]
        res = get_joom_reviews.delay(item_id, page_token)


def get_task():
    rd = redis.Redis(**info['redis']['task'])
    while True:
        task = rd.blpop('joom_task', 30)
        if not task:
            continue
        print('get task {} from task queue'.format(task[1]))
        task_info = task[1].decode('utf-8').split(',')
        print(task_info)
        add_task(*task_info)


if __name__ == '__main__':
    get_task()


