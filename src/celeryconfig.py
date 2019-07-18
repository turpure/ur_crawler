#! usr/bin/env/python3
# coding:utf-8
# @Time: 2019-07-18 15:21
# Author: turpure


from kombu import Exchange, Queue
from config.conf import info

BROKER_URL = info['redis']['broker']
CELERY_RESULT_BACKEND = info['redis']['backend']

CELERY_QUEUES = (
    Queue("cate_tasks", Exchange("cate_tasks"), routing_key="cate_tasks"),
    Queue("product_tasks", Exchange("product_tasks"), routing_key="product_tasks"),
)
# 路由
CELERY_ROUTES = {
    'reviews_tasks.get_joom_reviews': {"queue": "product_tasks", "routing_key": "product_tasks"},
    'product_tasks.get_joom_product_by_id': {"queue": "reviews_tasks", "routing_key": "reviews_tasks"}
}
CELERY_DEFAULT_QUEUE = 'cate_tasks'  # 设置默认的路由
CELERY_DEFAULT_EXCHANGE = 'cate_tasks'
CELERY_DEFAULT_ROUTING_KEY = 'cate_tasks'

CELERY_TASK_RESULT_EXPIRES = 10  # 设置存储的过期时间　防止占用内存过多
