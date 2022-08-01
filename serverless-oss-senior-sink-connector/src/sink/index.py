# -*- coding: utf-8 -*-
import json
import logging
import os
import oss2
import time
import sink_schema

from retrying import retry
from oss2 import exceptions
from schema import Schema
from compress_pkg.zip import compress_file_with_zip

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
            # 从 sink_config 变量中获取初始化参数，并创建 oss 客户端
            # get params from sink_config and create oss client
            endpoint = self.sink_config["endpoint"]
            bucket = self.sink_config["bucket"]
            accessKeyID = self.sink_config["accessKeyID"]
            accessKeySecret = self.sink_config["accessKeySecret"]
            securityToken = self.sink_config["securityToken"]

            auth = oss2.StsAuth(accessKeyID, accessKeySecret, securityToken)
            self.client = oss2.Bucket(auth, endpoint, bucket)
        except Exception as e:
            logger.error("new oss client failed.", e)
            raise e

        self.connected = True
        logger.info("new oss client success")

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
        return self.compress(filename, data)


    def compress(self, filename, data):
        try:
            compressType = sink.sink_config['compressType']
            if compressType == 'None':
                res = self.client.put_object(filename, data)
                return self.process_response(res)
            elif compressType == "ZIP":
                res = compress_file_with_zip(self.client, filename, data)
                return self.process_response(res)
            elif compressType == "GZIP":
                pass
            elif compressType == "Snappy":
                pass
            elif compressType == "Hadoop-Compatible Snappy":
                pass
        except Exception as e:
            logger.error("upload oss failed", e)
            return False

        return True

    def process_response(self, response):
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
    sink_config = json.loads(os.environ.get('SINK_CONFIG'))
    creds = context.credentials
    sink_config["accessKeyID"] = creds.access_key_id
    sink_config["accessKeySecret"] = creds.access_key_secret
    sink_config["securityToken"] = creds.security_token

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
        if not sink.is_connected():
            raise Exception("unconnected oss target")

        payload = json.loads(event)
        if not sink.deliver(payload):
            raise Exception("put object to oss failed")
    except Exception as e:
        logger.error(e)
        return json.dumps({"success": False, "error_message": str(e)})

    return json.dumps({"success": True, "error_message": ""})
