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
                InlineKeyboardButton(text="Присвоить роль", callback_data="set_role")
            ]
        ]
    )
