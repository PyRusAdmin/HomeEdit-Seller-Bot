# -*- coding: utf-8 -*-
from aiogram import F
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loguru import logger

from bot import bot
from bot.keyboards.admin import main_keyboard_admin
from bot.keyboards.admin import set_role_keyboard  # ← убедитесь, что путь правильный
from bot.states.admin import Admin
from bot.states.user import UserStates
from bot.utils.database import save_bot_user, get_user_role

router = Router(name=__name__)


@router.message(F.text == '/start')
async def cmd_start(message: Message, state: FSMContext):
    """Команда /start"""

    await state.clear()
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
        await state.set_state(UserStates.user_question)


@router.message(UserStates.user_question)
async def user_question_handler(message: Message, state: FSMContext):
    """Проверяет ID и показывает клавиатуру выбора роли."""
    user_text = message.text.strip()
    user_id = message.from_user.id
    username = f"@{message.from_user.username}" if message.from_user.username else "нет"

    SUPPORT_CHAT_ID = -1003502660042  # ID ЧАТА

    try:
        await bot.send_message(
            chat_id=SUPPORT_CHAT_ID,
            text=(
                f"📩 Новое обращение от пользователя:\n"
                f"• ID: <code>{user_id}</code>\n"
                f"• Username: {username}\n"
                f"• Сообщение:\n\n{user_text}"
            ),
            parse_mode="HTML"
        )
        await message.answer("✅ Ваше обращение передано в техническую поддержку.")
    except Exception as e:
        logger.exception(e)
        await message.answer("❌ Не удалось отправить обращение. Попробуйте позже.")

    await state.clear()
