from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database.methods.db_event import get_payer_debtors, get_debt_to_payers
from database.methods.db_user import user_id_by_tg_id
from utils.methods import send_callMessage
from utils.states import EventCalculation


#############################
#############################


async def __calculationsEvent(call: CallbackQuery, state: FSMContext):
    await state.reset_state()
    await state.set_state(EventCalculation.Calculate)
    user_telegram_id = call.from_user.id
    event_id = call.data.split('_')[1]
    msg_text_from_user = ''
    msg_text_to_user = ''

    user_id = await user_id_by_tg_id(user_telegram_id)
    debtors = await get_payer_debtors(event_id, user_id)
    payers = await get_debt_to_payers(event_id, user_id)

    for payer in payers:
        payer_id = payer[0]
        debtor_id = payer[1]
        payer_login = payer[2]
        user_to_payer_amount = payer[3]
        msg_text_from_user += f'Перевести пользователю {payer_login}: {round(user_to_payer_amount)}\n'
    # msg_text_from_user = re.sub('\n$', '\n\n', msg_text_from_user)

    for debtor in debtors:
        payer_id = debtor[0]
        debtor_id = debtor[1]
        debtor_login = debtor[2]
        debtor_to_user_amount = debtor[3]
        msg_text_to_user += f'Пользователь {debtor_login} должен вам: {round(debtor_to_user_amount)}\n'

    markup = (InlineKeyboardMarkup()
              .add(InlineKeyboardButton('Назад', callback_data=f'backToEvent_{event_id}')))
    msg_text = (f'Итог мероприятия\n\n'
                f'{msg_text_from_user}\n'
                f'{msg_text_to_user}')
    await send_callMessage(call,
                           text=msg_text,
                           reply_markup=markup)


def register_calculation_handlers(dp: Dispatcher) -> None:
    # region Calculation
    ## show calculate
    dp.register_callback_query_handler(__calculationsEvent,
                                       lambda c: c.data  and c.data.startswith('calculating_'),
                                       state='*')
