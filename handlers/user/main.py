from asyncio import exceptions

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

from config import ADMIN_LINK
from filters.main import IsSubscriber
from handlers.keyboards import btn_create_event, kb_main_menu
from handlers.user.calculation import register_calculation_handlers
# from handlers.user.dialog import register_dialog_handlers
from handlers.user.event import register_event_handlers
from handlers.user.members import register_members_handlers
from handlers.user.register import _register_register_handlers
from handlers.user.transaction import register_transaction_handlers
from loader import bot





async def __askTp(msg: Message):
    await bot.send_message(chat_id=msg.from_user.id,
                           text=f'Если у вас возникли вопросы или что-то не работает пишите: {ADMIN_LINK}')


def register_users_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(__askTp, Text(equals='👩🏼‍💻 Тех. поддержка'), IsSubscriber(), state='*')

    # dp.chat_join_request_handler(__channel_member)
    # dp.register_errors_handler(function_name, exception=exceptions.)

    _register_register_handlers(dp)
    register_event_handlers(dp)
    register_transaction_handlers(dp)
    register_calculation_handlers(dp)
    register_members_handlers(dp)
    # register_dialog_handlers(dp)
