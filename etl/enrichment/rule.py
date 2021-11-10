#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import schema
from schema import Schema


class EnrichmentRule:
    def __init__(self):
        # enrichment_schema is used to validate messages.
        # todo: move to layer
        """
        field: pk in db, 对于数据库采用单主键
        output_fields: 取出的字段，拼接到 value 中
        missing: 源中缺失时默认填充值
        mode:
            fill	当目标字段不存在或者值为空时，设置目标字段。
            fill-auto	当新值非空，且目标字段不存在或者值为空时，设置目标字段。
            add	当目标字段不存在时，设置目标字段。
            add-auto	当新值非空，且目标字段不存在时，设置目标字段。
            overwrite	总是设置目标字段。
            overwrite-auto	当新值非空，设置目标字段。
        """
        self.enrichment_schema = {
            'field': str,
            'output_fields': [str],
            'missing': str,
            'mode': str
        }
        self.rule = ""

    def set_rule(self, rule_str):
        try:
            Schema(self.enrichment_schema, ignore_extra_keys=True).validate(rule_str)
        except schema.SchemaError:
            return False
        else:

            self.rule = json.loads(rule_str)

            return True

    # 这里可以对消息进行处理后返回
    def deal_message(message, remote_record):
        # todo
        return message

