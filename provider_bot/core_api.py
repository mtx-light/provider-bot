from collections import deque
from langdetect import detect
from flask import Flask, request, jsonify
from mindmeld.components.dialogue import Conversation
from provider_bot.__init__ import app
from provider_bot.utils.aggressive import is_aggressive

LANGUAGE_CHAIN_LENGTH = 2  # TODO: Get this from settings file

conversations = {}

api = Flask(__name__)


def is_user_confirm(message):
    return app.app_manager.nlp.domains['internet'].intent_classifier.predict(message) == 'confirmation'


@api.route('/send', methods=['POST'])
def send():
    request_body = request.get_json()
    session_id = request_body['session_id']

    if not request_body['session_id'] in conversations:
        user_data = {'username': session_id,  # TODO: Need get real name
                     'language': 'uk',
                     'detected_languages': deque(maxlen=LANGUAGE_CHAIN_LENGTH),
                     'language_confirmed': False,
                     'message_without_response': None,
                     'suggest_change_language': False,
                     'aggressive_met': False}
        conversation = Conversation(app=app, context=user_data)
        conversations[session_id] = {'conversation': conversation,
                                     'data': user_data}

    conversation, data = conversations[session_id]['conversation'], conversations[session_id]['data']
    message = request_body['message']

    detected_languages = data['detected_languages']
    lang = detect(message)
    detected_languages.append(lang)

    if data.get('suggest_change_language'):
        change_lang = is_user_confirm(message)
        if change_lang:
            data['language'] = detected_languages[0]
        data['language_confirmed'] = True
        message = data['message_without_response']
        data['message_without_response'] = None
        data['suggest_change_language'] = False
    elif not data['language_confirmed'] and\
            len(detected_languages) == LANGUAGE_CHAIN_LENGTH and detected_languages[0] != data['language'] and \
            all(e == detected_languages[0] for e in detected_languages):
        data['message_without_response'] = message
        data['suggest_change_language'] = True

        conversations[session_id] = {'conversation': conversation,
                                     'data': data}
        return jsonify({'session_id': session_id,
                        'response': "Змінити мову з {} на {}?".format(data['language'], detected_languages[0]),
                        'from_core': True})

    if is_aggressive(message):
        if data['aggressive_met']:
            switch_to = conversation.frame.get('current_topic') or 'general'
            conversations[session_id] = {'conversation': conversation,
                                         'data': data}
            return jsonify({'session_id': session_id,
                            'response': "Заспокойтесь, ми з'єднаємо вас з оператором!",
                            'from_core': True,
                            'switch_to': switch_to})
        else:
            data['aggressive_met'] = True
            conversations[session_id] = {'conversation': conversation,
                                         'data': data}
            return jsonify({'session_id': session_id,
                            'response': "Заспокойтеся, будь ласка, ми вирішимо вашу проблему.",
                            'from_core': True})

    conversation.context = data
    response = conversation.say(message)
    data = conversation.context

    intent = conversation.history[0]['request']['intent']
    entities = conversation.history[0]['request']['entities']

    # TODO: Exit on goodbye?
    # if intent == 'goodbye':
    #     del conversations[session_id]

    conversations[session_id] = {'conversation': conversation,
                                 'data': data}
    return jsonify({
        'session_id': session_id,
        'response': response,
        'intent': intent,
        'entities': entities,
        'from_core': False,
        'lang': data['language']
    })


api.run(host='0.0.0.0', debug=True)