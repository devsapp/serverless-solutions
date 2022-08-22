# -*- coding: utf-8 -*-
import ast
import json
import logging
import re

# 设置日志输出等级, 默认为INFO，可以设置DEBUG进行调试
logger = logging.getLogger()
logger.setLevel(level=logging.INFO)

# 示例对象结构部分内容如下：
# filter_1234满足过滤条件
# {
#     "data": {
#         "body": "TEST",
#         "filter_1234": "filter_key",
#         "topic": "TopicName",
#         "userProperties": {}
#     }
# }


def handler_message(event, context):
    try:
        # 在对message数据清洗之前，先解析获得消息对象
        decode_event = event.decode('utf-8')
        literal_event = ast.literal_eval(repr(decode_event))
        message = json.loads(literal_event)

        # 帮助在日志显示实际进行处理的消息内容
        logger.debug("message: %s" % message)

        # 消息对象以<key, value>形式呈现，根据指定key对消息对象的制定内容进行过滤
        # 模版代码目前只针对key为'data'的部分进行过滤，也可以针对其它key进行过滤
        filter_key = 'data'
        filter_body = message[filter_key]
        if len(filter_body) > 0 and filter(filter_body):
            return message
    except Exception as e:
        logger.error(e)
        return json.dumps({"success": False, "error_message": str(e)})
    return None


# 这里假定data是一个<Key, Value>结构对象，如果存在符合过滤规则的Key，那么就返回该消息
def filter(data):
    # 定义消息过滤规则
    filter_pattern = re.compile(r'([a-z]+)_([0-9]+)', re.I)
    for itemKey in data.keys():
        search_obj = filter_pattern.match(itemKey)
        logger.info("data key: {%s}, value: {%s}" % (
            itemKey, data[itemKey]))
        if search_obj:
            return True
    return False
