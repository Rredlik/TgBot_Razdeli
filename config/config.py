# import aiohttp
import aiosqlite
import pendulum as pendulum
from .env import Env

ADMIN_IDS = Env.ADMINS  # 351931465
ADMIN_LINK = ['@skidikis']

# [-1001665320015]  # ачо а ничо
# [-1001681978222]  # OKO NETWORK  https://t.me/okobrand
CHANNEL_ID = -1001681978222  # Env.channel_id  # OKO NETWORK
CHANNEL_LINK = 'https://t.me/okobrand'  # Env.channel_link

# first_photo = Env.first_photo
# self_doc = Env.file_self
# child_doc = Env.file_child


# DESCRIPTION = 'СЕМЕЙНЫЙ КОНСУЛЬТАНТ ПО ТАЛАНТАМ'

def set_datetime(record):
    record['extra']['datetime'] = pendulum.now('Asia/Yekaterinburg').strftime('%d-%m-%Y %H:%M:%S')
