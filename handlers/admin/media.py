from aiogram import Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType, Message
from loguru import logger

from config import ADMIN_IDS
from filters.main import IsAdmin
from handlers.keyboards import kb_main_menu


async def send_photo_file_id(msg: Message):
    bot: Bot = msg.bot
    photo_id = msg.photo[-1].file_id

    await bot.send_message(chat_id=msg.chat.id,
                           text=photo_id)


async def __send_video_file_id(message: Message):
    msgText = f'Хорошее видео, сохранил 😊'
    video_id = message.video.file_id
    if message.from_user.id in ADMIN_IDS:
        msgText += f'\n\nId видео файла: {video_id}'
    logger.success(f'Video_id: {video_id}')
    await message.reply(text=msgText)


async def send_document_file_id(msg: Message):
    bot: Bot = msg.bot
    doc_id = msg.document.file_id
    # markup = await kb_main(msg.from_user.id)

    await bot.send_message(chat_id=msg.chat.id,
                           text=doc_id)

def _register_media_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(send_photo_file_id, IsAdmin(), content_types=ContentType.PHOTO)
    dp.register_message_handler(__send_video_file_id, IsAdmin(), content_types=ContentType.VIDEO)
    dp.register_message_handler(send_document_file_id, IsAdmin(), content_types=ContentType.DOCUMENT)
