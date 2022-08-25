# -*- coding: utf-8 -*-
import ast
import base64
import json
import logging
import sys
from os.path import dirname

logger = logging.getLogger()
logger.setLevel(level=logging.INFO)
#
# To enable the initializer feature (https://help.aliyun.com/document_detail/158208.html)
# please implement the initializer function as below：


def initializer(context):
    logger.info('initializing')


def handler(event, context):
    logger.info('hello world')
    print("context: %s" % context)
    print("event: %s" % event)
    response_json = event.decode('utf-8')
    dataform = ast.literal_eval(repr(response_json))
    message = json.loads(dataform)

    validate_scenario = message['validate_scenario']
    validate_account_id = message['validate_account_id']
    validate_argument = message['validate_argument']
    validate_code_encode = message['validate_code']
    validate_handler = message['validate_handler']
    print("encode: %s" % validate_code_encode)
    validate_code = base64.b64decode(validate_code_encode)
    print("decode: %s" % validate_code)

    logger.info('validate_scenario: {%s}, account_id: {%s}, validate_message: {%s}' % (
        validate_scenario, validate_account_id, message))
    validate_module = 'customer_function_validate_module'
    validate_module_path = '/tmp/{}.py'.format(validate_module)

    with open(validate_module_path, 'wb') as writer:
        writer.write(validate_code)
    sys.path.append(dirname(validate_module_path))

    # execute user code for check syntax and validate result
    validate_framework_bytecode = 'import sys\nimport traceback\nfrom importlib import reload\n\nimport {}\n\ntry:\n    validate_module = reload({})\n    result = validate_module.{}({}, {})\nexcept:\n    result = traceback.format_exception(*sys.exc_info())'.format(
        validate_module, validate_module,
        validate_handler,
        validate_argument, '{}')
    print("validate_entry:\n%s" % validate_framework_bytecode)

    execresult = {}
    exec(validate_framework_bytecode, globals(), execresult)
    print("result: %s" % execresult['result'])
    sys.modules.pop(validate_module)
    return repr(execresult)
