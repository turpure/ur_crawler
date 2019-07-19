#! usr/bin/env/python3
# coding:utf-8
# @Time: 2019-07-19 10:02
# Author: turpure


from kombu import Exchange, Queue
from celery import platforms

platforms.C_FORCE_ROOT = True

BROKER_URL = "redis://localhost:6379/10"
CELERY_RESULT_BACKEND = "redis://localhost:6379/11"

CELERY_QUEUES = (
    Queue("default", Exchange("default"), routing_key="default"),
    Queue("for_task_A", Exchange("for_task_A"), routing_key="for_task_A"),
    Queue("for_task_B", Exchange("for_task_B"), routing_key="for_task_B")
)

CELERY_ROUTES = {
    'tasks.taskA': {"queue": "for_task_A", "routing_key": "for_task_A"},
    'tasks.taskB': {"queue": "for_task_B", "routing_key": "for_task_B"}
}