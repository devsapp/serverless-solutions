#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from schema import Schema

# MESSAGE_SCHEMA is used to validate messages.
MESSAGE_SCHEMA = {
    'id': str,
    'source': str,
    'specversion': str,
    'type': str,
    'datacontenttype': str,
    'time': str,
    'subject': str,
    'aliyunaccountid': str,
    #'data': data is user define,
}

# CONFIG_SCHEMA is used to validate transform config.
CONFIG_SCHEMA = {
    'sink_service_name': str,
    'sink_function_name': str,
    'dataSchema': str,
    'messageType': str,
}


def validate_message_schema(message):
    """validate input message according to Message_SCHEMA.

    Args:
        message: Origin message in cloud events schema from event bridge.

    Returns:
        message: Whether message is validated.

    Raises:
        None.
    """
    return Schema(MESSAGE_SCHEMA, ignore_extra_keys=True).is_valid(message)


def validate_transform_config_schema(config):
    """validate input message according to Message_SCHEMA.

    Args:
        message: Origin message in cloud events schema from event bridge.

    Returns:
        bool: Whether the config is validated.

    Raises:
        None.
    """
    return Schema(CONFIG_SCHEMA, ignore_extra_keys=True).is_valid(config)