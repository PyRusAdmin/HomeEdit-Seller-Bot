# -*- coding: utf-8 -*-
from aiogram import F
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message
from loguru import logger

from bot import bot
from bot.keyboards.admin import main_keyboard_admin
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

    # Создаём кнопку "Ответить"
    reply_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📨 Ответить",
                    callback_data=f"reply:{user_id}"
                )
            ]
        ]
    )

    try:
        await bot.send_message(
            chat_id=SUPPORT_CHAT_ID,
            text=(
                f"📩 Новое обращение:\n"
                f"• ID: <code>{user_id}</code>\n"
                f"• Username: {username}\n\n"
                f"{user_text}"
            ),
            parse_mode="HTML",
            reply_markup=reply_kb
        )
        await message.answer("✅ Ваше обращение передано в техническую поддержку.")
    except Exception as e:
        logger.exception(e)
        await message.answer("❌ Не удалось отправить обращение. Попробуйте позже.")

    await state.clear()


@router.callback_query(F.data.startswith("reply:"))
async def handle_reply_callback(callback: CallbackQuery, state: FSMContext):
    # Извлекаем user_id из callback_data
    user_id = int(callback.data.split(":")[1])

    await state.update_data(reply_to_user_id=user_id)
    await state.set_state(ManagerStates.reply_message)

    await callback.message.answer(
        f"Напишите ответ пользователю (ID: {user_id}):"
    )
    await callback.answer()