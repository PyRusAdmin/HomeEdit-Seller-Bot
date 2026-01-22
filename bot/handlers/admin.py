# -*- coding: utf-8 -*-
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from loguru import logger

from bot.states.admin import Admin

router = Router(name=__name__)


# Обработка нажатия на inline-кнопку "Присвоить роль"
@router.callback_query(F.data == "set_role")
async def set_role_start(callback: CallbackQuery, state: FSMContext):
    """
    Запускает процесс назначения роли: запрашивает ID пользователя.
    """
    try:
        await state.clear()
        await callback.message.answer("Введите id пользователя бота для назначения роли:")
        await state.set_state(Admin.id_user)
        await callback.answer()  # Подтверждаем нажатие кнопки (убираем "часики")
    except Exception as e:
        logger.exception(e)


# Обработка ввода ID пользователя
@router.message(Admin.id_user)
async def process_id_user(message: Message, state: FSMContext):
    id_user = message.text.strip()
    if not id_user.isdigit():
        await message.answer("Пожалуйста, введите корректный числовой ID пользователя.")
        return

    logger.info(f"Пользователь {message.from_user.id} назначил роль пользователю {id_user}")
    # Здесь можно добавить логику сохранения роли, например:
    # await assign_role_to_user(int(id_user))

    await message.answer(f"Роль будет назначена пользователю с ID: {id_user}")
    await state.clear()
