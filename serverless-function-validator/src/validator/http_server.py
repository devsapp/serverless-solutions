# Python 3 server example
import ast
import base64
import json
import logging
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from os.path import dirname

hostName = "localhost"
serverPort = 8080


logger = logging.getLogger()
logger.setLevel(level=logging.INFO)


class MyServer(BaseHTTPRequestHandler):
    def do_POST(self):
        # read the message and convert it into a python dictionary
        length = int(self.headers['content-length'])
        response_json = self.rfile.read(length).decode('utf-8')
        dataform = ast.literal_eval(repr(response_json))
        message = json.loads(dataform)

        # add a property to the object, just to mess with data
        message['received'] = 'ok'
        print("received test data length: %s" % message)

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
        validate_module_path = '{}.py'.format(validate_module)

        validate_framework = 'customer_function_validate_framework'
        validate_framework_path = '{}.py'.format(
            validate_framework)

        with open(validate_module_path, 'wb') as writer:
            writer.write(validate_code)
        sys.path.append(dirname(validate_module_path))

        # execute user code for check syntax and validate result
        validate_framework_bytecode = 'import sys\nimport traceback\nfrom importlib import reload\n\nimport {}\n\ntry:\n    validate_module = reload({})\n    result = validate_module.{}({}, {})\nexcept:\n    result = traceback.format_exception(*sys.exc_info())'.format(
            validate_module, validate_module, validate_handler, validate_argument, '{}')
        print("validate_framework_bytecode:\n%s" % validate_framework_bytecode)

        with open(validate_framework_path, 'wb') as writer:
            writer.write(bytes(validate_framework_bytecode, "utf-8"))

        execresult = {}
        exec(validate_framework_bytecode, globals(), execresult)
        print("result: %s" % execresult['result'])
        sys.modules.pop(validate_module)

        self.send_response(201)
        self.end_headers()
        self.wfile.write(bytes(repr(execresult), "utf-8"))


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
