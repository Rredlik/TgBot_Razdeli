from asyncio import exceptions

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, ContentType

from config import ADMIN_LINK
<<<<<<< HEAD
from database.methods.db_event import create_new_event, add_event_member, get_event_by_id
=======
from database.methods.db_event import create_new_event, add_event_member
>>>>>>> 733588f7e4d4b7056534b357ff9d58ff5fae8575
from database.methods.db_user import user_id_by_tg_id
from filters.main import IsSubscriber
from handlers.keyboards import btn_create_event
from handlers.user.dialog import register_dialog_handlers
from handlers.user.register import _register_register_handlers
from loader import bot
from utils.states import Event


async def __create_event_msg(msg: Message, state: FSMContext):
    await state.set_state(Event.CreateEvent)
    await bot.send_message(chat_id=msg.from_user.id,
                           text=f'Введите название мероприятия')


async def __event_created(msg: Message):
    event_id = await create_new_event(msg.text)
    # user_id = await user_id_by_tg_id(msg.from_user.id)
    # telegram_id =
    await add_event_member(event_id, msg.from_user.id)
    await bot.send_message(chat_id=msg.from_user.id,
                           text=f'Мероприятие создано')
    await __send_event(msg, event_id)

async def __send_event(msg: Message, event_id=None):
    event = await get_event_by_id(event_id)
    event_name = event[1]
    event_date = event[2]
    event_message = (f'ID Меропириятия: {event_id}\n'
                     f'Название: {event_name}\n'
                     f'')
    await bot.send_message(chat_id=msg.from_user.id,
                           text=f'event_message')


    await bot.send_message()


def register_event_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(__create_event_msg,
                                Text(equals=btn_create_event), state='*')
    dp.register_message_handler(__event_created, content_types=[ContentType.TEXT], state=Event.CreateEvent)
