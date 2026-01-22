# -*- coding: utf-8 -*-
from aiogram import F, Router
from aiogram.types import Message
from loguru import logger

from bot.utils.database import save_bot_user

router = Router(name=__name__)


@router.message(F.text == '/start')
async def cmd_start(message: Message):
    """Команда /start"""
    # TODO.md: добавить определение роли пользователя (Пользователь, Администратор, Менеджер) Роли определяет администратор бота

    await save_bot_user(message)  # Сохраняем пользователя в базу данных и логируем
    logger.info(f'Пользователь {message.from_user.id} запустил бота')

    if message.from_user.id == 535185511:
        await message.answer('Привет, Админ!')

    if message.from_user.id == 7181118530:
        await message.answer('Привет, Менеджер!')

    await message.answer('Пожалуйста, введите артикул товара, по которому вы хотите получить поддержку!')
