import asyncio
from aiogram import BaseMiddleware
from aiogram.types import Message
from collections import defaultdict
import time

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit=1.0):
        self.rate_limit = rate_limit
        self.last_time = defaultdict(float)

    async def __call__(self, handler, event: Message, data):
        user_id = event.from_user.id
        now = time.time()
        if now - self.last_time[user_id] < self.rate_limit:
            return
        self.last_time[user_id] = now
        return await handler(event, data)