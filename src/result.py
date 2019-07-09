#! usr/bin/env/python3
# coding:utf-8
# @Time: 2019-07-05 16:33
# Author: turpure


import redis

r = redis.Redis(host='127.0.0.1', port=6379, db=3)

keys = r.keys()

for key in keys:
    res = r.get(key)
    print(key, res)
