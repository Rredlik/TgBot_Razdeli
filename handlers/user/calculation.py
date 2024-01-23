from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database.methods.db_event import get_event_by_id, get_event_members
from database.methods.db_event import get_event_transactions
# from handlers.user.dialog import register_dialog_handlers
from utils.methods import send_callMessage
from utils.states import EventCalculation


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
            'user_login': member[4],
            'balance': 0,
            'dolg': 0
            # 'telegram_id': member[1],
        })
    transactions = await get_event_transactions(event_id)
        # '''select transaction_id, user_id, amount from transactions where event_id = 1'''
    checks_sum = 0
    for transaction in transactions:
        checks_sum += int(transaction[4])

        for member in all_members:
            if member['user_id'] == transaction[1]:
                member['balance'] += int(transaction[4])

    checks_sum = round(checks_sum / len(members), 2)
    for member in all_members:
        member['dolg'] = member['balance'] - checks_sum

    for member in all_members:
        if member['dolg'] < 0:
            for send_to in all_members:
                if send_to['user_id'] != member['user_id']:
                    if send_to['balance'] > checks_sum:
                        diff = send_to['balance'] - member['dolg']
                        if diff > 0:
                            member['dolg'] -= member['dolg']
                            send_to['balance'] -= member['dolg']
                            msg_text_from_user += f'Перевести пользователю {send_to["user_login"]} {member["dolg"]}'
                        else:
                            member['dolg'] -= diff
                            send_to['balance'] += diff
                            msg_text_to_user += f'Пользователь {send_to["user_login"]} должен вам {member["dolg"]}'
                    # else:
                    #     diff = member['dolg']


    markup = (InlineKeyboardMarkup()
              .add(InlineKeyboardButton('Назад', callback_data=f'backToEvent_{event_id}')))
    msg_text += msg_text_from_user
    msg_text += msg_text_to_user
    await send_callMessage(call,
                           text=msg_text,
                           reply_markup=markup)


def register_calculation_handlers(dp: Dispatcher) -> None:
    # region EVENT
    ## create event
    dp.register_callback_query_handler(__calculationsEvent,
                                       lambda c: c.data  and c.data.startswith('calculating_'),
                                       state='*')


    # dp.register_message_handler(__create_event_msg,
    #                             Text(equals=btn_create_event), state='*')
    # dp.register_message_handler(__event_created, content_types=[ContentType.TEXT], state=Event.CreateEvent)