from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State


class AddMusic(StatesGroup):
    waiting_for_name = State()
    waiting_for_link = State()