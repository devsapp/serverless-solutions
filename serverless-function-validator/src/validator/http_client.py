# importing the requests library
import base64

import requests

# defining the api-endpoint
API_ENDPOINT = "http://127.0.0.1:8080/"

# your API key here
VALIDATE_KEY = "kafka_etl_pythob_validator"

handler = 'deal_message'
runtime = 'python3'
message = '{"testKey": "testValue"}'
source_code = ""
with open('customer_function_example.py', 'rb') as reader:
    source_code = reader.read()

source_code_enc = base64.b64encode(source_code)
source_code_enc_str = str(source_code_enc, 'utf-8')

print("Source code is: %s, %s, %s" %
      (source_code, source_code_enc, source_code_enc_str))

# data to be sent to api
data = {'validate_option': '{"action": "validate"}',
        'validate_handler': handler,
        'validate_argument': message,
        'validate_code_language': runtime,
        'validate_code': source_code_enc_str}

print("Request data is: %s" % data)

headers = {'Content-Type': 'application/json'}
r = requests.post(url=API_ENDPOINT, json=data, headers=headers)

# extracting response text
print("The validate result is: %s" % r.text)
