#! usr/bin/env/python3
# coding:utf-8
# @Time: 2019-07-19 10:04
# Author: turpure


from test_task.tasks import taskA, taskB, add
re1 = taskA.delay(100, 200)
re2 = taskB.delay(1, 2, 3)
res = add.delay(2, 4)
print(re1.status)
print(re2.id)
