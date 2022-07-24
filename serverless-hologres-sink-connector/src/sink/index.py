# -*- coding: utf-8 -*-
import json
import logging
import os

from schema import Schema
from retrying import retry

import psycopg2
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


def retry_if_psql_exception(exception):
    """Whether the exception needs to be retried.

    Args:
        exception - exception raised by deliver method

    Returns:
        Whether it is necessary to retry

    Raises:
        None
    """
    return isinstance(exception, psycopg2.Error)

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
            psycopg2.OperationalError
            Exception
        """
        primary_keys_name = sink_config['primaryKeysName']
        colsName = sink_config['colsName']
        self.sink_config = sink_config
        self.sink_config['primaryKeysName'] = [] if (primary_keys_name.strip() == '') else primary_keys_name.split(',')
        self.sink_config['colsName'] = [] if (colsName.strip() == '') else colsName.split(',')
        self.sink_config['port'] = int(sink_config['port'])
        try:
            self.conn = psycopg2.connect(host=self.sink_config['host'],
                                         port=self.sink_config['port'],
                                         dbname=self.sink_config['database'],
                                         user=self.sink_config['user'],
                                         password=self.sink_config['password'],
                                         application_name=self.sink_config['context'])
            self.connected = True
        except psycopg2.OperationalError as pe:
            logger.error(pe)
            logger.error(
                "ERROR: psycopg2 OperationalError: Could not connect to Hologres instance.")
            raise pe
        except Exception as e:
            logger.error(e)
            logger.error(
                "ERROR: unknown Error: Could not connect to Hologres instance.")
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

    @retry(stop_max_attempt_number=default_retry_times, wait_exponential_multiplier=1000,
           retry_on_result=result_need_retry, retry_on_exception=retry_if_psql_exception)
    def deliver(self, payload):
        """Sink operator.
            deliver data to hologres

        Args:
            payload: input payload

        Returns:
            None

        Raises:
            psycopg2.OperationalError
            Exception
        """

        data_list = []
        if self.sink_config['batchOrNot'] == "True":
            for single_payload in payload:
                data_list.append(single_payload['data'])
        else:
            data_list.append(payload['data'])
        try:
            deliver_success = self._write_data(data_list)
            return deliver_success
        except psycopg2.Error as pe:
            logger.error(pe)
            logger.error(
                "ERROR: psycopg2 Error: write data to Hologres table: %s failed." % self.sink_config['tableName'])
            raise pe
        except Exception as e:
            logger.error(e)
            logger.error(
                "ERROR: unknown error: write data to Hologres table: %s failed." % self.sink_config['tableName'])
            raise e


    def _write_data(self, data_list):
        """Inner method to write data to hologres instance.

        Args:
            data_list: input data list

        Returns:

        Raises:
            psycopg2.OperationalError
            Exception
        """
        primary_keys_name = self.sink_config['primaryKeysName']
        cols_name = self.sink_config['colsName']
        table_name = self.sink_config['tableName']
        idx = 0

        # Generate fields: (field1,field2,...)
        fields = "("
        for key in primary_keys_name:
            if idx == 0:
                fields = fields + "%s" % key
            else:
                fields = fields + ',%s' % key
            idx = idx + 1
        for col in cols_name:
            if idx == 0:
                fields = fields + "%s" % col
            else:
                fields = fields + ',%s' % col
            idx = idx + 1
        fields = fields + ')'

        logger.info("fields: " + fields)
        # Generate values: (val1,val2),(val3,val4)
        values = ""
        values_list = []
        for data in data_list:
            value = "("
            idx = 0
            for key in primary_keys_name:
                v = data[key]
                if idx == 0:
                    if isinstance(v, str):
                        value = value + ("'%s'" % str(v))
                    else:
                        value = value + ("%s" % str(v))
                else:
                    if isinstance(v, str):
                        value = value + (",'%s'" % str(v))
                    else:
                        value = value + (",%s" % str(v))
                idx = idx + 1
            for col in cols_name:
                v = data[col]
                if idx == 0:
                    if isinstance(v, str):
                        value = value + ("'%s'" % str(v))
                    else:
                        value = value + ("%s" % str(v))
                else:
                    if isinstance(v, str):
                        value = value + (",'%s'" % str(v))
                    else:
                        value = value + (",%s" % str(v))
                idx = idx + 1

            value = value + ')'
            values_list.append(value)

        idx = 0

        for v in values_list:
            if idx == 0:
                values = values + "%s" % v
            else:
                values = values + ",%s" % v
            idx = idx + 1
        logger.info("values: " + values)

        insert_sql = "INSERT INTO %s%s VALUES %s" % (table_name, fields, values)
        select_sql = "SELECT * FROM %s" % table_name
        logger.info("exec sql: " + insert_sql)
        with self.conn.cursor() as cursor:
            cursor.execute(insert_sql)
            self.conn.commit()

            cursor.execute(select_sql)
            result = cursor.fetchall()
            if not result:
                logger.error("fetch none result")
                return False

            logger.info("fetch result: " + str(result))
            cursor.close()
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
    creds = context.credentials
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
        raise Exception("Fail to write hologress.")


    return "success"
