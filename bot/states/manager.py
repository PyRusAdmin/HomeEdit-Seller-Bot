# -*- coding: utf-8 -*-
from aiogram.fsm.state import StatesGroup, State


class ManagerStates(StatesGroup):
    reply_message = State()
