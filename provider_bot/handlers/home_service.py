from provider_bot.root import app
from provider_bot.bot_db import get_user_data, call_home_service


@app.handle(intent='home_service')
def home_service(request, responder):
    if request.intent == 'home_service':
        responder.reply('Ви бажаєте залишити заявку на виклик майстра додому?')
        responder.params.target_dialogue_state = 'home_service'
        return
    if request.intent == 'abort':
        responder.reply('Зрозуміло. Чим іще ми можемо вам допомогти?')
        return
    if request.intent == 'confirmation':
        responder.params.target_dialogue_state = 'home_service_day_choice'
        responder.reply('На який день ви бажаєте викликати майстра?')
        return
    else:
        responder.frame['home_service_count'] = responder.frame.get('home_service_count', 0) + 1
        if responder.frame['home_service_count'] < 3:
            responder.params.target_dialogue_state = 'home_service'
            responder.reply('Вибачте я вас не зрозуміла. Ви бажаєте залишити заявку на виклик майстра?')
            return
        else:
            responder.frame['home_service_count'] = 0
            responder.reply('Вибачте, будь ласка, я вас не зрозуміла. Чим ще ми можемо вам допомогти?')
            return


@app.handle(targeted_only=True)
def home_service_day_choice(request, responder):
    if request.intent == 'abort':
        responder.reply('Зрозуміло. Чим іще ми можемо вам допомогти?')
        return
    day = None
    for e in request.entities:
        if e['type'] == 'sys_time' and e['role'] == 'day':
            day = e['value'][0]['value']
    if not day:
        responder.frame['home_service_day_choice_count'] = responder.frame.get('home_service_day_choice_count', 0) + 1
        if responder.frame['home_service_day_choice_count'] < 3:
            responder.params.target_dialogue_state = 'home_service_day_choice'
            responder.reply('Повторіть, будь ласка. На який день ви бажаєте викликати майстра?')
            return
        else:
            responder.frame['home_service_day_choice_count'] = 0
            responder.reply('Не вдалося розпізнати день. Зачекайте на з\'єднання з оператором.')
            return
    else:
        responder.frame['home_service_day'] = day
        responder.params.target_dialogue_state = 'home_service_hour_choice'
        responder.reply('На яку годину ви бажаєте викликати майстра?')


@app.handle(targeted_only=True)
def home_service_hour_choice(request, responder):
    if request.intent == 'abort':
        responder.reply('Зрозуміло. Чим іще ми можемо вам допомогти?')
        return
    hour = None
    for e in request.entities:
        if e['type'] == 'sys_time' and e['role'] == 'hour':
            hour = e['value'][0]['value']
    if not hour:
        responder.frame['home_service_hour_choice_count'] = responder.frame.get('home_service_hour_choice_count', 0) + 1
        if responder.frame['home_service_hour_choice_count'] < 3:
            responder.params.target_dialogue_state = 'home_service_hour_choice'
            responder.reply('Повторіть, будь ласка. На яку годину ви бажаєте викликати майстра?')
            return
        else:
            responder.frame['home_service_hour_choice_count'] = 0
            responder.reply('Не вдалося розпізнати годину. Зачекайте на з\'єднання з оператором.')
            return
    else:
        responder.frame['user'] = get_user_data(request.context['username'])
        day = request.frame['home_service_day']
        call_home_service(responder.frame['user']['id'], day, hour)
        responder.reply(f'Заявку на виклик майстра на {str(day)[:10]} {str(hour)[11:16]} створено. ' +
                        'Очікуйте на дзвінок від майстра. Чим ще можемо вам допомогти?')
