import asyncio

from aiogram import Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery, ContentType
from aiogram.utils import exceptions
from aiogram.utils.exceptions import ChatNotFound
from loguru import logger

from database.methods.db_user import parseAllUsers, make_new_admin
from filters.main import IsAdmin
# from handlers.admin.applications import _register_applications_handlers
from handlers.admin.media import _register_media_handlers
from handlers.keyboards import kb_main_menu
from utils.misc.const_functions import get_unix
from utils.states import ADPosting, AddAdmin


async def __admin_menu(msg: Message, state: FSMContext):
    await state.reset_state()
    userId = msg.from_user.id
    message_txt = ('Меню специальных функций администратора\n\n'
                   '- Добавить нового администратора\n'
                   '- Информация о боте\n'
                   '- Рассылка для всех пользователей')
    markup = InlineKeyboardMarkup() \
        .add(InlineKeyboardButton('Добавить администратора', callback_data='add_new_admin')) \
        .add(InlineKeyboardButton('Информация', callback_data='analytic')) \
        .add(InlineKeyboardButton('Рассылка', callback_data='adPosting'))

    await msg.bot.send_message(userId, message_txt, reply_markup=markup)
    # logger.info(f'User_id: {userId}')


# endregion
######################################################
######################################################
# Add New Admin region
async def __new_admin(query: CallbackQuery, state: FSMContext):
    await state.reset_state()
    await state.set_state(AddAdmin.TakeUserId)
    text = ('Отправьте id пользователя которого хотите добавить в администраторы.\n'
            'Получить его можно переслав сообщение этому боту: t.me/getmyid_bot')
    markup = InlineKeyboardMarkup() \
        .add(InlineKeyboardButton('Отмена', callback_data='close_menu_AD'))
    await query.bot.send_message(query.from_user.id, text, reply_markup=markup)


async def __AddAdmin(msg: Message, state: FSMContext):
    await state.reset_state()
    bot: Bot = msg.bot
    user_id = msg.from_user.id
    new_admin_id = msg.text
    # print('new_admin_username', new_admin_username)
    try:
        await make_new_admin(new_admin_id)
        await bot.send_message(new_admin_id, 'Вам выданы права админа', reply_markup=await kb_main_menu(new_admin_id))
        await bot.send_message(user_id, 'Новый администратор добавлен', reply_markup=await kb_main_menu(user_id))
        logger.info(f'Добавлен новый администатор: {user_id}')
    except ChatNotFound:
        await bot.send_message(user_id, 'Пользователь не найден', reply_markup=await kb_main_menu(user_id))


# endregion
######################################################
######################################################
# region Advertising
async def __write_AdPost(query: CallbackQuery, state: FSMContext):
    await state.reset_state()
    await state.set_state(ADPosting.WriteText)
    text = '📷 Фото: выбери одну фотографию и напиши текст поста\n' \
           '🎥 Видео: выбери одно видео и напиши текст поста\n\n' \
           'Специальные правила оформления для текста:\n' \
           '&lt;a href="ссылка"&gt;текст с сылкой&lt;/a&gt;\n' \
           '&lt;b&gt;<b>Полужирный текст</b>&lt;/b&gt;\n' \
           '&lt;i&gt;<i>Текст курсив</i>&lt;/i&gt;\n\n' \
           'Введите текст сообщения для рассылки, либо нажмите отмена\n\n'
    markup = InlineKeyboardMarkup() \
        .add(InlineKeyboardButton('Отмена', callback_data='close_menu_AD'))

    await query.bot.send_message(query.from_user.id, text, reply_markup=markup)


async def __check_AdPost(msg: Message, state: FSMContext, image=None, video=None):
    bot: Bot = msg.bot
    userId = msg.from_user.id
    await ADPosting.CheckPost.set()
    addText = '\n\n⬆⬆⬆\nПроверьте сообщение и нажмите "Отправить", если все хорошо, иначе нажмите "Исправить"'
    markup = InlineKeyboardMarkup() \
        .add(InlineKeyboardButton('Отправить', callback_data='sendAdPost')) \
        .add(InlineKeyboardButton('Исправить', callback_data='adPosting'))

    if msg.content_type == ContentType.PHOTO:
        image = msg.photo[0].file_id
        msgText = msg.caption if msg.caption else ''
        await bot.send_photo(userId, image, msgText + addText, reply_markup=markup)
    elif msg.content_type == ContentType.VIDEO:
        video = msg.video.file_id
        msgText = msg.caption if msg.caption else ''
        await bot.send_video(userId, video, msgText + addText, reply_markup=markup)
    else:
        msgText = msg.text
        await bot.send_message(userId, msgText + addText, reply_markup=markup)

    async with state.proxy() as data:
        data['msgText'] = msgText
        data['imageId'] = image
        data['videoId'] = video
    await ADPosting.SendPost.set()


async def __send_AdPost(query: CallbackQuery, state: FSMContext):
    bot: Bot = query.bot
    # dataS = await state.get_data()
    async with state.proxy() as data:
        msgText = data['msgText']
        image = data['imageId']
        video = data['videoId']
    await state.reset_state()
    admin_id = query.from_user.id
    await bot.send_message(admin_id, 'Рассылка начата✅', reply_markup=await kb_main_menu(admin_id))
    complete_message = await broadcaster(bot, msgText, image, video)
    await bot.send_message(admin_id, complete_message, reply_markup=await kb_main_menu(admin_id))


async def broadcaster(bot, msgText, image, video) -> int:
    """
    Simple broadcaster
    :return: Count of messages
    """
    receive_users, block_users, how_users = 0, 0, 0
    allUsers = await parseAllUsers()
    get_time = await get_unix()

    try:
        for user_id in allUsers:
            if await send_ADmessage(bot, user_id[0], text=msgText, image=image, video=video):
                receive_users += 1
            else:
                block_users += 1
            await asyncio.sleep(.08)  # 20 messages per second (Limit: 30 messages per second)
    finally:
        complete_message = (
            f"📢 Рассылка была завершена за <code>{await get_unix() - get_time}сек</code>\n"
            f"👤 Всего пользователей: <code>{len(allUsers)}</code>\n"
            f"✅ Пользователей получило сообщение: <code>{receive_users}</code>\n"
            f"❌ Пользователей не получило сообщение: <code>{block_users}</code>"
        )
        logger.success(complete_message)
    return complete_message


async def send_ADmessage(bot, user_id: int, text: str, disable_notification: bool = False, image=False,
                         video=False) -> bool:
    """
    Safe messages sender
    """
    try:
        if image:
            await bot.send_photo(chat_id=user_id, photo=image, caption=text,
                                 disable_notification=disable_notification)
        elif video:
            await bot.send_video(chat_id=user_id, video=video, caption=text,
                                 disable_notification=disable_notification)
        else:
            await bot.send_message(chat_id=user_id, text=text,
                                   disable_notification=disable_notification)

    except exceptions.RetryAfter as e:
        logger.error(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
        await asyncio.sleep(e.timeout)
        return await send_ADmessage(bot, user_id, text, disable_notification, image, video)  # Recursive call
    except Exception as er:
        logger.error(f"Target [ID:{user_id}]: {er}")
    else:
        return True
    return False


# endregion
######################################################
######################################################
# region Analytics

async def __analytic(query: CallbackQuery, state: FSMContext) -> None:
    users_count = await parseAllUsers()
    text = (
        'Отчет:\n',
        f'Кол-во пользователей: {len(users_count)}'
    )
    bot: Bot = query.bot
    await query.answer('\n'.join(text), show_alert=True, cache_time=0)
    await bot.answer_callback_query(query.id)


def register_admin_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(__admin_menu, IsAdmin(), commands=['admin'],
                                state='*')
    dp.register_message_handler(__admin_menu, IsAdmin(), Text(equals="Меню админа"),
                                state='*')
    # endregion

    # Add New Admin region
    dp.register_callback_query_handler(__new_admin, IsAdmin(), lambda c: c.data == 'add_new_admin',
                                       state='*')
    dp.register_message_handler(__AddAdmin, IsAdmin(), state=AddAdmin.TakeUserId,
                                content_types=[ContentType.TEXT])
    # endregion

    # region Advertising
    dp.register_callback_query_handler(__write_AdPost, lambda c: c.data == 'adPosting',
                                       IsAdmin(), state='*')
    dp.register_message_handler(__check_AdPost, IsAdmin(), state=ADPosting.WriteText,
                                content_types=[ContentType.PHOTO, ContentType.VIDEO, ContentType.TEXT])
    dp.register_message_handler(__admin_menu, IsAdmin(), lambda c: c.data == 'close_menu_AD',
                                state=ADPosting.WriteText)
    dp.register_callback_query_handler(__send_AdPost, lambda c: c.data == 'sendAdPost',
                                       IsAdmin(), state=ADPosting.SendPost)
    # endregion

    # region Analytics
    dp.register_callback_query_handler(__analytic, lambda c: c.data == 'analytic',
                                       IsAdmin(), state='*')
    _register_media_handlers(dp)
    # _register_applications_handlers(dp)
    # endregion
