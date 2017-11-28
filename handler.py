import json
import datetime
import os
from imaplib.scan import CamImageScanner

def endpoint(event, context):
    current_time = datetime.datetime.now().time()
    body = {
        "message": "Hello, the current time is " + str(current_time) + 'pid: '+ str(os.getpid())
    }
    s = CamImageScanner('images/bill1.jpg', 'images/xx.jpg')
    result = s.processImage()
    print(result)
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response
