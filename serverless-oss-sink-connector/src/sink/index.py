# -*- coding: utf-8 -*-
import json
import logging
import os
import oss2
import time
from retrying import retry

from oss2 import exceptions
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
        """Class Initializer. Initialization should  be realized in connect method.

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
            endpoint = self.sink_config["endpoint"]
            bucket = self.sink_config["bucket"]
            access_key_id = self.sink_config["access_key_id"]
            access_key_secret = self.sink_config["access_key_secret"]
            security_token = self.sink_config["security_token"]
            auth = oss2.StsAuth(access_key_id, access_key_secret, security_token)
            self.conn = oss2.Bucket(auth, endpoint, bucket)
        except Exception as e:
            logger.error(e)
            logger.error(
                "ERROR: Unexpected error: Could not connect to OSS instance.")
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

    def oss_file_exist(self, key):
        try:
            self.conn.get_object_meta(key)
        except exceptions.NoSuchKey as err1:
            return False, None
        except Exception as err2:
            logger.error("get oss key {%s} failed, err: %s", key, err2)
            return False, err2
        logger.info("file already exist, oss key: %s", key)
        return True, None

    @retry(stop_max_attempt_number=default_retry_times, wait_exponential_multiplier=1000,
           retry_on_result=result_need_retry)
    def deliver(self, payload):
        """Sink operator.

        Args:
            payload: input payload

        Returns:
            Bool, if the function call succeeded

        Raises:
            todo: xx
        """
        logger.info('exec deliver')
        filename = sink.sink_config["objectPathPrefix"] + "_" + str(int(time.time()))
        data = json.dumps(payload)
        exist, e = self.oss_file_exist(filename)
        while e is not None:
            exist, e = self.oss_file_exist(filename)
        if exist:
            logger.error("upload oss abort, %s is exist in %s", filename, self.sink_config["bucket"])
            return False
        response = self.conn.put_object(filename, data)
        if response.status != 200:
            logger.error("upload oss failed, response: %s", response)
            return False
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
    creds = context.credentials
    sink_config["access_key_id"] = creds.access_key_id
    sink_config["access_key_secret"] = creds.access_key_secret
    sink_config["security_token"] = creds.security_token
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

        success = sink.deliver(payload)

    except Exception as e:
        logger.error(e)
        return json.dumps({"success": False, "error_message": str(e)})

    return json.dumps({"success": True, "error_message": ""})
