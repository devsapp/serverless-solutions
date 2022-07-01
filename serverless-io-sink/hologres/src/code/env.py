#!/usr/bin/env python
# -*- coding: utf-8 -*-

# The original string value for SINK_CONFIG env
# {"host":"xxx","database":"access_test","user":"xxx","password":"xxx","port":80}

# The json representation for SINK_CONFIG env
# SINK_CONFIG = {
#     'context': 'xxx',
#     'host': 'xxxx',
#     'database': 'access_test',
#     'user': 'xxx',
#     'password': 'xxx',
#     'port': 80
# }

# Define the schema, validate the content read from SINK_CONFIG env
HOLOGRES_SINK_CONFIG_SCHEMA = {
    'context': str,
    'host': str,        # Hologres HOST名称
    'port': int,        # Hologres 端口号
    'database': str,    # Hologres 数据库名称
    'user': int,        # Hologres 用户名
    'password': str,    # Hologres 用户名对应的密码
}
