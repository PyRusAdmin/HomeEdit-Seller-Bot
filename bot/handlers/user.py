from aiogram import F, Router
from aiogram.types import Message

router = Router(name=__name__)


@router.message(F.text == '/start')
async def cmd_start(message: Message):
    await message.answer('Привет! Я бот на aiogram 3!')