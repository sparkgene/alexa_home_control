from __future__ import print_function

import json
import boto3
import time

print('Loading function')


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    client = boto3.client('iot-data', region_name='ap-northeast-1')

#    response = client.get_thing_shadow(
#        thingName='alexa_home'
#    )
#    streamingBody = response["payload"]
#    jsonState = json.loads(streamingBody.read())
#    print(jsonState)

    shadow = {
        'state': {
            'desired': {
                'command': 'light_off',
                'counter': int(time.time())
            }
        }
    }
    payload = json.dumps(shadow)
    response = client.update_thing_shadow(
        thingName='alexa_home',
        payload= payload
    )

    return True
