import time
from datetime import datetime


# Получение unix времени
async def get_unix(full: bool = False) -> int:
    if full:
        return time.time_ns()
    else:
        return int(time.time())
