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
from utils.states import Event, EventAddCheck, EventTransactions


async def __transactionsWatchAll(call: CallbackQuery, state: FSMContext):
    await state.set_state(EventTransactions.WatchAllTransactions)
    event_id = call.data.split('_')[1]

    markup = (InlineKeyboardMarkup()
              .add(InlineKeyboardButton('Назад', callback_data=f'backToEvent_{event_id}')))
    await bot.send_message(chat_id=call.from_user.id,
                           text=f'Введите название мероприятия',
                           reply_markup=markup)


def register_transaction_handlers(dp: Dispatcher) -> None:

    dp.register_callback_query_handler(__transactionsWatchAll,
                                       lambda c: c.data and c.data.startswith('showChecks_'),
                                       state='*')
