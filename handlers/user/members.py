from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database.methods.db_event import get_event_members
from database.methods.db_event import get_event_transactions, \
    get_transaction_by_id, get_all_transaction_payers
from handlers.user.event import backToEventFromOther
# from handlers.user.dialog import register_dialog_handlers
from loader import bot
from utils.methods import send_callMessage
from utils.states import EventTransactions, EventMembers


async def __membersWatchAll(call: CallbackQuery, state: FSMContext):
    await state.set_state(EventMembers.ShowAllMembers)
    event_id = call.data.split('_')[1]
    all_members = await get_event_members(event_id)

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Добавить участника',
                                    callback_data=f'addNewMember'))
    for member in all_members:
        member_id = member[0]
        member_login = member[4]
        btn_text = f'{member_login}'
        markup.add(InlineKeyboardButton(btn_text,
                                        callback_data=f'deleteEventMember_{member_id}'))
    markup.add(InlineKeyboardButton('Назад',
                                    callback_data=f'backToEvent_{event_id}'))
    await send_callMessage(call,
                           text=f'Нажмите "Добавить участника", чтобы добавить нового участника в мероприятие.\n'
                                f'Нажмите на участника, чтобы удалить его',
                           reply_markup=markup)


async def __membersAddNewMember(call: CallbackQuery, state: FSMContext):
    await state.set_state(EventMembers.AddNewMember)
    event_id = call.data.split('_')[1]

    markup = (InlineKeyboardMarkup()
              .add(InlineKeyboardButton('Пользуется', callback_data=f'addNewMember_user'))
              .add(InlineKeyboardButton('Не пользуется', callback_data=f'addNewMember_bot')))

    await send_callMessage(call,
                           text=f'Нажмите "Добавить участника", чтобы добавить нового участника в мероприятие.\n'
                                f'Нажмите на участника, чтобы удалить его',
                           reply_markup=markup)


def register_transaction_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(__membersWatchAll,
                                       lambda c: c.data and c.data.startswith('showAllMembers_'),
                                       state='*')
    dp.register_callback_query_handler(backToEventFromOther,
                                       lambda c: c.data and c.data.startswith('backToEvent_'),
                                       state=EventMembers.ShowAllMembers)

    dp.register_callback_query_handler(backToEventFromOther,
                                       lambda c: c.data == 'addNewMember',
                                       state=EventMembers.ShowAllMembers)
