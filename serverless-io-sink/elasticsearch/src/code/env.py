#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Define the schema, validate the content read from SINK_CONFIG env
ES_SINK_CONFIG_SCHEMA = {
    'host': str,        # ElasticSearch HOST名称
    'port': int,        # ElasticSearch 端口号
    'user': str,        # ElasticSearch 用户名
    'password': str,    # ElasticSearch 用户名对应的密码
    'use_ssl': bool,    # 是否使用 ssl 连接
    'index': str,       # 索引
    'doc_type': str,    # doc 类型
    'id': str,          # 实例 ID
}
