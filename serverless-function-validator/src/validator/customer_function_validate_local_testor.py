# importing the requests library
#import os
import customer_function_validate_local_module


def handler(event, context):
    # read from event
    message = {"key": "value"}
    print(customer_function_validate_local_module.deal_message(message))

    exeresult = {}

    #exec(open('/tmp/customer_function_validate_local_module.py').read(), globals(), exeresult)
    #exec('/tmp/customer_function_validate_local_module.py', globals(), exeresult)
    #print("result: %s" % exeresult['result'])
    # return repr(exeresult['result'])


handler('', '')
