from aiogram import Bot
from aiogram.types import CallbackQuery, ParseMode, InlineKeyboardMarkup, Message


async def send_message(query: CallbackQuery, text: str, markup: InlineKeyboardMarkup = None):
    bot: Bot = query.bot
    if type(query) is not Message:
        await bot.answer_callback_query(query.id)
    await bot.send_message(chat_id=query.from_user.id,
                           text=text,
                           reply_markup=markup)
