# Telegram Bot на aiogram 3

## Описание

Этот проект представляет собой шаблон Telegram-бота на aiogram 3 с правильной структурой файлов и папок.

## Установка

1. Клонируйте репозиторий:
    ```bash
    git clone <ссылка_на_репозиторий>
    ```

2. Создайте виртуальное окружение:
    ```bash
    python -m venv venv
    ```

3. Активируйте виртуальное окружение:
    - Windows:
   ```bash
   venv\Scripts\activate
   ```
    - Linux/MacOS:
   ```bash
   source venv/bin/activate
   ```

4. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

5. Создайте файл `.env` в корне проекта и добавьте туда токен бота:
   ```env
   BOT_TOKEN=ваш_токен_бота
   ```

## Запуск

```bash
python main.py
```

## Структура проекта

```
Прием отзывов/
├── .env
├── .gitignore
├── README.md
├── requirements.txt
├── main.py
└── bot/
    ├── __init__.py
    ├── bot.py
    ├── dispatcher.py
    ├── handlers/
    │   ├── __init__.py
    │   └── user.py
    ├── keyboards/
    │   ├── __init__.py
    │   └── reply.py
    ├── middleware/
    │   ├── __init__.py
    │   └── throttling.py
    └── utils/
        ├── __init__.py
        └── database.py
```

## Дополнительно

- Для работы с базой данных раскомментируйте соответствующие зависимости в `requirements.txt`
- Для использования вебхуков раскомментируйте зависимости и настройки в `.env` файле

## Лицензия

Этот проект лицензирован по лицензии MIT.