# -*- coding: utf-8 -*-
import json
import logging
import os
import numpy

from schema import Schema
from retrying import retry

import sink_schema
from elasticsearch import Elasticsearch
from elasticsearch import ElasticsearchException

logger = logging.getLogger()
default_retry_times = 3


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

    def result_need_retry(result):
        """if the result needes to be retried.

        Args:
            result: array, list of failed data

        Returns:
            Bool, if result == True, return False otherwise return True

        Raises:
            None
        """
        if numpy.size(result) > 0:
            return True
        else:
            return False

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
        self.sink_config = sink_config

        try:
            es_use_ssl = False
            if self.sink_config['esUseSsl'] == "True":
                es_use_ssl = True

            self.es = Elasticsearch(
                [self.sink_config['esHost']],
                http_auth=(self.sink_config['esUser'], self.sink_config['esPassword']),
                port=self.sink_config['esPort'],
                use_ssl=es_use_ssl
            )
            self.connected = True
            return
        except Exception as e:
            logger.error(e)
            logger.error(
                "ERROR: Unexpected error: Could not connect to elastic search instance.")
            raise Exception(str(e))
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

    def _write_data(self, single_data):
        """ Inner method to write data to elastic search instance.

         Args:
             single_data: input data

         Returns:
             Elastic search execution result

         Raises:
             Elastic search Exception
         """
        data = single_data['data']
        es_id = single_data['id']
        resp = self.es.index(index=self.sink_config['esIndex'], doc_type=self.sink_config['esDocType'],id=es_id,
                      body=data)
        logger.info('Insert data into elastic search index %s id %s with response : %s', self.sink_config['esIndex'], es_id, str(resp))

    @retry(stop_max_attempt_number=default_retry_times, wait_exponential_multiplier=1000, retry_on_result=result_need_retry)
    def deliver(self, payload):
        """Sink operator.
            todo: User should realize this method

        Args:
            payload: input payload
            todo: xx

        Returns:
            None

        Raises:
            todo: xx
        """
        failed_data_list = []
        if sink.sink_config['batchOrNot'] == "True":
            for single_payload in payload:
                if not sink_schema.validate_message_schema(single_payload):
                    try:
                        logger.error("validate failed error: %s",
                                     Schema(sink_schema.MESSAGE_SCHEMA, ignore_extra_keys=True).validate(
                                         single_payload))
                    except Exception as e:
                        logger.error("see Exception during data validation: %s", str(e))
                        raise Exception(e)
                    failed_data_list.append(single_payload)
                    continue
                try:
                    resp = self._write_data(single_payload)
                except ElasticsearchException as es_error:
                    logger.error('see Elastic Exception during data sinking: %s', str(es_error))
                    failed_data_list.append(single_payload)
                    pass
        else:
            try:
                resp = self._write_data(payload)
            except ElasticsearchException as es_error:
                logger.error('see elastic exception during data sinking: %s', str(es_error))
                failed_data_list.append(payload)
                pass

        return failed_data_list


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
    failed_data = []
    try:

        payload = json.loads(event)
        # only single data type is validated here.
        if sink.sink_config['batchOrNot'] == "False" and sink.sink_config["dataSchema"] == "cloudEvent":
            logger.info("check single data with schema: cloudEvent")
            if not sink_schema.validate_message_schema(payload):
                logger.error("validate failed error: %s",
                             Schema(sink_schema.MESSAGE_SCHEMA, ignore_extra_keys=True).validate(payload))
                raise Exception("MESSAGE_SCHEMA validate failed")

        if not sink.is_connected():
            raise Exception("unconnected sink target")

        failed_data = sink.deliver(payload)

    except Exception as e:
        logger.error("failed to deliver data into elastic search due to exception: %s", str(e))
        raise Exception(e)

    if numpy.size(failed_data) > 0:
        raise Exception("failed to deliver data into elastic search with listed ones %s", str(failed_data))
    return json.dumps({"success": True, "error_message": ""})