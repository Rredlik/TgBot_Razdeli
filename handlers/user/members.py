from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ContentType, Message

from database.methods.db_event import get_event_members, add_event_member
from database.methods.db_event import get_event_transactions, \
    get_transaction_by_id, get_all_transaction_payers
from database.methods.db_user import add_new_bot, user_id_by_tg_id
from handlers.user.event import backToEventFromOther, __send_event
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
                           text=f'Нажмите "Добавить участника", чтобы добавить нового участника в мероприятие.\n',
                                # f'Нажмите на участника из списка, чтобы удалить его',
                           reply_markup=markup)


async def __membersAddNewMember(call: CallbackQuery, state: FSMContext):
    await state.set_state(EventMembers.AddNewMember)
    event_id = call.data.split('_')[1]
    markup = (InlineKeyboardMarkup()
              # .add(InlineKeyboardButton('Пользуется', callback_data=f'addNewMember_user_{event_id}'))
              .add(InlineKeyboardButton('Не пользуется', callback_data=f'addNewMember_bot_{event_id}')))
    await send_callMessage(call,
                           text=f'Нажмите "Добавить участника", чтобы добавить нового участника в мероприятие.\n'
                                f'Нажмите на участника, чтобы удалить его',
                           reply_markup=markup)


async def __membersAddNewMemberBotOrUser(call: CallbackQuery, state: FSMContext):

    member_type = call.data.split('_')[2]
    event_id = call.data.split('_')[2]

    if member_type == 'user':
        await state.set_state(EventMembers.AddNewMemberUserID)
        txt = 'ID'
    else:
        await state.set_state(EventMembers.AddNewMemberBotName)
        txt = 'имя'
    async with state.proxy() as data:
        data['event_id'] = event_id
    markup = (InlineKeyboardMarkup().add(InlineKeyboardButton('Отмена',
                                    callback_data=f'backToEvent_{event_id}')))
    await send_callMessage(call,
                           text=f'Введите {txt} участника, которого хотите добавить',
                           reply_markup=markup)


async def __membersAddNewMemberBot(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        event_id = data['event_id']
    await state.reset_state()
    bot_name = msg.text
    telegram_id_bot = await add_new_bot(bot_name)
    await add_event_member(event_id, telegram_id_bot)

    markup = (InlineKeyboardMarkup().add(InlineKeyboardButton('Отмена',
                                                              callback_data=f'backToEvent_{event_id}')))
    await send_callMessage(msg,
                           text=f'Участник {bot_name} добавлен в мероприятие',
                           reply_markup=markup)
    await __send_event(msg, event_id)


def register_members_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(__membersWatchAll,
                                       lambda c: c.data and c.data.startswith('showAllMembers_'),
                                       state='*')
    dp.register_callback_query_handler(backToEventFromOther,
                                       lambda c: c.data and c.data.startswith('backToEvent_'),
                                       state=EventMembers.ShowAllMembers)

    dp.register_callback_query_handler(backToEventFromOther,
                                       lambda c: c.data == 'addNewMember',
                                       state=EventMembers.ShowAllMembers)

    dp.register_message_handler(__membersAddNewMemberBot, content_types=[ContentType.TEXT],
                                state=EventMembers.AddNewMemberBotName)
    dp.register_message_handler(__connectedToEvent, content_types=[ContentType.TEXT],
                                state=EventMembers.AddNewMemberUserID)