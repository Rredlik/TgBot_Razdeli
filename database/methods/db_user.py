import re
from datetime import datetime
import random
import string

from database.methods.db_main import parseAll, parseOne, updateDB


async def update_user_data(telegram_id, data_name, data):
    await updateDB(
        f"UPDATE 'users' SET {data_name} = :data WHERE telegram_id = :telegram_id",
        {'data': data, 'telegram_id': telegram_id}
    )

async def parseAllUsers():
    allUsers = await parseAll("SELECT telegram_id FROM 'users'")
    return allUsers


async def parseAllAdmins():
    allUsers = await parseAll("SELECT telegram_id FROM 'users' where is_admin = 1")
    return allUsers


async def user_id_by_tg_id(telegram_id):
    user_id = await parseOne("SELECT user_id FROM 'users' where telegram_id = :telegram_id",
                              {"telegram_id": telegram_id})
    return int(user_id[0])


async def add_new_bot(bot_name):
    telegram_id = ''.join([random.choice(string.digits) for n in range(10)])
    await updateDB(
                "INSERT INTO 'users' (telegram_id, user_name, reg_date) VALUES (?, ?, ?)",
                (telegram_id, bot_name, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            )
    return telegram_id


# async def is_subscriber(user_id):
#     have_gift = await parseOne("SELECT is_subscriber FROM 'users' where telegram_id = :user_id",
#                               {"user_id": user_id})
#     return int(have_gift[0])


# async def update_sub_status(user_id, status):
#     await updateDB(
#         "UPDATE 'users' SET is_subscriber = :status WHERE telegram_id = :user_id",
#         {'user_id': user_id, 'status': status}
#     )


async def isAdmin(user_id):
    is_admin = await parseOne("SELECT is_admin FROM 'users' where telegram_id = :user_id",
                              {"user_id": user_id})
    return int(is_admin[0])


async def make_new_admin(user_id):
    await updateDB(
        "UPDATE 'users' SET is_admin = 1 WHERE telegram_id = :user_id",
        {'user_id': user_id}
    )
