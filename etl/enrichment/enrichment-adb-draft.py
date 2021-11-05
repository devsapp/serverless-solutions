#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json
import os
from schema import Schema
import pymysql
import psycopg2
from kafka import KafkaProducer
from kafka.errors import KafkaError


logger = logging.getLogger()
logger.setLevel(logging.INFO)


# enrichment_schema is used to validate messages.
# todo: move to layer
"""
field: pk in db, 对于数据库采用单主键
output_fields: 取出的字段，拼接到 value 中
missing: 源中缺失时默认填充值
mode:
fill	当目标字段不存在或者值为空时，设置目标字段。
fill-auto	当新值非空，且目标字段不存在或者值为空时，设置目标字段。
add	当目标字段不存在时，设置目标字段。
add-auto	当新值非空，且目标字段不存在时，设置目标字段。
overwrite	总是设置目标字段。
overwrite-auto	当新值非空，设置目标字段。
"""
enrichment_schema = {
    'field': str,
    'output_fields': [str],
    'missing': str,
    'mode': str
}


def validate_rule_schema(rule):
    return Schema(enrichment_schema, ignore_extra_keys=True).validate(rule)


class SourceADBMysql(object):
    """
    将数据发送到ADB
    """

    def __init__(self, host, port, user, password, database, table):
        try:
            self.conn = pymysql.connect(
                host=host,  # 替换为您的HOST名称。
                port=port,  # 替换为您的端口号。
                user=user,  # 替换为您的用户名。
                passwd=password,  # 替换为您的用户名对应的密码。
                db=database,  # 替换为您的数据库名称。
                connect_timeout=5)
            self.table = table # 用于富化的数据表名称
        except Exception as e:
            logger.error(e)
            logger.error(
                "ERROR: Unexpected error: Could not connect to MySql instance.")
            raise Exception(str(e))

    def fetch(self, pri_key):
        """
        查询记录
        """
        sql = "SELECT * FROM %s WHERE PK = %s" % (self.table, pri_key)
        print(sql)
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
            print(result)
            return result


class SourceADBPostgre(object):
    """
    将数据发送到ADB
    """

    def __init__(self, host, port, user, password, database, table):
        try:
            self.conn = psycopg2.connect(
                host=host,  # HOST名称
                port=port,  # 端口号
                user=user,  # 用户名
                password=password,  # 用户名对应的密码
                database=database,  # 数据库名称
                connect_timeout=5)
            self.table = table  # 用于富化的数据表名称
        except Exception as e:
            logger.error(e)
            logger.error(
                "ERROR: Unexpected error: Could not connect to MySql instance.")
            raise Exception(str(e))

    def fetch(self, pri_key):
        """
        查询记录
        """
        sql = "SELECT * FROM %s WHERE PK = %s" % (self.table, pri_key)
        print(sql)
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
            print(result)
            return result


class ProduceToKafka(object):
    """
    将数据发送到Kafka集群
    """

    def __init__(self, bootstrap_servers):
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                                      api_version=(0, 10, 2),
                                      retries=5)
        self.futureList = []

    def produce(self, topic_name, key, value):
        """
        发送消息
        """
        try:
            if key is not None:
                send_key = bytes(key, encoding="utf8")
            else:
                send_key = None
            if value is not None:
                send_value = bytes(value, encoding="utf8")
            else:
                send_value = None
            future = self.producer.send(topic_name, key=send_key, value=send_value)
            self.futureList.append(future)
            return None
        except KafkaError as e:
            return e

    def flush(self):
        try:
            for future in self.futureList:
                future.get()
            return None
        except KafkaError as e:
            return e


# 这里可以对消息进行处理后返回
def deal_message(message, remote_record, rule):
    # todo
    return message


# 函数入口
def handler(event, context):
    """
    功能说明：根据 kafka 源 topic 传入的 key 作为主键值对 adb 表进行查询，查到数据后，将 adb 其他列内容按照 kv 赋值给原信息（如已有则覆盖）
    :param event:
    :param context:
    :env:
        bootstrap_servers: kafka bootstrap servers
        target_topic: kafka target
        dbType:   enum(adb-postgre|adb-mysql)
        dbHost:   string
        dbPort:   string
        user:     string
        password: string
        database: string
        rule: schema
    :return:

    """
    bootstrap_servers = os.getenv("bootstrap_servers")
    topic_name = os.getenv("target_topic")

    rule_str = os.getenv("rule")
    validate_rule_schema(rule_str)
    rule = json.loads(rule_str)

    kafka_producer = ProduceToKafka(bootstrap_servers)

    dbType = os.getenv("dbType")
    host = os.getenv("host")
    port = os.getenv("port")
    user = os.getenv("user")
    password = os.getenv("password")
    database = os.getenv("database")
    table = os.getenv("table")

    adb_source = SourceADBMysql(host, port, user, password, database, table)
    evt = json.loads(event)

    # 富化仅针对 value 进行。是否有 key 的需求？
    key = None
    value = None

    for record in evt:
        for keyItem in record.keys():
            if keyItem == 'key':
                key = record[keyItem]
                continue
            if keyItem == 'value':
                value = record[keyItem]
                continue
        # 1. fetch
        remote_record = adb_source.fetch(value[rule["field"]])
        # 2. enrichment
        dealt_message = deal_message(value, remote_record, rule)
        # 3. produce
        msg = kafka_producer.produce(topic_name, dealt_message['key'], dealt_message['value'])
        if msg is None:
            logger.info("Try send message succeed. original kafka message info:" + str(record))
        else:
            logger.info("Try send to kafka failed! error message:" + bytes.decode(
                msg) + " original kafka message info:" + record)
    msg = kafka_producer.flush()
    if msg is None:
        logger.info("Flush message succeed.")
    else:
        logger.info("Flush to kafka failed! error message:" + bytes.decode(msg))

    return "success"

