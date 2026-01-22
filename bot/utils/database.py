# -*- coding: utf-8 -*-
from peewee import SqliteDatabase, Model, CharField, IntegerField
from loguru import logger

# Настройка подключения к базе данных SQLite (или другой базы данных)
db = SqliteDatabase(f"data/database.db")


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


async def save_bot_user(message):
    """
    Сохраняет или обновляет данные о пользователе, который запустил бота.
    """
    from datetime import datetime

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
