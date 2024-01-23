from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from loader import bot


async def send_callMessage(call: CallbackQuery, text: str, reply_markup: InlineKeyboardMarkup = None):
    if type(call) is not Message:
        await bot.answer_callback_query(call.id)
    await bot.send_message(chat_id=call.from_user.id,
                           text=text,
                           reply_markup=reply_markup)
