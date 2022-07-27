# -*- coding: utf-8 -*-
import json
import logging
import os

from retrying import retry
from schema import Schema
from odps import ODPS

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

        Args:
            sink_config: config of this sink connector

        Returns:
            None

        Raises:
            None
        """
        try:
            self.sink_config = sink_config
            odps_project = sink_config['odpsProject']
            odps_endpoint = sink_config['odpsEndpoint']
            odps_ak_id = sink_config['accessKeyID']
            odps_ak_secret = sink_config['accessKeySecret']
            self.odps_client = ODPS(odps_ak_id, odps_ak_secret, odps_project, odps_endpoint)
            self.connected = True
        except Exception as e:
            logger.error("initializing connection failed.", e)
            raise e
        pass


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


    @retry(stop_max_attempt_number=default_retry_times, wait_exponential_multiplier=1000, retry_on_result=result_need_retry)
    def deliver(self, payload):
        """Sink operator.
        Args:
            payload: input payload

        Returns:
            Bool, if the function call succeeded

        Raises:
        """
        logger.info('exec deliver')

        try:
            block_records = []
            if self.sink_config['batchOrNot'] == "True":
                for e in payload:
                    block_records.append(e['data'])
            else:
                block_records.append(payload['data'])
            input_record = self.format_records(block_records)
            self.odps_client.write_table(self.sink_config['odpsTableName'], input_record)
            pass
        except Exception as e:
            logger.error(e)
            return False

        return True

    def format_records(self, block_records):
        columns_order = self.sink_config['odpsTableColumns'].split(',')
        record = []
        for r in block_records:
            tmp_r = []
            for column_name in columns_order:
                tmp_r.append(r[column_name])
            record.append(tmp_r)
        return record

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
    """
    logger.info('initializing odps sink connect')
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

        if (sink.sink_config['batchOrNot'] == "True") and (sink.sink_config["eventSchema"] == "cloudEvent"):
            logger.info("check batch data with schema: cloudEvent")
            for single_payload in payload:
                if not sink_schema.validate_message_schema(single_payload):
                    logger.error("validate failed error: %s",
                                 Schema(sink_schema.MESSAGE_SCHEMA, ignore_extra_keys=True).validate(single_payload))
                    raise Exception("MESSAGE_SCHEMA validate failed")

        if not sink.is_connected():
            raise Exception("unconnected sink target")

        is_succ = sink.deliver(payload)
        if not is_succ:
            raise Exception("put record to odps failed")

    except Exception as e:
        logger.error(e)
        raise json.dumps({"success": False, "error_message": str(e)})

    return json.dumps({"success": True, "error_message": ""})
