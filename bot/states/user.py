# -*- coding: utf-8 -*-
from aiogram.fsm.state import StatesGroup, State


class UserStates(StatesGroup):
    user_question = State()  # Вопрос пользователя
