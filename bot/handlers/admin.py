# -*- coding: utf-8 -*-
from aiogram import F
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import FSInputFile
from aiogram.types import Message
from loguru import logger
from bot.keyboards.admin import set_role_keyboard
from bot.states.admin import Admin
from bot.utils.database import update_user_role, get_all_bot_users
import asyncio

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

    # Обновляем роль в базе данных
    success = update_user_role(id_user, role)

    role_labels = {
        "user": "👤 Пользователь",
        "admin": "🛡️ Администратор",
        "manager": "💼 Менеджер"
    }

    if success:
        text = f"✅ Роль {role_labels[role]} успешно назначена пользователю с ID {id_user}."
    else:
        text = f"❌ Пользователь с ID {id_user} не найден в базе данных. Сначала он должен запустить бота."

    await callback.message.edit_text(text)
    await callback.answer()
    await state.clear()


@router.callback_query(F.data == "get_log")
async def log(callback: CallbackQuery, state: FSMContext, bot):
    """
    Отправляет лог файл администратору.
    :param callback:
    :param state:
    :param bot:
    :return:
    """

    await state.clear()

    try:
        document = FSInputFile("logs/logs.log")
        await callback.message.answer_document(
            document=document,
            caption="📄 Лог файл с ошибками.",
            parse_mode="HTML"
        )
    except FileNotFoundError:
        await callback.message.answer("❌ Файл логов не найден.")
    except Exception as e:
        logger.exception(e)

    await callback.answer()  # Обязательно: подтверждаем callback
    await state.clear()


@router.callback_query(F.data == "miss_message")
async def miss_message(callback: CallbackQuery, state: FSMContext, bot):
    """
    Отправляет сообщения пользователям бота, которые ранее взаимодействовали с ботом.
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    await state.clear()

    try:
        await callback.message.answer("Введите сообщение которое хотите отправить всем пользователям")
        await state.set_state(Admin.message_text)
        await callback.answer()
    except Exception as e:
        logger.exception(e)


@router.message(Admin.message_text)
async def send_message(message: Message, state: FSMContext, bot):
    """
    Отправляет сообщение всем пользователям из базы данных.
    """
    try:
        text = message.text.strip()
        if not text:
            await message.answer("❌ Необходимо ввести текст сообщения.")
            return

        user_ids = get_all_bot_users()  # Получаем все ID пользователей из базы данных
        total = len(user_ids)
        sent = 0
        failed = 0

        await message.answer(f"📤 Начинаю рассылку {total} пользователям...")

        for user_id in user_ids:
            try:
                await bot.send_message(chat_id=user_id, text=text)
                sent += 1
            except Exception as e:
                logger.exception(e)
                failed += 1

            await asyncio.sleep(0.04)  # Задержка для ограничения частоты запросов

        await message.answer(
            f"✅ Рассылка завершена!\n"
            f"Отправлено: {sent}\n"
            f"Ошибок: {failed}"
        )
        await state.clear()

    except Exception as e:
        logger.exception(e)
