# -*- coding: utf-8 -*-
import json
import logging
import os

import clickhouse_driver
import jinja2
from schema import Schema

from env import CLICK_HOUSE_SINK_CONFIG_SCHEMA

logger = logging.getLogger()


class ClickHouseSink(object):

    def __init__(self, clickhouse_url, exec_sql):
        # for example
        # clickhouse://[user:password]@localhost:9000/default
        # clickhouses://[user:password]@localhost:9440/default
        self.connect_url = clickhouse_url
        try:
            self.clickhouse_client = clickhouse_driver.Client.from_url(clickhouse_url)
        except Exception as e:
            logger.error(e)
            logger.error(
                "ERROR: Unexpected error: Could not create a clickhouse_client from %s", clickhouse_url)
            raise Exception(str(e))
        self.exec_sql = exec_sql

    def produce_to_clickhouse(self, data):
        if len(data) == 0:
            logger.warning("skip insert into clickhouse for empty data")
            return True
        try:
            self.clickhouse_client.execute(self.exec_sql, data)
        except Exception as e:
            logger.error(e)
            logger.error("ERROR: Unexpect error while produce message to clickhouse")
            return False
        return True


def initializer(context):
    clickhouse_full_url = os.environ.get('clickhouse_full_url')
    template_sql = os.environ.get('template_sql')
    sink_config_str = json.dumps({'clickhouse_full_url': clickhouse_full_url, 'template_sql': template_sql})
    sink_config = json.loads(sink_config_str)

    if not Schema(CLICK_HOUSE_SINK_CONFIG_SCHEMA, ignore_extra_keys=True).is_valid(sink_config):
        logger.error("validate failed error: %s", Schema(CLICK_HOUSE_SINK_CONFIG_SCHEMA, ignore_extra_keys=True).validate(sink_config))
        raise Exception("SINK_CONFIG validate failed")
    global clickhouse_sink
    clickhouse_sink = ClickHouseSink(clickhouse_full_url, template_sql)


def handler(event, context):
    # processing data
    evt = json.loads(event)
    print("handler event: ", evt)
    success = clickhouse_sink.produce_to_clickhouse(evt)
    return {"success": success}
