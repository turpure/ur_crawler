#! usr/bin/env/python3
# coding:utf-8
# @Time: 2019-07-19 10:02
# Author: turpure


from kombu import Exchange, Queue
from config.conf import info

CELERY_IMPORTS = ('test_task.tasks',)

BROKER_URL = info['redis']['broker']
CELERY_RESULT_BACKEND = info['redis']['backend']

CELERY_QUEUES = (
    Queue("default", Exchange("default"), routing_key="default"),
    Queue("for_task_A", Exchange("for_task_A"), routing_key="for_task_A"),
    Queue("for_task_B", Exchange("for_task_B"), routing_key="for_task_B")
)

CELERY_ROUTES = {
    'test_task.tasks.taskA': {"queue": "for_task_A", "routing_key": "for_task_A"},
    'test_task.tasks.taskB': {"queue": "for_task_B", "routing_key": "for_task_B"}
}
