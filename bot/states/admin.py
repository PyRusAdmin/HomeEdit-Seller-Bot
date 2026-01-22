# -*- coding: utf-8 -*-
from aiogram.fsm.state import StatesGroup, State


class Admin(StatesGroup):
    id_user = State()  # id пользователя бота
    role = State()
