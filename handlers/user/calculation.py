from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, ContentType, InlineKeyboardMarkup, InlineKeyboardButton

from database.methods.db_event import create_new_event, add_event_member, get_all_user_events
from database.methods.db_event import get_event_by_id, get_event_members, \
    create_transaction, add_transaction_members
from handlers.keyboards import btn_create_event, btn_con_event, btn_my_events
# from handlers.user.dialog import register_dialog_handlers
from loader import bot
from utils.states import Event, EventAddCheck, EventCalculation


#############################
#############################


async def __calculationsEvent(call: CallbackQuery, state: FSMContext):
    await state.reset_state()
    await state.set_state(EventCalculation.Calculate)
    user_id = call.from_user.id
    event_id = call.data.split('_')[1]
    msg_text = 'Итог мероприятия'
    msg_text_from_user = ''
    msg_text_to_user = ''

    event = await get_event_by_id(event_id)
    members = await get_event_members(event_id)
    all_members = []
    for member in members:
        all_members.append({
            'user_id': member[0],
            'telegram_id': member[1],
            'balance': 0,
            'dolg': 0
            # 'telegram_id': member[1],
        })
    transactions = '''await get_event_transactions(event_id)
        select transaction_id, user_id, amount from transactions where event_id = 1'''
    checks_sum = 0
    for transaction in transactions:
        checks_sum += int(transaction[2])

        for member in members:
            if member['user_id'] == transaction[1]:
                member['balance'] += int(transaction[2])

    checks_sum = round(checks_sum / len(members), 2)

    for member in members:
        member['dolg'] = member['balance'] - checks_sum
        if member['dolg'] < 0:
            for send_to in members:
                if send_to['user_id'] != member['user_id']:
                    if send_to['balance'] > checks_sum:
                        diff = send_to['balance'] - member['dolg']
                        if diff > 0:
                            member['dolg'] -= member['dolg']
                            send_to['balance'] -= member['dolg']
                        else:
                            member['dolg'] -= diff
                            send_to['balance'] += diff


    markup = (InlineKeyboardMarkup()
              .add(InlineKeyboardButton('Отмена', callback_data=f'cancelConnecting')))
    await bot.send_message(chat_id=user_id,
                           text=msg_text,
                           reply_markup=markup)



def register_calculation_handlers(dp: Dispatcher) -> None:
    # region EVENT
    ## create event
    dp.register_callback_query_handler(__calculationsEvent,
                                       lambda c: c.data  and c.data.startswith('calculating_'),
                                       state='*')

    dp.register_message_handler(__create_event_msg,
                                Text(equals=btn_create_event), state='*')
    dp.register_message_handler(__event_created, content_types=[ContentType.TEXT], state=Event.CreateEvent)