#! usr/bin/env/python3
# coding:utf-8
# @Time: 2019-07-04 15:27
# Author: turpure


from celery import Celery


# app = Celery('tasks', broker='redis://''@127.0.0.1:6379/2', backend='redis://''@127.0.0.1:6379/3')
app = Celery('tasks', broker='redis://''@47.88.7.50:6380/2', backend='redis://''@127.0.0.1:6379/3')


@app.task
def add(x, y):
    return x + y




