# -*- coding: utf-8 -*-
import ast
import copy
import json
import logging

# 设置日志输出等级, 默认为INFO，可以设置DEBUG进行调试
logger = logging.getLogger()
logger.setLevel(level=logging.INFO)


def handle_message(event, context):
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
        transform_body_array = []
        if len(transform_body) > 0:
            transform_body_array = transform(transform_body)

        for transform_body in transform_body_array:
            if len(transform_body) == 0:
                continue
            transform_message = copy.deepcopy(message)
            transform_message[transform_key] = transform_body
            transform_messages.append(transform_message)
        if len(transform_messages) == 0:
            transform_messages.append(message)
    except Exception as e:
        logger.error(e)
        return json.dumps({"success": False, "error_message": str(e)})
    return transform_messages

# 示例对象结构部分内容如下：
# {
#     "data": "1234348234234|19228143033|310-12345560813-6789"
# }
# 针对分割场景这里假定data是一个字符串类型的对象


def transform(data):
    split_dataset = []
    # 定义数据分隔符
    delimiter = '|'

    # 当前代码示例针对data按照字符串进行处理; 可以根据实际的数据结构定义处理逻辑
    data = str(data)

    # 对data部分数据按照分隔符进行分割，注意分隔后的内容会进行strip操作
    split_parts = data.split(delimiter)
    for part in split_parts:
        if len(part) == 0 or len(part.strip()) == 0:
            continue
        split_dataset.append(part.strip())
    return split_dataset
