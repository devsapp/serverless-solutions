import sys
import traceback
from importlib import reload

import customer_function_validate_local_module

try:
    customer_function_validate_module = reload(
        customer_function_validate_local_module)
    result = customer_function_validate_module.deal_message(
        {"testKey": "testValue"})
except:
    result = traceback.format_exception(*sys.exc_info())
