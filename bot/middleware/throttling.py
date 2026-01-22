from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Message
import time


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, throttle_time: int = 1):
        self.throttle_time = throttle_time
        self.users = {}

    async def __call__(self, handler, event: Message, data):
        user_id = event.from_user.id

        if user_id in self.users:
            if time.time() - self.users[user_id] < self.throttle_time:
                await event.answer("Не так быстро!")
                return

        self.users[user_id] = time.time()
        return await handler(event, data)
