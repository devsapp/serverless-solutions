#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ast
import json
import logging
import os

import psycopg2
from schema import Schema

from env import HOLOGRES_SINK_CONFIG_SCHEMA

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class VerifyException(Exception):
    pass


class Sink(object):
    # Initialize the specific sink with the SINK_CONFIG
    def __init__(self):
        try:
            context = os.environ.get('context')
            host = os.environ.get('host')
            database = os.environ.get('database')
            user = os.environ.get('user')
            password = os.environ.get('password')
            port = os.environ.get('port')



            sink_config_str = json.dumps(
                {'context': context, 'host': host,
                 'database': database, 'user': int(user),
                 'password': password, 'port': int(port)})  # os.environ["SINK_CONFIG"]
            sink_config = json.loads(sink_config_str)

            if not Schema(HOLOGRES_SINK_CONFIG_SCHEMA, ignore_extra_keys=True).is_valid(sink_config):
                logger.error("validate failed error: %s",
                             Schema(HOLOGRES_SINK_CONFIG_SCHEMA, ignore_extra_keys=True).validate(sink_config))
                raise VerifyException(
                    "env SINK_CONFIG validate failed with the schema")
            self.config = ast.literal_eval(sink_config)
        except Exception as e:
            logger.error(e)
            logger.error(
                "ERROR: Unexpected error: Could not get the mandotary sink config.")
            raise Exception(str(e))

    # Connecet the sink target with with sink config, we coud place this logic in __init__ phase also
    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                dbname=self.config['database'],
                user=self.config['user'],
                password=self.config['password'],
                application_name=self.config['context'])
            return
        except Exception as e:
            logger.error(e)
            logger.error(
                "ERROR: Unexpected error: Could not connect to hologres instance.")
            raise Exception(str(e))

    # Execute a sql sentence
    # INSERT_SQL_EXAMPLE: "insert into hologresdemo(name, address) values('test1', 'shanghai') returning name, address"
    # CREATE_SQL_EXAMPLE: 'CREATE TABLE HOLOGRESDEMO (name VARCHAR(255), address VARCHAR(255))'
    def execute(self, sql):
        print(sql)
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchone()
            if not result:
                return
            self.conn.commit()
            print(result)
            cursor.close()
            return result

    # deal the message, 这里可以对消息进行处理后返回
    def deal_message(self, message):
        return message

    # Write a entity to db table
    def write(self, message):
        sql = "INSERT INTO Data(id) VALUES ('%s') RETURNING *" % (
            message['data'])
        print(sql)
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchone()
            if not result:
                return
            self.conn.commit()
            print(result)
            cursor.close()
            return result

    def close(self):
        self.conn.close()

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

    evt = json.loads(event)
    print("handler event: ", evt)
    body = sink.deal_message(evt)
    sink.write(body)
    return {"result": "success"}


def destroy(context):
    logger.info('stop sink connection')
    sink.close()
