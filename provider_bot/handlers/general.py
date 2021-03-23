from provider_bot.root import app
from provider_bot.bot_db import get_user_data
from provider_bot.vocalizer import vocalized_name
from provider_bot.utils.state_logger import logged


@app.handle(default=True)
@logged
def default(request, responder):
    """This is a default handler."""
    responder.reply('Перепрошую?')


@app.handle(intent='thanks')
@logged
def thanks(request, responder):
    responder.reply(['Прошу.', 'Завжди рада допомогти.'])


@app.handle(intent='small_talk')
@logged
def small_talk(request, responder):
    responses = ['Я би з задоволенням з вами поспілкувалася, але можу допомогти лише з послугами компанії "Воля."',
                 'На жаль, на це відповісти я не зможу.',
                 'Я розумію, що вам цікаво зі мною погратися, але я не найкращий співбесідник, якщо справа не стосується послуг компанії "Воля"',
                 'Що ж, якщо будуть питання щодо послуг компанії "Воля" - звертайтесь.']
    responder.frame['small_talk_cycle'] = responder.frame.get('small_talk_cycle', 0)
    responder.reply(responses[responder.frame['small_talk_cycle']])
    responder.frame['small_talk_cycle'] += 1
    if responder.frame['small_talk_cycle'] >= len(responses):
        responder.frame['small_talk_cycle'] = 0


@app.handle(intent='confirmation')
@logged
def confirmation(request, responder):
    responder.reply(['Чим саме я можу вам допомогти?',
                     'Сформулюйте, будь ласка, ваш запит.'])


@app.handle(intent='greet')
@logged
def welcome(request, responder):
    responder.frame['greeted'] = responder.frame.get('greeted', False)
    username = get_user_data(request.context['username'])['username']
    if not responder.frame['greeted']:
        responder.frame['greeted'] = True
        if username:
            responder.reply(f'Вітаю, {vocalized_name(username)}!')
        else:
            responder.reply('Вітаю!')
    else:
        responder.reply([f'Слухаю вас',
                         f'Так-так, я вас слухаю',
                         f'Так, {vocalized_name(username)}, чим можу допомогти?'])


@app.handle(intent='abort')
@logged
def abort(request, responder):
    responder.reply("Буду рада вам допомогти, якщо виникнуть проблеми.")


@app.handle(intent='goodbye')
@logged
def goodbye(request, responder):
    responder.reply(['До побачення!', 'До зустрічі!', "На зв'язку!", "Бувайте!"])


@app.handle(intent='suicide')
@logged
def suicide(request, responder):
    responder.reply("Ми готові вас вислухати, зачекайте хвилинку.")
