from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, ContentType, InlineKeyboardMarkup, InlineKeyboardButton

from database.methods.db_event import create_new_event, add_event_member, get_all_user_events, get_event_transactions, \
    get_transaction_by_id, get_all_transaction_payers
from database.methods.db_event import get_event_by_id, get_event_members, \
    create_transaction, add_transaction_members
from handlers.keyboards import btn_create_event, btn_con_event, btn_my_events
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
        markup.add(InlineKeyboardButton(f'{transaction_name} - {amount}', callback_data=f'openEventCheck_{transaction_id}'))
    markup.add(InlineKeyboardButton('Назад', callback_data=f'backToEvent_{event_id}'))
    await bot.send_message(chat_id=call.from_user.id,
                           text=f'Выберите чек и нажмите на него, чтобы посмотреть подробную информацию',
                           reply_markup=markup)


async def __transactionsOpenOne(call: CallbackQuery, state: FSMContext):
    await state.set_state(EventTransactions.SelectTransaction)
    transaction_id = call.data.split('_')[1]
    transaction = await get_transaction_by_id(transaction_id)
    all_members = await get_event_members(transaction[2])
    payers = await get_all_transaction_payers(transaction_id)

    for member in all_members:
        if member[1]


def register_transaction_handlers(dp: Dispatcher) -> None:

    dp.register_callback_query_handler(__transactionsWatchAll,
                                       lambda c: c.data and c.data.startswith('showChecks_'),
                                       state='*')
    dp.register_callback_query_handler(__transactionsWatchAll,
                                       lambda c: c.data and c.data.startswith('openEventCheck_'),
                                       state=EventTransactions.SelectTransaction)
