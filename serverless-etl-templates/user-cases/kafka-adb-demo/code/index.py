#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json
from schema import Schema
import pymysql
import psycopg2


logger = logging.getLogger()
logger.setLevel(logging.INFO)

message_schema = {
        'channel_id': str,
        'logtype': str,
        'match_uid': int,
        'ml': int,
        'match_info': str,
        'uid': int,
        'type': str,
        'addtime': int,
        'search_gender': int,
        'host': str,
        'gender': int,
        'ctcode': str,
    }

class ProduceToADB(object):
    """
    将数据发送到ADB
    """

    def __init__(self):
        try:
            self.conn = pymysql.connect(
                host="",  # 替换为您的HOST名称。
                port=3306,  # 替换为您的端口号。
                user="",  # 替换为您的用户名。
                passwd="",  # 替换为您的用户名对应的密码。
                db="",  # 替换为您的数据库名称。
                connect_timeout=5)
        except Exception as e:
            logger.error(e)
            logger.error(
                "ERROR: Unexpected error: Could not connect to MySql instance.")
            raise Exception(str(e))

    def produce(self, oriMessage):
        """
        发送消息
        """
        message = json.loads(oriMessage)
        validate_message_schema(message)

        sql = "INSERT INTO kafka_message(channel_id, \
                   logtype, match_uid, ml, match_info, uid, type, addtime, search_gender, host, gender, ctcode) \
                   VALUES ('%s', '%s', %s, %s, '%s', '%s', '%s',  %s, %s, '%s', %s, '%s') RETURNING *" % \
              (message['channel_id'], message['logtype'], message['match_uid'], message['ml'], message['match_info'], message['uid'],
               message['type'], message['addtime'], message['search_gender'], message['host'], message['gender'], message['ctcode'])
        print(sql)
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
            print(result)
            return result


class ProduceToADBPostgre(object):
    """
    将数据发送到ADB
    """

    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                host="gp-uf638xnkx552xid0zo-master.gpdb.rds.aliyuncs.com",  # 替换为您的HOST名称。
                port=5432,  # 替换为您的端口号。
                user="postgre_root",  # 替换为您的用户名。
                password="root@adb1",  # 替换为您的用户名对应的密码。
                database="kafka_adb_postgre",  # 替换为您的数据库名称。
                connect_timeout=5)
            return
        except Exception as e:
            logger.error(e)
            logger.error(
                "ERROR: Unexpected error: Could not connect to MySql instance.")
            raise Exception(str(e))

    def produce(self, oriMessage):
        """
        发送消息
        """
        message = json.loads(oriMessage)
        validate_message_schema(message)

        sql = "INSERT INTO kafka_message(channel_id, \
                   logtype, match_uid, ml, match_info, uid, type, addtime, search_gender, host, gender, ctcode) \
                   VALUES ('%s', '%s', %s, %s, '%s', '%s', '%s',  %s, %s, '%s', %s, '%s') RETURNING *" % \
              (message['channel_id'], message['logtype'], message['match_uid'], message['ml'], message['match_info'], message['uid'],
               message['type'], message['addtime'], message['search_gender'], message['host'], message['gender'], message['ctcode'])
        print(sql)
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
            print(result)
            return result


def validate_message_schema(message):
    return Schema(message_schema, ignore_extra_keys=True).validate(message)


# 这里可以对消息进行处理后返回
def deal_message(message):
    return message


# 函数入口
def handler(event, context):
    # adb on mysql
    # produce_to_adb = ProduceToADB()
    # adb on postgre
    produce_to_adb = ProduceToADBPostgre()
    evt = json.loads(event)
    for record in evt:
        # processing data 数据处理，在这边可以做数据变换，最终保持数据投递格式为jsonArray
        dealt_message = deal_message(record)
        print("dealt1")
        print(deal_message)
        if dealt_message is None:
            continue
        for keyItem in dealt_message.keys():
            logger.info(keyItem)
            if keyItem == 'key' and dealt_message[keyItem] == 'kafka_log':
                # this is a valid message
                # kafka_log key marks the data. value is the real json message
                value = dealt_message['value']
                logger.info(value)
                msg = produce_to_adb.produce(value)
                break

    return "success"
