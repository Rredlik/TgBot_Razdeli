from datetime import datetime

from loguru import logger

from database.main import connectToDB


async def parseAll(command, parameters=None):
    async with connectToDB() as db:
        try:
            answ = await db.execute(
                command, parameters
            )
            await db.commit()
            result = await answ.fetchall()
            return result
        except Exception as er:
            logger.error(er)
        finally:
            await db.commit()


async def parseOne(command, parameters=None):
    async with connectToDB() as db:
        try:
            answ = await db.execute(
                command, parameters
            )
            await db.commit()
            result = await answ.fetchone()
            return result
        except Exception as er:
            logger.error(er)
        finally:
            await db.commit()


async def updateDB(command, parameters=None):
    async with connectToDB() as db:
        try:
            data = await db.execute(
                command, parameters
            )
            await db.commit()
            return data
        except Exception as er:
            logger.error(er)
        finally:
            await db.commit()
