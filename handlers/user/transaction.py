from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, ContentType, InlineKeyboardMarkup, InlineKeyboardButton

from database.methods.db_event import create_new_event, add_event_member, get_all_user_events, get_event_transactions, \
    get_transaction_by_id, get_all_transaction_payers
from database.methods.db_event import get_event_by_id, get_event_members, \
    create_transaction, add_transaction_members
from handlers.keyboards import btn_create_event, btn_con_event, btn_my_events
from handlers.user.event import __send_event, backToEventFromOther
# from handlers.user.dialog import register_dialog_handlers
from loader import bot
from utils.states import Event, EventAddCheck, EventTransactions



async def __transactionsWatchAll(call: CallbackQuery, state: FSMContext):
    await state.set_state(EventTransactions.SelectTransaction)
    event_id = call.data.split('_')[1]
    transactions = await get_event_transactions(event_id)
    markup = InlineKeyboardMarkup()
    for transaction in transactions:
        transaction_id = transaction[0]
        transaction_name = transaction[3]
        amount = transaction[4]
        markup.add(
            InlineKeyboardButton(f'{transaction_name} - {amount}', callback_data=f'openEventCheck_{transaction_id}'))
    markup.add(InlineKeyboardButton('Назад', callback_data=f'backToEvent_{event_id}'))
    await bot.send_message(chat_id=call.from_user.id,
                           text=f'Выберите чек и нажмите на него, чтобы посмотреть подробную информацию',
                           reply_markup=markup)


async def __transactionsOpenOne(call: CallbackQuery, state: FSMContext):
    await state.set_state(EventTransactions.OpenTransaction)
    transaction_id = call.data.split('_')[1]
    transaction = await get_transaction_by_id(transaction_id)
    all_members = await get_event_members(transaction[2])
    payers = await get_all_transaction_payers(transaction_id)
    event_id = transaction[2]
    transaction_name = transaction[3]
    transaction_amount = transaction[4]
    print(payers)
    markup = InlineKeyboardMarkup()
    members = []
    for member in all_members:
        is_payer = False
        member_id = member[0]
        member_login = member[4]
        btn_text = f'{member_login} ❌'
        if member[1] in payers:
            is_payer = True
            btn_text = f'{member_login} ✅'
        members.append({
            'member_id': member_id,
            'member_login': member_login,
            'is_payer': is_payer
        })
        markup.add(InlineKeyboardButton(btn_text,
                                        callback_data=f'changePayerStatusInCheck_{member_id}'))
    async with state.proxy() as data:
        data['event_id'] = event_id
        data['members'] = members
    markup.add(InlineKeyboardButton('Назад',
                                    callback_data=f'backToEventTransactions_{event_id}'))
    await bot.send_message(chat_id=call.from_user.id,
                           text=f'Чек: {transaction_name}\n'
                                f'Сумма чека: {transaction_amount}\n\n'
                                f'Нажмите на участника, чтобы изменить его статус плательщика за этот чек',
                           reply_markup=markup)


async def __transactions_changePayerStatus(call: CallbackQuery, state: FSMContext):
    user_id = call.data.split('_')[1]
    async with state.proxy() as data:
        members = data['members']
        event_id = data['event_id']
    markup = InlineKeyboardMarkup()
    for member in members:
        member_id = member['user_id']
        member_login = member['user_login']
        if str(member_id) == str(user_id):
            member['is_payer'] = not member['is_payer']
        is_payer = '✅' if member['is_payer'] else '❌'
        markup.add(InlineKeyboardButton(text=f'{member_login} {is_payer}',
                                        callback_data=f'changePayerStatusInCheck_{member_id}'))
    async with state.proxy() as data:
        data['members'] = members
    markup.add(InlineKeyboardButton('Назад',
                                    callback_data=f'backToEventTransactions_{event_id}'))
    await bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        reply_markup=markup)


def register_transaction_handlers(dp: Dispatcher) -> None:


    dp.register_callback_query_handler(__transactionsWatchAll,
                                       lambda c: c.data and c.data.startswith('showChecks_'),
                                       state='*')

    dp.register_callback_query_handler(__transactionsOpenOne,
                                       lambda c: c.data and c.data.startswith('openEventCheck_'),
                                       state=EventTransactions.SelectTransaction)
    dp.register_callback_query_handler(__transactions_changePayerStatus,
                                       lambda c: c.data and c.data.startswith('changePayerStatusInCheck_'),
                                       state=EventTransactions.OpenTransaction)

    dp.register_callback_query_handler(__transactionsWatchAll,
                                       lambda c: c.data and c.data.startswith('backToEventTransactions_'),
                                       state=EventTransactions.OpenTransaction)
