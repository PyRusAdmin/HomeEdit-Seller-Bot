# -*- coding: utf-8 -*-
from datetime import datetime

from loguru import logger
from peewee import SqliteDatabase, Model, CharField, IntegerField, DateTimeField, ForeignKeyField, TextField

# Настройка подключения к базе данных SQLite (или другой базы данных)
db = SqliteDatabase(f"data/database.db")


class SupportTicket(Model):
    ticket_id = CharField(unique=True)  # Например, "TICKET_123456"
    user_id = IntegerField()
    status = CharField(default="open")  # open / closed
    created_at = DateTimeField(default=datetime.now)
    closed_at = DateTimeField(null=True)

    # Новые поля:
    chat_id = IntegerField(null=True)      # ID чата, куда отправлен тикет
    message_id = IntegerField(null=True)   # ID сообщения с кнопками

    class Meta:
        database = db
        table_name = "support_tickets"


class TicketMessage(Model):
    ticket = ForeignKeyField(SupportTicket, backref='messages')
    sender = CharField()  # "user" или "manager"
    text = TextField()
    sent_at = DateTimeField(default=datetime.now)

    class Meta:
        database = db
        table_name = "ticket_messages"


class BotUsers(Model):
    """
    Таблица пользователей, которые запускали бота.
    """
    user_id = IntegerField(unique=True)  # ID пользователя
    username = CharField(null=True)  # username
    first_name = CharField(null=True)  # Имя
    last_name = CharField(null=True)  # Фамилия
    chat_type = CharField()  # Тип чата (private, group и т.д.)
    language_code = CharField(null=True)  # Язык Telegram
    date_start = CharField()  # Дата первого запуска
    role = CharField(default="user")  # Роль пользователя

    class Meta:
        database = db
        table_name = "bot_users"


def get_all_bot_users() -> list:
    """
    Возвращает список всех user_id, которые когда-либо запускали бота.
    """
    return [user.user_id for user in BotUsers.select(BotUsers.user_id)]


def get_user_role(user_id: int) -> str:
    """
    Возвращает роль пользователя по его user_id.
    Если пользователь не найден — возвращает 'user' (по умолчанию).
    """
    try:
        user = BotUsers.get(BotUsers.user_id == user_id)
        return user.role
    except BotUsers.DoesNotExist:
        return "user"  # или "guest", если хотите


def update_user_role(user_id: int, role: str):
    """
    Обновляет роль пользователя в базе данных.

    Если пользователь с указанным user_id существует, обновляет его роль.
    Если пользователь не существует, создаёт новую запись с указанной ролью
    и остальными полями по умолчанию.

    Args:
        user_id (int): Уникальный идентификатор пользователя в Telegram.
        role (str): Новая роль пользователя (например, 'user', 'admin').

    Returns:
        bool: Всегда возвращает True после успешного обновления или создания записи.
    """
    user, created = BotUsers.get_or_create(
        user_id=user_id,
        defaults={
            "username": None,
            "first_name": None,
            "last_name": None,
            "chat_type": "private",
            "language_code": None,
            "date_start": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "role": role
        }
    )
    if not created:
        user.role = role
        user.save()
    return True


async def save_bot_user(message):
    """
    Сохраняет или обновляет данные о пользователе, который запустил бота.
    """

    try:

        user_id = message.from_user.id  # Получаем ID пользователя из сообщения
        username = message.from_user.username  # Получаем username пользователя (может быть None)
        first_name = message.from_user.first_name  # Получаем имя пользователя
        last_name = message.from_user.last_name  # Получаем фамилию пользователя (может быть None)
        chat_type = message.chat.type  # Определяем тип чата (личный, группа и т.д.)
        lang = message.from_user.language_code  # Получаем языковой код пользователя
        date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Форматируем текущую дату и время для записи в БД

        user, created = BotUsers.get_or_create(
            user_id=user_id,
            defaults={
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "chat_type": chat_type,
                "language_code": lang,
                "date_start": date_now,
            },
        )

        if not created:
            # обновляем данные, если пользователь уже есть
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.chat_type = chat_type
            user.language_code = lang
            user.save()

        logger.info(f"✅ Пользователь {user_id} сохранён в БД (new={created})")

    except Exception as e:
        logger.exception(e)
