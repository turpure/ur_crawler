#! usr/bin/env/python3
# coding:utf-8
# @Time: 2019-07-23 9:29
# Author: turpure

from config.conf import info
from services.db_con import DataBase
import redis
import json

db = DataBase()
db.connect()
con = db.con
cur = con.cursor()


def get_result():
    rd = redis.Redis(**info['redis']['result'])
    while True:
        result = rd.blpop('joom_result', 30)
        if not result:
            continue
        if result[1]:
            save_result(result[1])


def save_result(result_info):
    global con, cur
    try:
        res = json.loads(result_info)
        if res['result_type'] == 'product':
            sql = ('insert  into joom_product (productId,proCreatedDate,reviewsCount)'
                   ' values (%s, %s, %s) on duplicate key update reviewsCount=values(reviewsCount)')
            try:
                cur.execute(sql, (res['product_id'], res['created_date'], res['reviews_count']))
                con.commit()
                print('putting {}'.format(res['product_id']))
            except Exception as why:
                print(why)

        elif res['result_type'] == 'reviews':
            sql = ('insert ignore into joom_reviews (reviewId, productId,starRating,reviewCreatedDate)'
                   ' values (%s, %s, %s,%s)')
            try:
                cur.execute(sql, (res['id'], res['productId'], res['startRating'], res['reviewCreatedDate']))
                con.commit()
            except Exception as why:
                print(why)
        elif res['result_type'] == 'update':
            sql = ('insert into joom_productLog (productId,reviewsCount,price,rating,publishedDate, updatedDate)'
                   ' values (%s, %s, %s,%s,%s, %s) on duplicate key update price=values(price), rating=values(rating)')
            try:
                cur.execute(sql, (res['product_id'], res['reviews_count'],
                                  res['price'], res['rating'],
                                  res['created_date'], res['updated_date']))
                con.commit()
                print(f'updating {res["product_id"]}')
            except Exception as why:
                print(why)
        elif res['result_type'] == 'cate':
            sql = ('insert ignore into joom_cateProduct (cateId, productId,productName,price,mainImage,'
                   'rating,storeId,taskCreatedTime, taskUpdatedTime)'
                   ' values (%s, %s, %s,%s,%s,%s,%s,now(),now())')
            try:
                cur.execute(sql, (
                    res['cateId'], res['productId'], res['productName'],
                    res['price'], res['mainImage'], res['rating'], res['storeId']))
                con.commit()
            except Exception as why:
                print(why)

        elif res['result_type'] == 'store':
            sql = ('insert ignore into joom_storeProduct (productId,productName,price,mainImage,'
                   'rating,storeName,storeId,taskCreatedTime, taskUpdatedTime)'
                   ' values (%s, %s, %s,%s,%s,%s,%s,now(),now())')
            try:
                cur.execute(sql, (
                    res['productId'], res['productName'], res['price'], res['mainImage'],
                    res['rating'], res['storeName'], res['storeId']))
                con.commit()
            except Exception as why:
                print(why)
    except:
        print(result_info)


if __name__ == '__main__':
    get_result()
