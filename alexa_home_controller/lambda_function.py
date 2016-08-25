from __future__ import print_function

import json
import boto3
import time

APP_ID = ""

LIGHT_INTENTS = [
    "TurnOnLight",
    "TurnOffLight",
    "ChangeLightMode"
]

FAN_INTENTS = [
    "TurnOnFan",
    "TurnOffFan",
    "ChangeFanSpeed",
    "SpeedUpFan",
    "SlowDownFan",
    "ReverseFan"
]

INTENT_ACTION_MAP = {
    "TurnOnLight": "light_all",
    "TurnOffLight": "light_off",
    "TurnOnFan": "fan_low",
    "TurnOffFan": "fan_stop"
}

FAN_COMMAND_MAP = {
    "slow": "fan_low",
    "low": "fan_low",
    "fast": "fan_high",
    "high": "fan_high",
    "medium": "fan_mid",
    "back": "fan_rev",
    "reverse": "fan_rev"
}

iot_client = boto3.client('iot-data', region_name='ap-northeast-1')

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])
    print(event)

    # check application id
    if (event['session']['application']['applicationId'] != APP_ID):
        raise ValueError("Invalid Application ID")

    if event['request']['type'] == "IntentRequest":
        return on_intent(event['request'])
    else:
        return create_help_resopnse()

def on_intent(intent_request):
    print("on_intent")

    # Dispatch skill's intent handlers
    if intent_request['intent']['name'] in LIGHT_INTENTS:
        if light_intent(intent_request['intent']):
            return create_ok_resopnse()
    elif intent_request['intent']['name'] in FAN_INTENTS:
        if fan_intent(intent_request['intent']):
            return create_ok_resopnse()

    return create_help_resopnse()

def light_intent(intent):
    if intent['name'] == "TurnOnLight" or intent['name'] == "TurnOffLight":
        return send_command(INTENT_ACTION_MAP[intent['name']])
    elif intent['name'] == "ChangeLightMode":
        cur_cmd = describe_current_command()
        print(cur_cmd)
        if cur_cmd == "light_all":
            return send_command("light_half_1")
        elif cur_cmd == "light_half_1":
            return send_command("light_half_2")
        elif cur_cmd == "light_half_2":
            return send_command("light_off")
        else:
            return send_command("light_all")
    return False

def fan_intent(intent):

    if intent['name'] == "TurnOnFan" or intent['name'] == "TurnOffFan":
        return send_command(INTENT_ACTION_MAP[intent['name']])
    elif intent['name'] == "ChangeFanSpeed":
        action_type = intent["slots"]["action"]["value"]
        if action_type in FAN_COMMAND_MAP.keys():
            return send_command(FAN_COMMAND_MAP[action_type])
    elif intent['name'] == "SpeedUpFan":
        cur_cmd = describe_current_command()
        if cur_cmd == "fan_low":
            return send_command("fan_mid")
        elif cur_cmd == "fan_mid":
            return send_command("fan_high")
        else:
            return send_command("fan_high")
    elif intent['name'] == "SlowDownFan":
        cur_cmd = describe_current_command()
        if cur_cmd == "fan_high":
            return send_command("fan_mid")
        elif cur_cmd == "fan_mid":
            return send_command("fan_low")
        else:
            return send_command("fan_low")
    elif intent['name'] == "ReverseFan":
        return send_command("fan_rev")
    return False

# --------------- Functions that control the skill's behavior ------------------

def create_help_resopnse():
    """ build help message
    """

    help_message = """
    You can control light and fan with "pi home" keyword.
    Say "tell pi home light on or off" for lights control.
    Say "tell pi home change fan speed slow" for fan control.
    """
    return build_response(build_speechlet_response(
        help_message, help_message))

def create_ok_resopnse():
    """ build OK message
    """

    return build_response(build_speechlet_response(
        "OK", "OK"))

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(output, reprompt_text):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'Pi Home',
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': True
    }


def build_response(speechlet_response):
    return {
        'version': '1.0',
        'response': speechlet_response
    }


def send_command(command):
    shadow = {
        'state': {
            'desired': {
                'command': command,
                'counter': int(time.time())
            }
        }
    }
    payload = json.dumps(shadow)

    response = iot_client.update_thing_shadow(
        thingName='alexa_home',
        payload= payload
    )
    return True

def describe_current_command():
    response = iot_client.get_thing_shadow(
        thingName='alexa_home'
    )
    streamingBody = response["payload"]
    jsonState = json.loads(streamingBody.read())
    print(jsonState)
    return jsonState['state']['desired']['command']
