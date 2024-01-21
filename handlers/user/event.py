from asyncio import exceptions

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, ContentType

from config import ADMIN_LINK
from filters.main import IsSubscriber
from handlers.keyboards import btn_create_event
from handlers.user.dialog import register_dialog_handlers
from handlers.user.register import _register_register_handlers
from loader import bot
from utils.states import Event


async def __create_event_msg(msg: Message, state: FSMContext):
    await state.set_state(Event.CreateState)
    await bot.send_message(chat_id=msg.from_user.id,
                           text=f'Введите название мероприятия')


async def __event_created(msg: Message):
    add_event_member(event_id, telegram_id)
    await bot.send_message(chat_id=msg.from_user.id,
                           text=f'Мероприятие создано')




def register_dialog_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(__create_event_msg,
                                Text(equals=btn_create_event), state='*')
    dp.register_message_handler(__event_created, content_types=[ContentType.TEXT], state=Event.CreateState)