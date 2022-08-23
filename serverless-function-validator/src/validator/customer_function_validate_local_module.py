import re

def deal_message(message):
    for keyItem in message.keys():
        if (keyItem == 'value'):
            searchObj = re.search( r'.* hello world .*', message[keyItem], re.M|re.I)
            if searchObj:
                return message
            else:
                return None
    return None

validate_argument={"value": "test hello world Value"}
print(deal_message(validate_argument))
