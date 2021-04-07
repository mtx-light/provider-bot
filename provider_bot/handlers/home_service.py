from provider_bot.handlers.balance_and_home_service import balance_and_home_service
from provider_bot.root import app
from provider_bot.bot_db import get_user_data, call_home_service
from provider_bot.utils.state_logger import logged

@app.handle(intent='home_service')
@logged
def home_service(request, responder):
    responder.frame['with_balance'] = False
    balance_and_home_service(request, responder)