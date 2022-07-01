#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ast
import logging
import os
import json
from schema import Schema
import psycopg2
import cloudevents
from env import ADB_POSTGRE_SINK_CONFIG_SCHEMA

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


class VerifyException(Exception): pass


class Sink(object):
    """
    将数据发送到ADB
    """
    # Initialize the specific sink with the SINK_CONFIG
    def __init__(self):
        try:
            sink_config = os.environ["SINK_CONFIG"]
            env = json.loads(sink_config)
            if not Schema(ADB_POSTGRE_SINK_CONFIG_SCHEMA, ignore_extra_keys=True).is_valid(env):
                raise VerifyException("env validate failed")
            self.config = ast.literal_eval(sink_config)
            self.conn = None
            print(self.config)
        except Exception as e:
            logger.error(e)
            logger.error(
                "ERROR: Unexpected error: Could not get the mandatory sink config.")
            raise Exception(str(e))

    # Connect the sink target with with sink config, we coud place this logic in __init__ phase also
    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=self.config["host"],  # 替换为您的HOST名称。
                port=self.config["port"],  # 替换为您的端口号。
                user=self.config["user"],  # 替换为您的用户名。
                password=self.config["password"],  # 替换为您的用户名对应的密码。
                database=self.config["database"],  # 替换为您的数据库名称。
                connect_timeout=5)
            return
        except Exception as e:
            logger.error(e)
            logger.error(
                "ERROR: Unexpected error: Could not connect to MySql instance.")
            raise Exception(str(e))

    # deal the message, 这里可以对消息进行处理后返回
    def deal_message(self, ori_message):
        return ori_message

    # Write a entity to db table
    def write(self, ori_message):
        """
        发送消息
        """
        message = json.loads(ori_message)
        validate_message_schema(message)

        sql = "INSERT INTO Data(id) VALUES ('%s') RETURNING *" % (message['id'])
        print(sql)
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
            print(result)
            return result


def validate_message_schema(message):
    return Schema(message_schema, ignore_extra_keys=True).validate(message)


sink = Sink()

def initializer(context):
    logger.info('initializing sink connect')
    # how to resume connection when resumed from snapshot?
    sink.connect()


# 函数入口
def handler(event, context):
    if not sink.is_connected():
        sink.connect()

    # event 要求为 cloud event，校验
    evt = json.loads(event)
    # todo: check the cloud event 需要确定 event 格式，是 binary 还是 json

    print("handler event: ", evt)
    for record in evt:
        print(record)
        body = sink.deal_message(record)
        sink.write(body)
    return {"result": "success"}


def destroy(context):
    logger.info('stop sink connection')
    sink.close()

