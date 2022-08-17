# -*- coding: utf-8 -*-
import ast
import copy
import json
import logging
import re

logger = logging.getLogger()
logger.setLevel(level=logging.INFO)


def handler_message(event, context):
    try:
        # 在对message数据清洗之前，先解析获得消息对象
        decode_event = event.decode('utf-8')
        literal_event = ast.literal_eval(repr(decode_event))
        message = json.loads(literal_event)

        logger.info("message: %s" % message)

        # 定义消息分隔符
        delimiter = "xxxx"

        splited_messages = []
        # 消息对象以<key, value>形式呈现，根据指定key对消息对象的制定内容进行过滤
        # 模版代码目前只针对key为'data'的部分进行过滤，也可以针对其它key进行过滤
        for key in message.keys():
            logger.info("message key: %s" % key)
            if key == 'data':
                key_value_str = repr(message[key])
                for split_value in key_value_str.split(delimiter):
                    if len(split_value) == 0:
                        continue
                    new_message = copy.deepcopy(message)
                    new_message[key] = split_value
                    splited_messages.append(new_message)
        if len(splited_messages) == 0:
            splited_messages.append(message)
    except Exception as e:
        logger.error(e)
        return json.dumps({"success": False, "error_message": str(e)})
    return splited_messages
