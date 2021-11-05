#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json
import os
from schema import Schema
from kafka import KafkaProducer
from kafka.errors import KafkaError


logger = logging.getLogger()
logger.setLevel(logging.INFO)


# enrichment_schema is used to validate rules.
# todo: move to layer
"""
field: pk in db, 对于 oss 采用单列匹配(对于 csv 文件，是否有多列匹配的需求？)
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


class SourceOSS(object):

    def __init__(self, oss_csv_file_arn):
        # todo
        return

    def fetch(self, pri_key):
        # todo
        return


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
def deal_message(message, remote_message, rule):
    # todo
    return message


# 函数入口
def handler(event, context):
    """
    功能说明：根据 env rule 规则对 kafka 源 topic 传入的 value 进行富化。rule 的规则详见 schema 注释
    :param event:
    :param context:
    :env:
        bootstrap_servers: kafka bootstrap servers
        target_topic: kafka target
        oss_csv_file_arn:   acs:oss:cn-beijing:123456:bucket1/file1
        rule: schema
    :return:
    """
    bootstrap_servers = os.getenv("bootstrap_servers")
    topic_name = os.getenv("target_topic")
    # like: acs:oss:region:accid:bucket/file
    # 跨region暂不支持。不过 arn 给 跨 region 留了口子
    oss_csv_file_arn = os.getenv("oss_csv_file_arn")

    rule_str = os.getenv("rule")
    validate_rule_schema(rule_str)
    rule = json.loads(rule_str)

    kafka_producer = ProduceToKafka(bootstrap_servers)
    oss_source = SourceOSS(oss_csv_file_arn)
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
        remote_message = oss_source.fetch(value[rule["field"]])
        # 2. deal
        dealt_message = deal_message(value, remote_message, rule)
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

