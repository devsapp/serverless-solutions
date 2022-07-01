#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ast
import json
import logging
import os
from schema import Schema

from elasticsearch import Elasticsearch
from env import ES_SINK_CONFIG_SCHEMA

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# FC supported sink types
# FCHologresSink
# FCADBMySQLSink
# FCADBPostgreSQLSink
# FCElasticSearchSink
# FCKafkaSink
# FCAliyunOTSSink
# FCClickHouseSink


class VerifyException(Exception): pass


class Sink(object):
    # Initialize the specific sink with the SINK_CONFIG
    def __init__(self):
        try:
            host = os.environ.get('host')
            port = os.environ.get('port')
            user = os.environ.get('user')
            password = os.environ.get('password')

            ssl_bool_var = os.environ.get('use_ssl')
            use_ssl = False
            if ssl_bool_var == "True" or ssl_bool_var == "true":
                use_ssl = True
            index = os.environ.get('index')
            doc_type = os.environ.get('doc_type')
            id = os.environ.get('id')

            sink_config_str = json.dumps(
                {'use_ssl': use_ssl, 'host': host,
                 'index': index, 'user': user,
                 'doc_type': doc_type, 'id': id,
                 'password': password, 'port': int(port)})  # os.environ["SINK_CONFIG"]
            sink_config = json.loads(sink_config_str)

            if not Schema(ES_SINK_CONFIG_SCHEMA, ignore_extra_keys=True).is_valid(sink_config):
                logger.error("validate failed error: %s",
                             Schema(ES_SINK_CONFIG_SCHEMA, ignore_extra_keys=True).validate(sink_config))
                raise VerifyException("env validate failed")
            self.config = sink_config
            self.es = None
        except Exception as e:
            logger.error(e)
            logger.error(
                "ERROR: Unexpected error: Could not get the mandatory sink config.")
            raise Exception(str(e))

    # Connecet the sink target with with sink config, we coud place this logic in __init__ phase also
    def connect(self):
        try:
            self.es = Elasticsearch(
                [self.config['host']],
                http_auth=(self.config['user'], self.config['password']),
                port=self.config['port'],
                use_ssl=self.config['use_ssl']
            )
            return
        except Exception as e:
            logger.error(e)
            logger.error(
                "ERROR: Unexpected error: Could not connect to hologres instance.")
            raise Exception(str(e))

    # Write a entity to db table
    def write(self, body):
        self.es.index(index=self.config['index'], doc_type=self.config['doc_type'],id=self.config['id'],
                      body=body)

    def close(self):
        pass

    def isConnected(self):
        return True


sink = Sink()


def initializer(context):
    logger.info('initializing sink connect')
    # how to resume connection when resumed from snapshot?
    sink.connect()


def handler(event, context):
    if not sink.isConnected():
        sink.connect()

    # event 要求为 cloud event，校验
    evt = json.loads(event)
    # todo: check the cloud event 需要确定 event 格式，是 binary 还是 json

    print("handler event: ", evt)
    sink.write(evt)
    return {"result": "success"}


def destroy(context):
    logger.info('stop sink connection')
    sink.close()
