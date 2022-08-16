# -*- coding: utf-8 -*-
import ast
import json
import logging
import re

logger = logging.getLogger()
logger.setLevel(level=logging.INFO)


def handler_message(event, context):
    try:
        # 数据处理，在对message加工之前，先解析获得消息对象
        decode_event = event.decode('utf-8')
        literal_event = ast.literal_eval(repr(decode_event))
        message = json.loads(literal_event)

        logger.info("message: %s" % message)

        # 数据处理，根据消息对象指定Key的内容进行数据加工
        for key in message.keys():
            logger.info("message key: %s" % key)
            if key == 'data':
                key_value_str = repr(message[key])
                pattern = re.compile(r'([a-z]+) ([a-z]+)', re.I)
                search_obj = pattern.match(key_value_str)
                logger.info("message key: {%s}, value: {%s}" % (
                    key, key_value_str))
                if search_obj:
                    return message
    except Exception as e:
        logger.error(e)
        return json.dumps({"success": False, "error_message": str(e)})
    return json.dumps({"success": True, "error_message": ""})
