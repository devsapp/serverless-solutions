# importing the requests library

def deal_message(message):
    message["testKeyValidate"] = "testValidate"
    print("deal message: %s" % message)
    return message
