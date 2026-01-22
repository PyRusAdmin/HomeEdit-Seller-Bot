import asyncio
from bot.bot import bot
from bot.dispatcher import dispatcher


class App:
    def __init__(self):
        self.dp = dispatcher
        self.bot = bot

    async def start(self):
        print('Bot is starting...')
        try:
            await dispatcher.start_polling(bot)
        except Exception as e:
            print(f'Error: {e}')
        finally:
            await bot.session.close()


if __name__ == '__main__':
    app = App()
    asyncio.run(app.start())