import re
from datetime import datetime
import random
import string

from database.methods.db_main import parseOne, updateDB, parseAll
from database.methods.db_user import user_id_by_tg_id


async def get_event_by_id(event_id):
    event = await parseOne(
        """SELECT * FROM 'events' where event_id = :event_id""",
        {'event_id': event_id})
    return event


async def get_event_members(event_id):
    members = await parseAll(
        """select * from users where user_id in (SELECT user_id
                        FROM 'event_members' where event_id = :event_id);""",
        {'event_id': event_id}
    )
    return members


async def get_transaction_by_id(transaction_id):
    transaction = await parseOne(
        """SELECT * FROM 'transactions' where transaction_id = :transaction_id""",
        {'transaction_id': transaction_id})
    return transaction


async def get_event_transactions(event_id):
    members = await parseAll(
        """select * from transactions where event_id = :event_id;""",
        {'event_id': event_id}
    )
    return members


async def get_all_user_events(telegram_id):
    events = await parseAll(
        """select * from events where event_id in 
                        (SELECT event_id FROM 'event_members' where user_id = 
                            (SELECT user_id FROM 'users' where telegram_id = :telegram_id))""",
        {'telegram_id': telegram_id}
    )
    return events


async def get_all_transaction_payers(transaction_id):
    events = await parseAll(
        """select user_id from transaction_members where transaction_id = :transaction_id""",
        {'transaction_id': transaction_id}
    )
    return events


async def create_new_event(event_name):
    event_id = ''.join([random.choice(string.digits) for n in range(7)])
    await updateDB(
        "INSERT INTO 'events' (event_id, event_name, event_date) VALUES (?, ?, ?)",
        (event_id, event_name, datetime.now().strftime('%d.%m.%Y %H:%M'))
    )
    return event_id


async def add_event_member(event_id, telegram_id):
    user_id = await user_id_by_tg_id(telegram_id)
    await updateDB(
        "INSERT INTO 'event_members' (event_id, user_id) VALUES (?, ?)",
        (event_id, user_id)
    )


async def create_transaction(user_id, event_id, transaction_name, amount):
    transaction_id = ''.join([random.choice(string.digits) for n in range(10)])
    await updateDB(
        "INSERT INTO 'transactions' (transaction_id, user_id, event_id, transaction_name, amount) "
        "VALUES (?, ?, ?, ?, ?)",
        (transaction_id, user_id, event_id, transaction_name, amount)
    )
    return transaction_id


async def add_transaction_members(transaction_id, members_list):  # Должен вводиться массив из user_id
    command = '''INSERT INTO 'transaction_members' (transaction_id, user_id) VALUES '''
    for member in members_list:
        command += f'''({transaction_id}, {member}), '''
    command = re.sub(', $', ';', command)
    await updateDB(command)


async def add_transaction_debtors(payer_id, members_list, amount, transaction_id, event_id):
    # Должен вводиться массив из user_id
    command = '''INSERT INTO 'debts' \
                (payer_id, debtor_id, debt_amount, transaction_id, event_id) VALUES '''
    debt_amount = round(amount / len(members_list), 2)
    for member in members_list:
        debtor_id = member
        if debtor_id != int(payer_id):
            command += f'''({payer_id}, {debtor_id}, {debt_amount}, {transaction_id}, {event_id}), '''
    command = re.sub(', $', ';', command)
    await updateDB(command)


async def get_payer_debtors(event_id, payer_id):
    events = await parseAll(
            """select payer_id, debtor_id, users.user_login, sum(debt_amount) as debt_amount 
            from debts 
            join users on debts.debtor_id=users.user_id
            where event_id = :event_id and payer_id = :payer_id group by debtor_id;""",
            {'event_id': event_id, 'payer_id': payer_id}
        )
    return events


async def get_debt_to_payers(event_id, debtor_id):
    events = await parseAll(
            """select payer_id, debtor_id, users.user_login, sum(debt_amount) as debt_amount 
            from debts 
            join users on debts.payer_id=users.user_id
            where event_id = :event_id and debtor_id = :debtor_id group by debtor_id;""",
            {'event_id': event_id, 'debtor_id': debtor_id}
        )
    return events
# async def get_app_id(user_id):
#     application = await parseOne(
#         """SELECT id FROM 'applications' where by_user = :user_id""",
#         {'user_id': user_id})
#     return application
#
#
# async def check_app(user_id):
#     application = await parseOne(
#         """SELECT * FROM 'applications' where by_user = :user_id""",
#         {'user_id': user_id})
#     if application is None:
#         await create_new_app(user_id)
#         return False
#     else:
#         return True
#
#
# async def get_all_completed_apps():
#     applications = await parseAll(
#         """SELECT * FROM 'applications' where is_complete = 1"""
#     )
#     return applications
#
#
# async def get_one_not_in_work():
#     applications = await parseAll(
#         """SELECT * FROM 'applications' where is_complete = 1 and in_work = 0 limit 1"""
#     )
#     return applications[0]
#
# async def create_new_app(user_id):
#     await updateDB(
#         "INSERT INTO 'applications' (by_user, timestamp) VALUES (?, ?)",
#         (user_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
#     )
#
#
# async def update_app_for_who(user_id, for_who):
#     await updateDB(
#         "UPDATE 'applications' SET for_who = :for_who WHERE by_user = :user_id",
#         {'for_who': for_who, 'user_id': user_id}
#     )
#
#
# async def update_app_theme(user_id, theme):
#     await updateDB(
#         "UPDATE 'applications' SET theme = :theme WHERE by_user = :user_id",
#         {'theme': theme, 'user_id': user_id}
#     )
#
#
# async def update_app_data(user_id, data_type, data):
#     await updateDB(
#         f"UPDATE 'applications' SET {data_type} = :data WHERE by_user = :user_id",
#         {'data': data, 'user_id': user_id}
#     )
#
#
# async def update_app_data_by_id(app_id, data_type, data):
#     await updateDB(
#         f"UPDATE 'applications' SET {data_type} = :data WHERE id = :app_id",
#         {'data': data, 'app_id': app_id}
#     )
