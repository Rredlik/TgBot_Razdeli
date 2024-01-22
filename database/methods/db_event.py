from datetime import datetime

from database.methods.db_main import parseOne, updateDB, parseAll
from database.methods.db_user import user_id_by_tg_id


async def create_new_event(event_name):
    event = await updateDB(
        "INSERT INTO 'events' (event_name, timestamp) VALUES (?, ?)",
        (event_name, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    )
    print(event)


async def add_event_member(event_id, telegram_id):
    user_id = await user_id_by_tg_id(telegram_id)
    await updateDB(
        "INSERT INTO 'event_members' (event_id, user_id) VALUES (?, ?)",
        (event_id, user_id)
    )


async def get_event_by_id(event_id):
    event = await parseOne(
        """SELECT * FROM 'events' where event_id = :event_id""",
        {'event_id': event_id})
    return event


async def get_app_id(user_id):
    application = await parseOne(
        """SELECT id FROM 'applications' where by_user = :user_id""",
        {'user_id': user_id})
    return application


async def check_app(user_id):
    application = await parseOne(
        """SELECT * FROM 'applications' where by_user = :user_id""",
        {'user_id': user_id})
    if application is None:
        await create_new_app(user_id)
        return False
    else:
        return True


async def get_all_completed_apps():
    applications = await parseAll(
        """SELECT * FROM 'applications' where is_complete = 1"""
    )
    return applications


async def get_one_not_in_work():
    applications = await parseAll(
        """SELECT * FROM 'applications' where is_complete = 1 and in_work = 0 limit 1"""
    )
    return applications[0]

async def create_new_app(user_id):
    await updateDB(
        "INSERT INTO 'applications' (by_user, timestamp) VALUES (?, ?)",
        (user_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    )


async def update_app_for_who(user_id, for_who):
    await updateDB(
        "UPDATE 'applications' SET for_who = :for_who WHERE by_user = :user_id",
        {'for_who': for_who, 'user_id': user_id}
    )


async def update_app_theme(user_id, theme):
    await updateDB(
        "UPDATE 'applications' SET theme = :theme WHERE by_user = :user_id",
        {'theme': theme, 'user_id': user_id}
    )


async def update_app_data(user_id, data_type, data):
    await updateDB(
        f"UPDATE 'applications' SET {data_type} = :data WHERE by_user = :user_id",
        {'data': data, 'user_id': user_id}
    )


async def update_app_data_by_id(app_id, data_type, data):
    await updateDB(
        f"UPDATE 'applications' SET {data_type} = :data WHERE id = :app_id",
        {'data': data, 'app_id': app_id}
    )