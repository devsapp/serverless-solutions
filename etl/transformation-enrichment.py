#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import json
from kafka import KafkaProducer
from kafka.errors import KafkaError
import kafka

# 数据转换，添加前/后缀
# 该示例往消息的key和value中添加一个后缀
# 可以import python内置模块以及部分fc支持的内置模块。
# fc支持内置模块参见：https://help.aliyun.com/document_detail/56316.html#title-2kb-mpf-bbk
# 函数名不要变更，否则会处理失败
# message为字典格式，key和value对应来源topic的key和value，不要变更其他key
# 请将处理完的message返回，返回None表示不往目标端发送


logger = logging.getLogger()
logger.setLevel(logging.INFO)


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
def deal_message(message):
    for keyItem in message.keys():
        if keyItem == 'key':
            message[keyItem] = message[keyItem] + "KeySurfix"
            continue
        if keyItem == 'value':
            message[keyItem] = message[keyItem] + "ValueSurfix"
            continue
    return message


# 函数入口
def handler(event, context):
    bootstrap_servers = os.getenv("bootstrap_servers")
    topic_name = os.getenv("target_topic")

    # processing data 数据处理，在这边可以做数据变换，最终保持数据投递格式为jsonArray
    evt = json.loads(event)

    produce_to_kafka = ProduceToKafka(bootstrap_servers)
    for record in evt:
        dealt_message = deal_message(record)
        if dealt_message is None:
            continue
        key = None
        value = None
        for keyItem in dealt_message.keys():
            if keyItem == 'key':
                key = dealt_message[keyItem]
                continue
            if keyItem == 'value':
                value = dealt_message[keyItem]
                continue
        msg = produce_to_kafka.produce(topic_name, key, value)
        if msg is None:
            logger.info("Try send message succeed. original kafka message info:" + str(record))
        else:
            logger.info("Try send to kafka failed! error message:" + bytes.decode(
                msg) + " original kafka message info:" + record)
    msg = produce_to_kafka.flush()
    if msg is None:
        logger.info("Flush message succeed.")
    else:
        logger.info("Flush to kafka failed! error message:" + bytes.decode(msg))

    return "success"
