from aiogram import F, Router
from aiogram.types import Message
from loguru import logger

from bot.utils.database import save_bot_user

router = Router(name=__name__)


@router.message(F.text == '/start')
async def cmd_start(message: Message):
    """Команда /start"""
    # TODO: добавить определение роли пользователя (Пользователь, Администратор, Менеджер) Роли определяет администратор бота

    await save_bot_user(message)  # Сохраняем пользователя в базу данных и логируем
    logger.info(f'Пользователь {message.from_user.id} запустил бота')
    await message.answer('Пожалуйста, введите артикул товара, по которому вы хотите получить поддержку!')
