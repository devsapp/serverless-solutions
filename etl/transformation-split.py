#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import os

from kafka import KafkaProducer
from kafka.errors import KafkaError

# 数据分隔处理
# 函数接收单个消息，并将其按照分隔符（换行符）分为多个输出事件到目标 topic 中。
# 可以import python内置模块以及部分fc支持的内置模块。
# fc支持内置模块参见：https://help.aliyun.com/document_detail/56316.html#title-2kb-mpf-bbk
# 函数名不要变更，否则会处理失败
# message为字典格式，key和value对应来源topic的key和value，不要变更其他key
# 默认支持的分隔符为换行符，可根据需要修改分隔符


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
def deal_message(message, delimiter, splitting_by_key):
    messages = []
    if splitting_by_key and len(message["key"]) == 0:
        # keep
        messages.append(message)
        return message
    elif not splitting_by_key and len(message["value"]) == 0:
        # throw message if value is empty
        return messages
    if splitting_by_key:
        for v in message["key"].split(delimiter):
            if len(v) == 0:
                continue
            messages.append({
                "key": v,
                "value": message["value"]
            })
    else:
        for v in message["value"].split(delimiter):
            if len(v) == 0:
                continue
            messages.append({
                "key": message["key"],
                "value": v
            })
    return messages


# In this demo, we will introduce you how to split an item list
# into several single items with an customized delimiter. For example, we have an input
# `Oral-B, toothpaste, $12.98, 100g\nColgate, toothpaste, $7.99, 80g\nColgate, toothbrush, $1.99, 20g` with
# the giving delimiter `\n`,
# then the function will produce three items as outputs
# `Oral-B, toothpaste, $12.98, 100g`
# `Colgate, toothpaste, $7.99, 80g`
# `Colgate, toothbrush, $1.99, 20g`
# 函数入口
def handler(event, context):
    bootstrap_servers = os.getenv("bootstrap_servers")
    target_topic_name = os.getenv("target_topic")
    delimiter = os.getenv("delimiter")
    splitting_by_key = os.getenv("splitting_by_key", 'False').lower() in ('true', '1', 't')

    # processing data 数据处理，在这边可以做数据变换，最终保持数据投递格式为jsonArray
    evt = json.loads(event)

    produce_to_kafka = ProduceToKafka(bootstrap_servers)
    for record in evt:
        dealt_messages = deal_message(record, delimiter, splitting_by_key)
        if dealt_messages is None:
            continue
        for dealt_message in dealt_messages:
            key = dealt_message["key"]
            value = dealt_message["value"]
            msg = produce_to_kafka.produce(target_topic_name, key, value)
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
