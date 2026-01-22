# -*- coding: utf-8 -*-
import asyncio
from bot.bot import bot
from bot.dispatcher import dispatcher
from loguru import logger
from bot.utils.database import db, BotUsers

logger.add('logs/logs.log', rotation='10 MB', compression='zip')


class App:
    def __init__(self):
        self.dp = dispatcher
        self.bot = bot

    async def start(self):
        logger.info('Бот запущен...')
        # Создаем таблицы в базе данных
        db.connect()
        db.create_tables([BotUsers])
        try:
            await dispatcher.start_polling(bot)
        except Exception as e:
            logger.exception(e)
        finally:
            await bot.session.close()


if __name__ == '__main__':
    app = App()
    asyncio.run(app.start())
