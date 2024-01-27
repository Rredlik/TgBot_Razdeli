import aiosqlite
from loguru import logger

PATH_DATABASE = "main.db"


def connectToDB():
    connection = aiosqlite.connect(PATH_DATABASE)
    return connection


async def create_db():
    async with connectToDB() as db:

        try:
            tables_count = 6

            users = await (await db.execute("PRAGMA table_info(users)")).fetchall()
            events = await (await db.execute("PRAGMA table_info(events)")).fetchall()
            event_members = await (await db.execute("PRAGMA table_info(event_members)")).fetchall()
            transactions = await (await db.execute("PRAGMA table_info(transactions)")).fetchall()
            transaction_members = await (await db.execute("PRAGMA table_info(transaction_members)")).fetchall()
            debts = await (await db.execute("PRAGMA table_info(debts)")).fetchall()

            current_table = 1
            if len(users) == 7:
                logger.success(f"DB was found ({current_table}/{tables_count})")
            else:
                logger.warning(f"DB was not found ({current_table}/{tables_count}) | Creating...")
                await db.execute('create table users('
                                 'user_id       INTEGER not null primary key autoincrement unique,'
                                 'telegram_id   INTEGER key unique,'
                                 'is_admin      text default 0,'
                                 'user_name     text default 0,'
                                 'user_login    text default 0,'
                                 'phone_number  text default 0,'
                                 'reg_date      INTEGER not null)')
                logger.success(f"DB was create ({current_table}/{tables_count})")

            current_table += 1
            if len(events) == 3:
                logger.success(f"DB was found ({current_table}/{tables_count})")
            else:
                logger.warning(f"DB was not found ({current_table}/{tables_count}) | Creating...")
                await db.execute('create table events('
                                 'event_id      TEXT not null unique,'
                                 'event_name    TEXT default 0,'
                                 'event_date    INTEGER not null)')
                logger.success(f"DB was create ({current_table}/{tables_count})")

            current_table += 1
            if len(event_members) == 2:
                logger.success(f"DB was found ({current_table}/{tables_count})")
            else:
                logger.warning(f"DB was not found ({current_table}/{tables_count}) | Creating...")
                await db.execute('create table event_members('
                                 'event_id TEXT not null,'
                                 'user_id  TEXT not null)')
                logger.success(f"DB was create ({current_table}/{tables_count})")

            current_table += 1
            if len(transactions) == 5:
                logger.success(f"DB was found ({current_table}/{tables_count})")
            else:
                logger.warning(f"DB was not found ({current_table}/{tables_count}) | Creating...")
                await db.execute('create table transactions('
                                 'transaction_id   TEXT not null primary key unique ,'
                                 'user_id          TEXT,'
                                 'event_id         TEXT,'
                                 'transaction_name TEXT,'
                                 'amount           integer)')
                logger.success(f"DB was create ({current_table}/{tables_count})")

            current_table += 1
            if len(transaction_members) == 2:
                logger.success(f"DB was found ({current_table}/{tables_count})")
            else:
                logger.warning(f"DB was not found ({current_table}/{tables_count}) | Creating...")
                await db.execute('create table transaction_members('
                                 'transaction_id   TEXT,'
                                 'user_id          TEXT)')
                logger.success(f"DB was create ({current_table}/{tables_count})")

            current_table += 1
            if len(debts) == 7:
                logger.success(f"DB was found ({current_table}/{tables_count})")
            else:
                logger.warning(f"DB was not found (5/{tables_count}) | Creating...")
                await db.execute('create table debts('
                                 'debt_id           INTEGER not null primary key autoincrement unique,'
                                 'payer_id          TEXT,'
                                 'debtor_id         TEXT,'
                                 'debt_amount       TEXT,'
                                 'transaction_id    TEXT,'
                                 'event_id          TEXT),'
                                 'is_payed INT default 0 not null')
                logger.success(f"DB was create ({current_table}/{tables_count})")
        except Exception as er:
            logger.error(f"{er}")
        finally:
            await db.commit()
