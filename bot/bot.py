from aiogram import Bot
import os
from dotenv import load_dotenv

load_dotenv()

# Настройка сессии с пользовательским агентом
bot = Bot(token=os.getenv('BOT_TOKEN'), session=None)