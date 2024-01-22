import aiosqlite
from loguru import logger

PATH_DATABASE = "main.db"


def connectToDB():
    connection = aiosqlite.connect(PATH_DATABASE)
    return connection


async def create_db():
    async with connectToDB() as db:

        try:
            users = await (await db.execute("PRAGMA table_info(users)")).fetchall()
            applications = await (await db.execute("PRAGMA table_info(applications)")).fetchall()
            config = await (await db.execute("PRAGMA table_info(config)")).fetchall()

            if len(users) == 7:
                logger.success("DB was found (1/5)")
            else:
                logger.warning("DB was not found (1/5) | Creating...")
                await db.execute('create table users('
                                 'user_id  INTEGER not null primary key autoincrement unique,'
                                 'telegram_id INTEGER key unique,'
                                 'is_admin text default 0,'
                                 'user_name text default 0,'
                                 'user_login text default 0,'
                                 'phone_number text default 0,'
                                 'reg_date INTEGER not null)')
                logger.success("DB was create (1/5)")

            if len(applications) == 3:
                logger.success("DB was found (2/5)")
            else:
                logger.warning("DB was not found (2/5) | Creating...")
                await db.execute('create table events('
                                 'event_id    TEXT not null unique,'
                                 'event_name  TEXT default 0,'
                                 'event_date    INTEGER not null)')
                logger.success("DB was create (2/5)")

            if len(config) == 2:
                logger.success("DB was found (3/5)")
            else:
                logger.warning("DB was not found (3/5) | Creating...")
                await db.execute('create table event_members('
                                 'event_id TEXT not null,'
                                 'user_id  TEXT not null)')
                logger.success("DB was create (3/5)")

            if len(config) == 5:
                logger.success("DB was found (4/5)")
            else:
                logger.warning("DB was not found (4/5) | Creating...")
                await db.execute('create table transactions('
                                 'transaction_id   TEXT not null unique,'
                                 'user_id          TEXT,'
                                 'event_id         TEXT,'
                                 'transaction_name TEXT,'
                                 'amount           integer)')
                logger.success("DB was create (4/5)")

            if len(config) == 2:
                logger.success("DB was found (5/5)")
            else:
                logger.warning("DB was not found (5/5) | Creating...")
                await db.execute('create table transaction_members('
                                 'transaction_id   TEXT,'
                                 'user_id          TEXT)')
                logger.success("DB was create (5/5)")
        except Exception as er:
            logger.error(f"{er}")
        finally:
            await db.commit()
