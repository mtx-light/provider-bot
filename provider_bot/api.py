from flask import Flask, request, jsonify
from provider_bot.__init__ import app
from mindmeld.components.dialogue import Conversation
from provider_bot.bot_db import create_database

api = Flask(__name__)
conversation = Conversation(app=app, context={'username': 'inmost_light'})


def simplify_entity(e):
    if e is None:
        return None
    if e['type'] == 'sys_time':
        if e['role'] == 'day':
            return str(e['value'][0]['value'])[:10]
        if e['role'] == 'hour':
            return str(e['value'][0]['value'])[11:16]
        else:
            raise NotImplementedError('Unknown sys_time role')
    if e['type'] == 'service_plan':
        return e['value'][0]['cname']
    if e['type'] == 'sys_number':
        return e['value'][0]['value']
    else:
        raise NotImplementedError('Unknown entity type')

def get_entity(entities, e_type, role=None):
    for e in entities:
        if (e['type'] == e_type) and ((not role) or (e['role'] == role)):
            if e['type'] == 'sys_time':
                if e['role'] == 'day':
                    return str(e['value'][0]['value'])[:10]
                if e['role'] == 'hour':
                    return str(e['value'][0]['value'])[11:16]
            if e['type'] == 'sys_number':
                return e['value'][0]['value']
            return e['value'][0]['cname']
    return None

@api.route('/api',methods = ['POST'])
def endpoint():
    message = request.json['message']
    conversation.say(message)
    history = conversation.history
    entities = history[0]['request']['entities']

    return jsonify({"intent": history[0]['request']['intent'],
                    "e_day": get_entity(entities, 'sys_time', 'day'),
                    "e_hour": get_entity(entities, 'sys_time', 'hour'),
                    "e_house_number": get_entity(entities, 'sys_number', 'house_number'),
                    "e_service_number": get_entity(entities, 'sys_number', 'service_number'),
                    "e_service_plan": get_entity(entities, 'service_plan')})


api.run(host= '0.0.0.0',debug=True)