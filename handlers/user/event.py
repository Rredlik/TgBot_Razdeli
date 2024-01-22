from asyncio import exceptions

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, ContentType, InlineKeyboardMarkup, InlineKeyboardButton

from config import ADMIN_LINK
from database.methods.db_event import create_new_event, add_event_member, get_event_by_id, get_event_members
from database.methods.db_event import create_new_event, add_event_member
from database.methods.db_user import user_id_by_tg_id
from filters.main import IsSubscriber
from handlers.keyboards import btn_create_event
# from handlers.user.dialog import register_dialog_handlers
from handlers.user.register import _register_register_handlers
from loader import bot
from utils.states import Event, EventAddCheck


async def __create_event_msg(msg: Message, state: FSMContext):
    await state.set_state(Event.CreateEvent)
    await bot.send_message(chat_id=msg.from_user.id,
                           text=f'Введите название мероприятия')


async def __event_created(msg: Message, state: FSMContext):
    event_id = await create_new_event(msg.text)
    # user_id = await user_id_by_tg_id(msg.from_user.id)
    # telegram_id =

    await add_event_member(event_id, msg.from_user.id)
    await bot.send_message(chat_id=msg.from_user.id,
                           text=f'Мероприятие создано')
    await state.reset_state()
    await __send_event(msg, event_id)


async def __send_event(msg: Message, event_id=None, state: FSMContext = None):
    if state is not None:
        await state.reset_state()
    event = await get_event_by_id(event_id)
    event_name = event[1]
    event_date = event[2]
    members = await get_event_members(event_id)

    event_message = (f'ID Меропириятия: <code>{event_id}</code>\n'
                     f'Название: {event_name}\n'
                     f'Дата: {event_date}\n'
                     f'Участников: {len(members)}')

    markup = (InlineKeyboardMarkup()
              .add(InlineKeyboardButton('Добавить чек', callback_data=f'addCheck_{event_id}'))
              .add(InlineKeyboardButton('Добавить участника', callback_data=f'addMember_{event_id}'))
              .add(InlineKeyboardButton('Посмотреть чеки', callback_data=f'addMember_{event_id}')))
    await bot.send_message(chat_id=msg.from_user.id,
                           text=event_message, reply_markup=markup)


async def __addCheck_selectMember(call: CallbackQuery, state: FSMContext):
    await state.set_state(EventAddCheck.ChooseMember)
    event_id = call.data.split('_')[1]
    members = await get_event_members(event_id)
    markup = InlineKeyboardMarkup()

    for member in members:
        member_id = member[0]
        member_login = member[4]
        markup.add(InlineKeyboardButton(text=f'{member_login}',
                                        callback_data=f'addCheckOwner_{member_id}'))
    await bot.send_message(chat_id=call.from_user.id,
                           text=f'Выберите участника, который платил за чек',
                           reply_markup=markup)


def register_event_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(__create_event_msg,
                                Text(equals=btn_create_event), state='*')
    dp.register_message_handler(__event_created, content_types=[ContentType.TEXT], state=Event.CreateEvent)

    dp.register_callback_query_handler(__addCheck_selectMember,
                                       lambda c: c.data and c.data.startswith('addCheck_'), state=None)
    dp.register_callback_query_handler(__addCheck_selectMember,
                                       lambda c: c.data and c.data.startswith('addCheckOwner_'),
                                       state=EventAddCheck.ChooseMember)
