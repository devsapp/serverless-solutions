# -*- coding: utf-8 -*-
import json
import logging
import os
from retrying import retry

from schema import Schema

import sink_schema

logger = logging.getLogger()
default_retry_times = 3

def result_need_retry(result):
    """if the result needes to be retried.

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
            todo: User should realize this method

        Args:
            sink_config: config of this sink connector

        Returns:
            None

        Raises:
            None
        """
        self.connected = True
        self.sink_config = sink_config
        pass


    def close(self):
        """Sink connector deconstruct method.
            todo: User should realize this method

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self.connected = False
        pass


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


    @retry(stop_max_attempt_number=default_retry_times, wait_exponential_multiplier=1000, retry_on_result=result_need_retry)
    def deliver(self, payload):
        """Sink operator.
            todo: User should realize this method

        Args:
            payload: input payload
            todo: xx

        Returns:
            Bool, if the function call succeeded

        Raises:
            todo: xx
        """
        logger.info('exec deliver')

        try:
            pass
        except Exception as e:
            raise e

        return True


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
        todo: User should realize this method

    Args:
        context: fc function invocation context

    Returns:
        None

    Raises:
        todo: xx
    """
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
    try:

        payload = json.loads(event)
        # only single data type is validated here.
        if sink.sink_config['batchOrNot'] == "False" and sink.sink_config["eventSchema"] == "cloudEvent":
            logger.info("check single data with schema: cloudEvent")
            if not sink_schema.validate_message_schema(payload):
                logger.error("validate failed error: %s",
                             Schema(sink_schema.MESSAGE_SCHEMA, ignore_extra_keys=True).validate(payload))
                raise Exception("MESSAGE_SCHEMA validate failed")

        if not sink.is_connected():
            raise Exception("unconnected sink target")

        sink.deliver(payload)

    except Exception as e:
        logger.error(e)
        raise e

    return json.dumps({"success": True, "error_message": ""})
