from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    language = State()
    fio = State()
    phone = State()
