# -*- coding: utf-8 -*-
import ast
import json
import logging
import re

# 设置日志输出等级, 默认为INFO，可以设置DEBUG进行调试
logger = logging.getLogger()
logger.setLevel(level=logging.INFO)


def handle_message(event, context):
    try:
        # 在对message数据清洗之前，先解析获得消息对象
        decode_event = event.decode('utf-8')
        literal_event = ast.literal_eval(repr(decode_event))
        message = json.loads(literal_event)

        # 帮助在日志显示实际进行处理的消息内容
        logger.debug("message: %s" % message)

        # 消息对象以<key, value>形式呈现，根据指定key对消息对象的指定内容进行富化处理
        # 模版代码目前只针对key为'data'的内容进行富化处理，也可以针对其它key进行富化处理
        transform_key = 'data'
        transform_body = message[transform_key]
        if len(transform_body) > 0:
            message[transform_key] = transform(transform_body)
    except Exception as e:
        logger.error(e)
        return json.dumps({"success": False, "error_message": str(e)})
    return message

# 示例对象结构部分内容如下：
# {
#     "data": {
#         "test1": "xxx",
#         "test2": "xxx"
#     }
# }
# {
#     "data": {
#         "test1": "xxx_enrich_new_surfix",
#         "test2": "enrich_new_prefix_xxx",
#     }
# }
# 这里假定data是一个<Key, Value>结构对象，如果存在符合过滤规则的Key，那么就返回该消息
# 对消息的data部分进行富化处理，在原来内容的基础上增加新的内容
# 这些内容可以来自于数据库或者OSS对象存储，也可以来调用外部API获得富化数据


def transform(data):
    # 当前代码示例针对data按照字典（dict）对象进行处理; 可以根据实际的数据结构定义处理逻辑
    if not isinstance(data, dict):
        return data
    for itemKey in data.keys():
        if itemKey == 'test1':
            data[itemKey] = data[itemKey] + "_enrich_new_surfix"
        elif itemKey == 'test2':
            data[itemKey] = "enrich_new_prefix_" + data[itemKey]
    return data
