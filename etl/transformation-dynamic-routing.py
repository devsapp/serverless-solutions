#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import os
import re

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
def deal_message(message, rule, routing_by_key):
    result = set()
    if routing_by_key and message["key"] == 0:
        result.add(rule["defaultTopic"])
        return result
    elif not routing_by_key and len(message["value"]) == 0:
        return result
    v = message["value"]
    if routing_by_key:
        v = message["key"]
    if len(v) == 0:
        result.add(rule["defaultTopic"])
        return result
    for r in rule["rules"]:
        pattern = r["regex"]
        target_topics = r["targetTopics"]
        if pattern is None:
            continue
        if re.match(pattern, v) is not None:
            for topic in target_topics:
                result.add(topic)
    if len(result) == 0:
        result.add(rule["defaultTopic"])
    return result


# In this demo, we will introduce you how to route the input events into
# different topics dynamically. For example, we have two inputs
# `Oral-B, toothpaste, $12.98, 100g` and `Colgate, toothpaste, $7.99, 80g`
# and routing-rules which could be described as an item from Oral-B should be
# sent to topic `Oral-B-item-topic` while an item from Colgate should be sent to topic
# `Colgate-item-topic`, and then the `Oral-B, toothpaste, $12.98, 100g` message
# will be routed to topic `Oral-B-item-topic` while the `Colgate, toothpaste, $7.99, 80g`
# will be routed to topic `Colgate-item-topic`.
# In particular, the rule can be hard-coded in your functions, and it
# also can be retrieved from oss or any other data sources.

# 函数入口
def handler(event, context):
    bootstrap_servers = os.getenv("bootstrap_servers")
    #
    # rule meta:
    #
    # defaultTopic: # String, routing all mismatched messages to default topic
    # rules: # List, rules describes a list of regex-based routing rules
    #   - regex: # String, any regex matched string will be routing to each target topic for once
    #     targetTopics: # List, all target topics related to regex
    #
    # rule example json:
    #
    # {
    #   "defaultTopic": "unknown-brand-topic",
    #   "rules": [
    #       {
    #           "regex": "^Colgate",
    #           "targetTopics": ["Colgate-item-topic","Colgate-discount-topic"]
    #       },{
    #           "regex": "^Oral-B",
    #           "targetTopics": ["Oral-B-item-topic", "Oral-B-discount-topic"]
    #       }
    #   ]
    # }
    rule_json = os.getenv("routing_rule")
    routing_by_key = os.getenv("routing_by_key", 'False').lower() in ('true', '1', 't')
    # processing data 数据处理，在这边可以做数据变换，最终保持数据投递格式为jsonArray
    evt = json.loads(event)
    rule = json.loads(rule_json)
    produce_to_kafka = ProduceToKafka(bootstrap_servers)
    for record in evt:
        target_topics = deal_message(record, rule, routing_by_key)
        if len(target_topics) == 0:
            continue
        for target_topic in target_topics:
            key = record["key"]
            if key is None:
                continue
            value = record["value"]
            if value is None:
                continue
            msg = produce_to_kafka.produce(target_topic, key, value)
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
