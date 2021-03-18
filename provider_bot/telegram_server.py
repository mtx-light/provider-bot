from telebot import TeleBot

from provider_bot.__init__ import app
from mindmeld.components.dialogue import Conversation
from provider_bot.bot_db import create_database

bot = TeleBot(__name__)

conversations = {}

@bot.route('/start')
def reply(message):
    try:
        username = message['chat']['username'].lower()
    except:
        return

    conversations[username] = {}
    conversations[username]['data'] = {'username': username}
    conversations[username]['conversation'] = Conversation(app=app, context=conversations[username]['data'])

    print(f"{username} has new session")
    print("==========================")
    bot.send_message(message['chat']['id'], "")

@bot.route('.*')
def reply(message):
    try:
        request_text = message['text']
        username = message['chat']['username'].lower()
    except:
        return

    if username not in conversations:
        conversations[username] = {}
        conversations[username]['data'] = {'username': username}
        conversations[username]['conversation'] = Conversation(app=app, context=conversations[username]['data'])
    resp = conversations[username]['conversation'].say(request_text)[0]

    print(username)
    print(request_text)
    print(resp)
    print("==========================")
    bot.send_message(message['chat']['id'], resp)


create_database()
bot.config['api_key'] = '1690556509:AAEejV2fvqsexl8KgWbtLsb1IjRbTujzHo0'
bot.poll(debug=True)

