# -*- coding: utf-8 -*-
import uuid
from datetime import datetime

from aiogram import F
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message
from loguru import logger

from bot.keyboards.admin import main_keyboard_admin
from bot.states.manager import ManagerStates
from bot.states.user import UserStates
from bot.utils.database import save_bot_user, get_user_role, SupportTicket, TicketMessage

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
async def user_question_handler(message: Message, state: FSMContext, bot):
    user_text = message.text.strip()
    user_id = message.from_user.id
    username = f"@{message.from_user.username}" if message.from_user.username else "нет"

    # Создаём тикет
    ticket_id = f"TICKET_{uuid.uuid4().hex[:8].upper()}"
    ticket = SupportTicket.create(ticket_id=ticket_id, user_id=user_id)

    # Сохраняем первое сообщение
    TicketMessage.create(ticket=ticket, sender="user", text=user_text)

    SUPPORT_CHAT_ID = -1003502660042

    reply_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📨 Ответить", callback_data=f"reply:{ticket_id}"),
                InlineKeyboardButton(text="CloseOperation️ Закрыть", callback_data=f"close:{ticket_id}")
            ]
        ]
    )

    sent_msg = await bot.send_message(
        chat_id=SUPPORT_CHAT_ID,
        text=(
            f"📩 Новое обращение:\n"
            f"• Тикет: <code>{ticket_id}</code>\n"
            f"• ID: <code>{user_id}</code>\n"
            f"• Username: {username}\n\n"
            f"{user_text}"
        ),
        parse_mode="HTML",
        reply_markup=reply_kb
    )

    # Сохраняем message_id и chat_id в тикет
    ticket.message_id = sent_msg.message_id
    ticket.chat_id = sent_msg.chat.id
    ticket.save()

    await message.answer("✅ Ваше обращение передано в техподдержку.")
    await state.clear()


@router.callback_query(F.data.startswith("reply:"))
async def handle_reply_callback(callback: CallbackQuery, state: FSMContext):
    ticket_id = callback.data.split(":")[1]
    await state.update_data(current_ticket_id=ticket_id)
    await state.set_state(ManagerStates.reply_message)
    await callback.message.answer(f"Напишите ответ по тикету {ticket_id}:")
    await callback.answer()


@router.message(ManagerStates.reply_message)
async def send_reply_to_user(message: Message, state: FSMContext, bot):
    data = await state.get_data()
    ticket_id = data.get("current_ticket_id")

    if not ticket_id:
        await message.answer("❌ Ошибка: тикет не найден.")
        await state.clear()
        return

    try:
        ticket = SupportTicket.get(SupportTicket.ticket_id == ticket_id)
        if ticket.status != "open":
            await message.answer("⚠️ Этот тикет уже закрыт.")
            await state.clear()
            return

        # Сохраняем ответ менеджера
        TicketMessage.create(ticket=ticket, sender="manager", text=message.text)

        # Отправляем пользователю
        await bot.send_message(
            chat_id=ticket.user_id,
            text=f"📬 Ответ от поддержки:\n\n{message.text}"
        )

        # === Обновляем ИСХОДНОЕ сообщение с кнопками ===
        if ticket.chat_id and ticket.message_id:
            new_kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="📨 Ответить", callback_data=f"reply:{ticket_id}"),
                        InlineKeyboardButton(text="CloseOperation️ Закрыть", callback_data=f"close:{ticket_id}")
                    ]
                ]
            )
            try:
                await bot.edit_message_reply_markup(
                    chat_id=ticket.chat_id,
                    message_id=ticket.message_id,
                    reply_markup=new_kb
                )
            except Exception as e:
                logger.warning(f"Не удалось обновить кнопки тикета {ticket_id}: {e}")
        await message.answer("✅ Ответ отправлен.")

    except SupportTicket.DoesNotExist:
        await message.answer("❌ Тикет не найден.")
    except Exception as e:
        logger.exception(e)
        await message.answer("❌ Ошибка отправки.")

    await state.clear()


@router.callback_query(F.data.startswith("close:"))
async def close_ticket(callback: CallbackQuery, bot):
    ticket_id = callback.data.split(":")[1]
    try:
        ticket = SupportTicket.get(SupportTicket.ticket_id == ticket_id)
        if ticket.status == "closed":
            await callback.answer("Тикет уже закрыт.", show_alert=True)
            return

        ticket.status = "closed"
        ticket.closed_at = datetime.now()
        ticket.save()

        # Уведомляем пользователя
        await bot.send_message(
            chat_id=ticket.user_id,
            text="🔒 Ваше обращение закрыто. Спасибо за обращение!"
        )

        # Обновляем сообщение в чате
        # Убираем кнопки у исходного сообщения
        if ticket.chat_id and ticket.message_id:
            await bot.edit_message_reply_markup(
                chat_id=ticket.chat_id,
                message_id=ticket.message_id,
                reply_markup=None
            )

        await callback.answer("✅ Тикет закрыт.")

    except SupportTicket.DoesNotExist:
        await callback.answer("Тикет не найден.", show_alert=True)
