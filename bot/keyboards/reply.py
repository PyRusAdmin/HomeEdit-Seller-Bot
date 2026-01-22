from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Пример обычной клавиатуры
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="/start")
        ]
    ],
    resize_keyboard=True
)
