from aiogram.types import  ReplyKeyboardMarkup, KeyboardButton

from config import ID

ADMIN_ID = ID  

def user_buttons(user_id):
    if user_id == ADMIN_ID:
        keyboard = [
            [KeyboardButton(text="🎵 Musiqa qo'shish"), KeyboardButton(text="📊 Statistika")],
            [KeyboardButton(text="🎼 Musiqa soni"), KeyboardButton(text="🎲 Tasodifiy qo'shiqlar")]
        ]
    else:
        keyboard = [
            [KeyboardButton(text="🎲 Tasodifiy qo'shiqlar")]
        ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Musiqa nomini kiriting yoki pastdagi tugmalardan foydalaning"
    )