from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from .handlers.user import router as user_router

storage = MemoryStorage()
dispatcher = Dispatcher(storage=storage)

dispatcher.include_router(user_router)