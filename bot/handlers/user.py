# bot/handlers/user.py
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from loguru import logger
import uuid
from datetime import datetime

from bot.utils.database import (
    save_bot_user,
    get_user_role,
    BotUsers,
    SupportTicket,
    TicketMessage,
)
from bot.states.manager import ManagerStates
from bot.keyboards.admin import main_keyboard_admin

router = Router(name=__name__)

SUPPORT_CHAT_ID = -1003502660042  # вынесено в константу


@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await save_bot_user(message)
    logger.info(f"Пользователь {message.from_user.id} запустил бота")

    role = get_user_role(message.from_user.id)

    if role == "admin":
        await message.answer("Привет, Админ!", reply_markup=main_keyboard_admin())
    elif role == "manager":
        await message.answer("Привет, Менеджер!")
    else:
        # Проверяем открытый тикет
        open_ticket = SupportTicket.get_or_none(
            (SupportTicket.user_id == message.from_user.id) &
            (SupportTicket.status == "open")
        )
        if open_ticket:
            await message.answer(
                "У вас уже есть активное обращение. Дополните его прямо здесь."
            )
        else:
            await message.answer(
                "Пожалуйста, опишите ваш вопрос или проблему:",
                parse_mode="HTML"
            )


@router.message(F.text)
async def handle_user_message(message: Message, bot):
    user_id = message.from_user.id
    role = get_user_role(user_id)

    if role in ("admin", "manager"):
        return  # игнорируем

    # Ищем открытый тикет
    ticket = SupportTicket.get_or_none(
        (SupportTicket.user_id == user_id) &
        (SupportTicket.status == "open")
    )

    if ticket:
        # Добавляем к существующему
        TicketMessage.create(ticket=ticket, sender="user", text=message.text.strip())
        await bot.send_message(
            chat_id=ticket.chat_id,
            text=f"🔁 Новое сообщение:\n\n{message.text}",
            reply_to_message_id=ticket.message_id,
        )
        await message.answer("✅ Сообщение добавлено к вашему обращению.")
        return

    # Создаём новый тикет
    ticket_id = f"TICKET_{uuid.uuid4().hex[:8].upper()}"
    user_text = message.text.strip()
    username = f"@{message.from_user.username}" if message.from_user.username else "нет"

    ticket = SupportTicket.create(
        ticket_id=ticket_id,
        user_id=user_id,
        status="open"
    )
    TicketMessage.create(ticket=ticket, sender="user", text=user_text)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📨 Ответить", callback_data=f"reply:{ticket_id}"),
            InlineKeyboardButton(text="CloseOperation️ Закрыть", callback_data=f"close:{ticket_id}")
        ]
    ])

    sent = await bot.send_message(
        chat_id=SUPPORT_CHAT_ID,
        text=(
            f"📩 Новое обращение:\n"
            f"• Тикет: <code>{ticket_id}</code>\n"
            f"• ID: <code>{user_id}</code>\n"
            f"• Username: {username}\n\n"
            f"{user_text}"
        ),
        parse_mode="HTML",
        reply_markup=kb
    )

    ticket.chat_id = sent.chat.id
    ticket.message_id = sent.message_id
    ticket.save()

    await message.answer("✅ Ваше обращение передано в техподдержку.")

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
        TicketMessage.create(ticket=ticket, sender="manager", text=message.text.strip())

        # Отправляем пользователю
        try:
            await bot.send_message(
                chat_id=ticket.user_id,
                text=f"📬 Ответ от поддержки:\n\n{message.text}"
            )
            logger.info(f"✅ Ответ отправлен пользователю {ticket.user_id}")
        except Exception as e:
            logger.error(f"❌ Не удалось отправить ответ: {e}")
            await message.answer("❌ Не удалось доставить сообщение пользователю.")

        # Обновляем кнопки (опционально)
        if ticket.chat_id and ticket.message_id:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="📨 Ответить", callback_data=f"reply:{ticket_id}"),
                    InlineKeyboardButton(text="CloseOperation️ Закрыть", callback_data=f"close:{ticket_id}")
                ]
            ])
            try:
                await bot.edit_message_reply_markup(
                    chat_id=ticket.chat_id,
                    message_id=ticket.message_id,
                    reply_markup=kb
                )
            except Exception as e:
                if "message is not modified" not in str(e):
                    logger.warning(f"Не удалось обновить кнопки: {e}")

        await message.answer("✅ Ответ отправлен.")

    except SupportTicket.DoesNotExist:
        await message.answer("❌ Тикет не найден.")
    except Exception as e:
        logger.exception(e)
        await message.answer("❌ Ошибка при отправке ответа.")

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