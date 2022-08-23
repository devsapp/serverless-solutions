# kafka_ importing the requests library

def deal_message(message, context):
    message["testKeyValidate"] = "testValidate"
    message["testNewValidate"] = "testValidate"

    print("deal message: %s" % message)
    return message
