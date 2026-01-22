# -*- coding: utf-8 -*-
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.keyboards.admin import set_role_keyboard  # ← убедитесь, что путь правильный
from bot.states.admin import Admin

router = Router(name=__name__)


@router.callback_query(F.data == "set_role")
async def set_role_start(callback: CallbackQuery, state: FSMContext):
    """Запрашивает ID пользователя."""
    await state.clear()
    await callback.message.answer("Введите ID пользователя для назначения роли:")
    await state.set_state(Admin.id_user)
    await callback.answer()


@router.message(Admin.id_user)
async def process_id_user(message: Message, state: FSMContext):
    """Проверяет ID и показывает клавиатуру выбора роли."""
    id_user = message.text.strip()
    if not id_user.isdigit():
        await message.answer("❌ Некорректный ID. Введите число.")
        return

    await state.update_data(id_user=int(id_user))  # Сохраняем ID как число
    await message.answer(
        f"Выберите роль для пользователя с ID {id_user}:",
        reply_markup=set_role_keyboard()
    )
    await state.set_state(Admin.role)  # Переходим к следующему состоянию


@router.callback_query(Admin.role, F.data.in_({"user", "admin", "manager"}))
async def process_role_selection(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает выбор роли и завершает процесс."""
    role = callback.data  # "user", "admin" или "manager"
    data = await state.get_data()
    id_user = data["id_user"]

    # Здесь вы можете сохранить роль в БД (пример ниже)
    # await assign_role_to_user(id_user, role)

    role_labels = {
        "user": "👤 Пользователь",
        "admin": "🛡️ Администратор",
        "manager": "💼 Менеджер"
    }

    await callback.message.edit_text(
        f"✅ Роль {role_labels[role]} успешно назначена пользователю с ID {id_user}."
    )
    await callback.answer()
    await state.clear()