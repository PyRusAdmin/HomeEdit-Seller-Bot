# -*- coding: utf-8 -*-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_keyboard_admin() -> InlineKeyboardMarkup:
    """
    Главная клавиатура админа
    :return: InlineKeyboardMarkup
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🎯 Присвоить роль", callback_data="set_role"),
                InlineKeyboardButton(text="📄 Получить лог файл", callback_data="get_log")
            ],
            [
                InlineKeyboardButton(text="📩 Рассылка сообщений", callback_data="miss_message"),
            ],
        ]
    )


def set_role_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора роли
    :return: InlineKeyboardMarkup
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👤 Пользователь", callback_data="user"),
                InlineKeyboardButton(text="🛡️ Администратор", callback_data="admin")
            ],
            [
                InlineKeyboardButton(text="💼 Менеджер", callback_data="manager")
            ],
        ]
    )
