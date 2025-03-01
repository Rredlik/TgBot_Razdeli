import asyncio

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger

from config import ADMIN_IDS
from config.env import Env
from database.main import create_db
from database.methods.db_user import make_new_admin
from filters import register_all_filters
from handlers.admin import register_admin_handlers
from handlers.keyboards import kb_main_menu
from handlers.user.main import register_users_handlers
from handlers.user.register import is_registered
from handlers import router


# from misc.scheduler_jobs import register_jobs


async def register_all_handlers(dp: Dispatcher) -> None:
    handlers = (
        register_admin_handlers,
        register_users_handlers
    )
    for handler in handlers:
        handler(dp)


async def __on_start_up(dp: Dispatcher):
    # await register_database()
    await create_db()
    # await register_all_filters(dp)
    #await register_all_handlers(dp)
    # await register_jobs(dp)

    logger.success("Bot started!")
    logger.success("developed by @skidikis")
    logger.info(f"Admins list: {ADMIN_IDS}")
    # logger.info(f"Channel list: {CHANNEL_LINK}")

    for admin_id in ADMIN_IDS:
        await is_registered(user_id=admin_id)
        await make_new_admin(admin_id)

    await dp.send_message(chat_id=351931465, text='Бот перезапущен!\n /start',
                              reply_markup=await kb_main_menu(351931465))


async def __on_shutdown(dp):
    logger.info("Bot stopped!\n")


async def main():
    bot = Bot(token=Env.BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())  # надо изучить как не стирать состояния диспетчера при перезапуске
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(),
                           on_startup=__on_start_up, on_shutdown=__on_shutdown)


def start_telegram_bot():
    # logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    #                     level=logging.DEBUG,)
    # logger = logging.getLogger(__name__)
    # bot = Bot(token=Env.BOT_TOKEN, parse_mode='HTML')
    # dp = Dispatcher(bot, storage=MemoryStorage())
    asyncio.run(main())
    #executor.start_polling(dp,  skip_updates=True, on_startup=__on_start_up, on_shutdown=__on_shutdown)
