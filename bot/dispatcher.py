from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

storage = MemoryStorage()
dispatcher = Dispatcher(storage=storage)