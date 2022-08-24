# -*- coding: utf-8 -*-
import json
import logging
import os
from py2neo import Graph, Node
from retrying import retry

from schema import Schema

import sink_schema

logger = logging.getLogger()
default_retry_times = 3


def result_need_retry(result):
    """if the result needs to be retried.

    Args:
        result: bool, if the function call succeeded

    Returns:
        Bool, if result == True, return False otherwise return True

    Raises:
        None
    """
    if result:
        return False
    return True


class Sink(object):
    """Sink Class.

     The main class deal with the incoming message and put to sink target.
     """

    def __init__(self):
        """Class Initializer. Initialization should realized in connect method.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self.connected = False

    def connect(self, sink_config):
        """Sink connector construct method.
        Args:
            sink_config: config of this sink connector

        Returns:
            None

        Raises:
            None
        """

        self.sink_config = sink_config
        try:
            url = sink_config['host'] + ":" + sink_config['port']
            user = sink_config['user']
            password = sink_config['password']
            self.conn = Graph(url, auth=(user, password))
        except Exception as e:
            logger.error(e)
            logger.error(
                "ERROR: Unexpected error: Could not connect to Neo4j instance.")
            raise Exception(str(e))

        self.connected = True

    def close(self):
        """Sink connector deconstruct method.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self.connected = False

    def is_connected(self):
        """Sink connector connect check.

         Args:
             None

         Returns:
             None

         Raises:
             None
         """
        return self.connected

    def _write_data(self, data_list):
        """ Inner method to write data to neo4j instance.

        Args:
            single_data: input data

        Returns:

        Raises:
            Exception
        """
        for data in data_list:
            print(data['key'])
            node = Node(data['key'], name=data['value'])
            self.conn.create(node)
        return True

    @retry(stop_max_attempt_number=default_retry_times, wait_exponential_multiplier=1000,
           retry_on_result=result_need_retry)
    def deliver(self, payload):
        """Sink operator.
            deliver data to hologres

        Args:
            payload: input payload

        Returns:
            None

        Raises:
            Exception
        """

        data_list = []
        if self.sink_config['batchOrNot'] == "True":
            for single_payload in payload:
                data_list.append(json.loads(single_payload)['data'])
        else:
            data_list.append(json.loads(payload[0])['data'])
        try:
            deliver_success = self._write_data(data_list)
            return deliver_success
        except Exception as e:
            logger.error(e)
            logger.error(
                "ERROR: unknown error: write data to Neo4j failed.")
            raise e


sink = Sink()


def initialize(context):
    """Sink function initializer.
        this method is called before the function invocation,
        and will be only called once in a specified container.
        todo: User should realize this method

    Args:
        context: fc function invocation context

    Returns:
        None

    Raises:
        todo: xx
    """
    logger.info('initializing sink connect')
    sink_config_env = os.environ.get('SINK_CONFIG')
    sink_config = json.loads(sink_config_env)
    if not sink_schema.validate_sink_config_schema(sink_config):
        logger.error("validate failed error: %s",
                     Schema(sink_schema.SINK_CONFIG_SCHEMA, ignore_extra_keys=True).validate(sink_config))
        raise Exception("SINK_CONFIG_SCHEMA validate failed")

    sink.connect(sink_config)


def destroy(context):
    """Sink function deconstructor.
       This method is called as pre-stop, which will be executed before the function container releasement.

    Args:
        context: fc function invocation context

    Returns:
        None

    Raises:
        Exception
    """
    logger.info('stop sink connection')
    sink.close()


def handler(event, context):
    """FC Function handler.

     Args:
         event: FC function invocation payload.

     Returns:
         context:  FC function invocation context. Valid params see: https://help.aliyun.com/document_detail/422182.html.

     Raises:
         Exception.
     """

    payload = json.loads(event)

    # only single data type is validated here.
    if (sink.sink_config['batchOrNot'] == "False") and (sink.sink_config["eventSchema"] == "cloudEvent"):
        logger.info("check single data with schema: cloudEvent")
        if not sink_schema.validate_message_schema(payload):
            logger.error("validate failed error: %s",
                         Schema(sink_schema.MESSAGE_SCHEMA, ignore_extra_keys=True).validate(payload))
            raise Exception("MESSAGE_SCHEMA validate failed")

    if (sink.sink_config['batchOrNot'] == "True") and (sink.sink_config["eventSchema"] == "cloudEvent"):
        logger.info("check batch data with schema: cloudEvent")
        for single_payload in payload:
            if not sink_schema.validate_message_schema(single_payload):
                logger.error("validate failed error: %s",
                             Schema(sink_schema.MESSAGE_SCHEMA, ignore_extra_keys=True).validate(single_payload))
                raise Exception("MESSAGE_SCHEMA validate failed")

    if not sink.is_connected():
        raise Exception("unconnected sink target")

    deliver_success = sink.deliver(payload)

    if not deliver_success:
        raise Exception("Fail to write neo4j.")

    return "success"
