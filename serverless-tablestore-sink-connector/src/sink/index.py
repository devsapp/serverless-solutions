# -*- coding: utf-8 -*-
import json
import logging
import os

from schema import Schema
from tablestore import BatchWriteRowRequest
from tablestore import Condition
from tablestore import OTSClient
from tablestore import PutRowItem
from tablestore import Row
from tablestore import RowExistenceExpectation
from tablestore import TableInBatchWriteRowItem
from retrying import retry

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


    def connect(self, sink_config, access_key_id, access_key_secret, security_token):
        """Sink connector construct method.
            todo: User should realize this method

        Args:
            sink_config: config of this sink connector
            access_key_id: access key id
            access_key_secret: access key secret
            security_token: security token
        Returns:
            None

        Raises:
            None
        """
        primary_keys_name = sink_config['primaryKeysName']
        rows_name = sink_config['colsName']
        self.sink_config = sink_config
        self.sink_config['primaryKeysName'] = primary_keys_name.split(',')
        self.sink_config['colsName'] = rows_name.split(',')

        try:
            try:
                security_token
            except NameError:
                # security_token is undefined
                self.client = OTSClient(end_point=self.sink_config['endpoint'],
                                        access_key_id=access_key_id,
                                        access_key_secret=access_key_secret,
                                        instance_name=self.sink_config['instanceName'],
                                        socket_timeout=20)
            else:
                self.client = OTSClient(end_point=self.sink_config['endpoint'],
                                        access_key_id=access_key_id,
                                        access_key_secret=access_key_secret,
                                        instance_name=self.sink_config['instanceName'],
                                        sts_token=security_token, socket_timeout=20)
            self.connected = True
        except Exception as e:
            logger.error(e)
            logger.error(
                "ERROR: Unexpected error: Could not connect to Tablestore instance.")
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

    @retry(stop_max_attempt_number=default_retry_times, wait_exponential_multiplier=1000, retry_on_result=result_need_retry)
    def deliver(self, payload):
        """Sink operator.
            deliver data to ots

        Args:
            payload: input payload

        Returns:
            success flag

        Raises:
            Exception
        """
        try:
            data_list = []
            if self.sink_config['batchOrNot'] == "True":
                for single_payload in payload:
                    data_list.append(single_payload['data'])
            else:
                data_list.append(payload['data'])

            put_row_items = self._get_row(data_list)

            # batch write data list into table
            table_name = self.sink_config['tableName']
            req = BatchWriteRowRequest()
            req.add(TableInBatchWriteRowItem(table_name, put_row_items))
            resp = self.client.batch_write_row(req)
            succeed_items, failed_items = resp.get_put()

            for item in failed_items:
                logger.error('Put item failed, error code: %s, error message: %s' % (item.error_code, item.error_message))
            return resp.is_all_succeed()
        except Exception as e:
            logger.error('deliver failed due to exception: ' + str(e))
            return false

    def _get_row(self, data_list):
        """Inner method to get tablestore put row.

        Args:
            data_list: data list

        Returns:
            put_row_items: tablestore put row items
        Raises:
            None
        """
        put_row_items = []
        for data in data_list:
            pks = []
            cols = []
            primary_keys_name = self.sink_config['primaryKeysName']
            rows_name = self.sink_config['colsName']
            for key in primary_keys_name:
                logger.info("primary key: %s, value %s", key, data[key])
                pks.append((key, data[key]))
            for row in rows_name:
                logger.info("row name: %s, value: %s", row, data[row])
                cols.append((row, data[row]))

            row = Row(pks, cols)
            condition = Condition(RowExistenceExpectation.IGNORE)
            item = PutRowItem(row, condition)
            put_row_items.append(item)
        return put_row_items


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
    creds = context.credentials
    sink_config_env = os.environ.get('SINK_CONFIG')
    sink_config = json.loads(sink_config_env)
    if not sink_schema.validate_sink_config_schema(sink_config):
        logger.error("validate failed error: %s",
                     Schema(sink_schema.SINK_CONFIG_SCHEMA, ignore_extra_keys=True).validate(sink_config))
        raise Exception("SINK_CONFIG_SCHEMA validate failed")


    sink.connect(sink_config, creds.access_key_id, creds.access_key_secret, creds.security_token)


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

        is_succ = sink.deliver(payload)
        if is_succ is False:
            return json.dumps({"success": False, "error_message": "sink to ots failed."})

    except Exception as e:
        logger.error(e)
        return json.dumps({"success": False, "error_message": str(e)})

    return json.dumps({"success": True, "error_message": ""})
