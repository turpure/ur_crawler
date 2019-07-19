#! usr/bin/env/python3
# coding:utf-8
# @Time: 2019-07-18 15:21
# Author: turpure


from kombu import Exchange, Queue
from celery import platforms
from config.conf import info

platforms.C_FORCE_ROOT = True

BROKER_URL = info['redis']['broker']
CELERY_RESULT_BACKEND = info['redis']['backend']

CELERY_QUEUES = (
    Queue("cate_tasks", Exchange("cate_tasks"), routing_key="cate_tasks"),
    Queue("product_tasks", Exchange("product_tasks"), routing_key="product_tasks"),
    Queue("reviews_tasks", Exchange("reviews_tasks"), routing_key="reviews_tasks"),
)
# 路由
CELERY_ROUTES = {
    'tasks.get_joom_reviews': {"queue": "reviews_tasks", "routing_key": "reviews_tasks"},
    'tasks.get_joom_product_by_category': {"queue": "cate_tasks", "routing_key": "cate_tasks"},
    'tasks.get_joom_product_by_id': {"queue": "product_tasks", "routing_key": "product_tasks"}
}

