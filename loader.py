# import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config.env import Env

bot = Bot(token=Env.BOT_TOKEN, parse_mode='HTML')
dp = Dispatcher(bot, storage=MemoryStorage())
# loop = asyncio.get_event_loop()
# dp = Dispatcher(bot, storage=storage, loop=loop)