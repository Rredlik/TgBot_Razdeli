from aiogram import Dispatcher, Bot
from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.handler import CancelHandler
from aiogram.types import Message, ChatMemberStatus, InlineKeyboardMarkup, InlineKeyboardButton

from config import *
from database.methods.db_user import parseAllAdmins


class IsSubscriber(BoundFilter):
    async def check(self, message: Message):
        bot: Bot = message.bot
        subscribed = 0
        for chat_id in CHANNEL_ID:
            sub_status = await bot.get_chat_member(chat_id=chat_id, user_id=message.from_user.id)

            if sub_status.status != ChatMemberStatus.LEFT:
                subscribed += 1

        if subscribed == len(CHANNEL_ID):
            return True
        else:
            return False
            raise CancelHandler()


class IsAdmin(BoundFilter):
    async def check(self, message: Message):
        admins_pack = await parseAllAdmins()
        admins = []
        for admin in admins_pack:
            admins.append(int(admin[0]))
        return True if message.from_user.id in admins else False


class NotAdmin(BoundFilter):
    async def check(self, message: Message) -> bool:
        return False if message.from_user.id in ADMIN_IDS else True


async def register_all_filters(dp: Dispatcher):
    filters = (
        NotAdmin,
        IsAdmin,
        IsSubscriber
    )
    for filter in filters:
        dp.bind_filter(filter)
