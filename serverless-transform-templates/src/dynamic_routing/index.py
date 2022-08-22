# -*- coding: utf-8 -*-
import ast
import copy
import json
import logging

# 设置日志输出等级, 默认为INFO，可以设置DEBUG进行调试
logger = logging.getLogger()
logger.setLevel(level=logging.INFO)


def handler_message(event, context):
    transform_messages = []
    try:
        # 在对message数据清洗之前，先解析获得消息对象
        decode_event = event.decode('utf-8')
        literal_event = ast.literal_eval(repr(decode_event))
        message = json.loads(literal_event)

        # 帮助在日志显示实际进行处理的消息内容
        logger.debug("message: %s" % message)

        # 消息对象以<key, value>形式呈现，根据指定key对消息对象的指定内容进行分割处理
        # 模版代码目前只针对key为'data'的内容进行分割，也可以针对其它key进行分割处理
        transform_key = 'data'
        transform_body = message[transform_key]
        result = dynamic_routing(transform_body)
    except Exception as e:
        logger.error(e)
        return json.dumps({"success": False, "error_message": str(e)})
    return json.dumps({"success": True, "error_message": str(result)})

# 示例对象结构部分内容如下：
# {
#     "data": "1234348234234|19228143033|310-12345560813-6789"
# }
# 针对分割场景这里假定data是一个字符串类型的对象


def dynamic_routing(data):
    split_dataset = []
    # 定义数据分隔符
    delimiter = '|'

    # 对data部分数据按照分隔符进行分割，注意分隔后的内容会进行strip操作
    split_parts = data.split(delimiter)
    for part in split_parts:
        if len(part) == 0 or len(part.strip()) == 0:
            continue
        # dynamic routing the data to different topic
        logger.info(
            "dynamic routing the message {%s} to topic: {%s}" % (part, "xxx"))
    return ""
