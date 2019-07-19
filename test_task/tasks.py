#! usr/bin/env/python3
# coding:utf-8
# @Time: 2019-07-19 10:01
# Author: turpure

# !/usr/bin/env
# -*-conding:utf-8-*-
from celery import Celery, platforms

platforms.C_FORCE_ROOT = True

app = Celery()
app.config_from_object("celeryconfig")


@app.task
def taskA(x, y):
    return x * y


@app.task
def taskB(x, y, z):
    return x + y + z


@app.task
def add(x, y):
    return x + y

