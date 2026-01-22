# -*- coding: utf-8 -*-
from aiogram import F, Router
from aiogram.types import Message
from loguru import logger

from bot.keyboards.admin import main_keyboard_admin
from bot.utils.database import save_bot_user, get_user_role

router = Router(name=__name__)


@router.message(F.text == '/start')
async def cmd_start(message: Message):
    """Команда /start"""
    # TODO.md: добавить определение роли пользователя (Пользователь, Администратор, Менеджер) Роли определяет администратор бота

    await save_bot_user(message)  # Сохраняем пользователя в базу данных и логируем
    logger.info(f'Пользователь {message.from_user.id} запустил бота')

    # Получаем роль из базы данных
    role = get_user_role(message.from_user.id)

    if role == "admin":
        await message.answer('Привет, Админ!', reply_markup=main_keyboard_admin())
    elif role == "manager":
        await message.answer('Привет, Менеджер!')
    else:  # role == "user" или любой другой
        await message.answer(
            'Пожалуйста, введите артикул товара 📦, по которому вы хотите получить поддержку! 💬',
            parse_mode='HTML'
        )
