#! usr/bin/env/python3
# coding:utf-8
# @Time: 2019-07-05 16:33
# Author: turpure


import redis
from config.conf import info
from services.db_con import DataBase
import json


class ResultSaver(object):
    def __init__(self):
        db = DataBase()
        db.connect()
        self.con = db.con
        self.cur = self.con.cursor()
        self.rd = redis.Redis(**info['redis']['result'])

    def get_result(self):
        keys = self.rd.keys()
        for key in keys:
            try:
                res = self.rd.get(key).decode('utf-8')
                res = json.loads(res)
                ret = res['result']
                if isinstance(ret, dict) and 'cateId' in ret:
                    cateId = ret['cateId']
                    rows = ret['products']
                    for row in rows:
                        out = dict()
                        out['cateId'] = cateId
                        out['productId'] = row['id']
                        out['productName'] = row['name']
                        out['price'] = row['price']
                        out['mainImage'] = row['mainImage']['images'][-1]['url']
                        out['rating'] = row.get('rating', '0')
                        out['storeId'] = row['storeId']
                        self.save(out)

            except Exception as why:
                print(why)
        self.con.commit()

    def save(self, row):
        sql = ('insert ignore into joom_cateProduct (cateId, productId,productName,price,mainImage,'
               'rating,storeId,taskCreatedTime, taskUpdatedTime)'
               ' values (%s, %s, %s,%s,%s,%s,%s,now(),now())')
        self.cur.execute(sql, (row['cateId'],
                               row['productId'],
                               row['productName'],
                               row['price'],
                               row['mainImage'],
                               row['rating'],
                               row['storeId'],
                               ))
        print('saving {}'.format(row['productId']))


if __name__ == "__main__":
    worker = ResultSaver()
    worker.get_result()


