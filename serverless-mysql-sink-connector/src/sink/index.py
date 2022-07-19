# -*- coding: utf-8 -*-
import json
import logging
import os
import pymysql

from schema import Schema

import sink_schema

logger = logging.getLogger()


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
		self.sink_config = sink_config

		try:
			self.conn = pymysql.connect(
				host=self.sink_config["host"],
				port=self.sink_config["port"],
				user=self.sink_config["user"],
				passwd=self.sink_config["password"],
				db=self.sink_config["database"],
				connect_timeout=5
			)
		except Exception as e:
			logger.error(e)
			logger.error(
				"ERROR: Unexpected error: Could not connect to MySql instance.")
			raise Exception(str(e))

		logger.info("sink target: mysql connected")
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
		self.conn.close()

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
		""" Inner method to write data to mysql instance.

        Args:
            single_data: input data

        Returns:
            SQL execution result

        Raises:
            MysqlException
        """
		sql = "INSERT INTO Data(data) VALUES ('%s') " % (json.dumps(single_data))
		logger.info("exec sql: " + sql)
		with self.conn.cursor() as cursor:
			cursor.execute(sql)
			self.conn.commit()
			result = cursor.fetchall()
			return result

	def deliver(self, payload):
		"""Sink operator.

        Args:
            payload: input payload

        Returns:
            Failed data list

        Raises:
            MysqlException
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
						pass
					failed_data_list.append(single_payload)
					continue
				resp = self._write_data(single_payload)

		else:
			resp = self._write_data(payload)

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
        Exception
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
        None
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

	failed_data_list = []
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
			sink.connect(sink.sink_config)
			logger.error("unconnected sink target. Now reconnected")

		failed_data_list = sink.deliver(payload)

	except Exception as e:
		logger.error(e)
		return json.dumps({"success": False, "error_message": str(e), "failed_data": json.dumps(failed_data_list)})

	return json.dumps({"success": True, "error_message": "", "failed_data": json.dumps(failed_data_list)})
