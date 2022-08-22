# -*- coding: utf-8 -*-
import ast
import json
import logging
import re

# 设置日志输出等级, 默认为INFO，可以设置DEBUG进行调试
logger = logging.getLogger()
logger.setLevel(level=logging.INFO)


def handler_message(event, context):
    try:
        # 在对message数据清洗之前，先解析获得消息对象
        decode_event = event.decode('utf-8')
        literal_event = ast.literal_eval(repr(decode_event))
        message = json.loads(literal_event)

        # 帮助在日志显示实际进行处理的消息内容
        logger.debug("message: %s" % message)

        # 消息对象以<key, value>形式呈现，根据指定key对消息对象的指定内容进行投影处理
        # 模版代码目前只针对key为'data'的内容部分信息进行投影处理，也可以针对其它key进行同样的操作
        transform_key = 'data'
        transform_body = message[transform_key]
        if len(transform_body) > 0:
            message[transform_key] = transform(transform_body)
    except Exception as e:
        logger.error(e)
        return json.dumps({"success": False, "error_message": str(e)})
    return message


def projection(matched):
    logger.info("projection matched: {%s}" % (matched))

# 示例对象结构部分内容如下：
# {
#     "data": [
#         "John Smith, 19228143033, 310-12345560813-6789",
#         "Jane Doe, 18228147085, 610-12345560813-7890"
#     ]
# }

# 这里假定data是一个Array类型的对象，如果存在符合过滤规则的Key，那么就返回该消息


def transform(data):
    new_dataset = []
    # 定义数据分隔符
    delimiter = ","

    # 定义指定字段提取模式
    phone_extract_pattern = re.compile(r'^(\d{3})(\d{4})(\d{4})$', re.I)
    id_extract_pattern = re.compile(r'^(\d{3})-(\d{11})-(\d{4})$', re.I)
    for item in data:
        logger.info("data item: '%s'" % (item))
        item_values = item.split(delimiter)
        new_values = []
        for value in item_values:
            value = value.strip()
            value = re.sub(phone_extract_pattern, r'\1****\3', value)
            value = re.sub(id_extract_pattern, r'\1-***-\3', value)
            new_values.append(value)
        logger.info("new item: '%s'" % (new_values))
        new_dataset.append(", ".join(new_values))
    logger.info("new data: '%s'" % (new_dataset))
    return data
