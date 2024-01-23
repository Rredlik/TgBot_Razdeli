from datetime import datetime

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ContentType
from loguru import logger

from database.main import connectToDB
from database.methods.db_user import update_user_data
from handlers.keyboards import *
from loader import bot
from utils.states import Register


async def __start(message: Message, state: FSMContext):
    await state.reset_state()
    user_id = message.from_user.id

    is_reg = await is_registered(message=message)
    if is_reg:
        msg_txt = "Отправил вам клавиатуру. Используйте кнопки, чтобы пользоваться ботом"
        await bot.send_message(chat_id=user_id, text=msg_txt, reply_markup=await kb_main_menu(user_id))
    else:
        await state.set_state(Register.WaitLogin)
        msg_txt = ("Приветствую вас! Это бот для справедливого расчета между "
                   "участниками мероприятия или проекта\n\n"
                   "Введите ваш логин, пожалуйста")
        await bot.send_message(chat_id=user_id, text=msg_txt)


async def __getName(message: Message, state: FSMContext):
    await state.reset_state()
    user_id = message.from_user.id
    user_login = message.text
    '''
    TO DO:
    Добавить проверку правильности ввода логина (без лишних символов и пробелов)
    '''
    await update_user_data(user_id, 'user_login', user_login)
    msg_txt = ('Спасибо за регистрацию.\n'
               'Используйте кнопки, чтобы пользоваться ботом')
    await bot.send_message(chat_id=user_id, text=msg_txt, reply_markup=await kb_main_menu(user_id))


async def __mainMenu(msg: Message, state: FSMContext) -> None:
    await state.reset_state()
    user_id = msg.from_user.id
    msg_text = 'Используй кнопки, чтобы пользоваться ботом'
    await bot.send_message(chat_id=user_id,
                           text=msg_text,
                           reply_markup=await kb_main_menu(user_id))


###########################################################################################################
###########################################################################################################

async def is_registered(user_id=None, message: Message = None):
    if message is not None:
        user_id = message.from_user.id
    async with connectToDB() as db:
        try:
            command = await db.execute(
                """SELECT * FROM 'users' WHERE telegram_id = :user_id""",
                {'user_id': user_id}
            )
            await db.commit()
            values = await command.fetchone()

            if values is None:
                await create_new_user(user_id, message)
                return False
            else:
                return True
        except Exception as er:
            logger.error(f"{er}")
        finally:
            await db.commit()


async def create_new_user(user_id=None, message: Message = None):
    username = 'admin'
    if message is not None:
        user_id = str(message.from_user.id)
        username = message.from_user.username.lower()
    async with connectToDB() as db:
        try:
            await db.execute(
                "INSERT INTO 'users' (telegram_id, user_name, reg_date) VALUES (?, ?, ?)",
                (user_id, username, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            )
            logger.info(f"New user registered: {user_id}")
            await db.commit()
        except Exception as er:
            logger.error(f"{er}")
        finally:
            await db.commit()


def _register_register_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(__start, commands=["start"], state='*')
    dp.register_message_handler(__getName, content_types=[ContentType.TEXT], state=Register.WaitLogin)
    # dp.register_callback_query_handler(attention_to_sub, lambda c: c.data == 'check_sub_status', state='*')
