from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from random import sample

from app.music import search_music, check_music, check_music_add, random_music
from app.kb import user_buttons
from app.states import AddMusic
from config import TOKEN, ID, DIR

import sqlite3
import os
import json

API_TOKEN = TOKEN
ADMIN_ID = ID  
SAVE_DIR = DIR

STAT_FILE = "stats.json"
user_results_paged = {}
user_results = {}
os.makedirs(SAVE_DIR, exist_ok=True)

if os.path.exists(STAT_FILE):
    with open(STAT_FILE, "r") as f:
        stats = json.load(f)
else:
    stats = {
        "total_sent": 0,
        "total_searches": 0
    }

def save_stats():
    with open(STAT_FILE, "w") as f:
        json.dump(stats, f)

def increment_sent():
    stats["total_sent"] += 1
    save_stats()

def increment_searches():
    stats["total_searches"] += 1
    save_stats()

def get_stats():
    return stats

root = Router()

@root.message(CommandStart())
async def start(message: types.Message):
    kb = user_buttons(message.from_user.id)
    await message.answer(
    "🎵 *Assalomu alaykum!*\n\n"
    "Bot quyidagilarni amalga oshiradi:\n"
    "• Musiqa nomi bo‘yicha qidiradi;\n"
    "• Yuborilgan *audio*, *video* yoki *video note* orqali musiqa nomini aniqlaydi.\n\n"
    "Qidirishni boshlash uchun musiqa nomini kiriting yoki fayl yuboring.",
    reply_markup=kb,
    parse_mode="Markdown"
)


@root.message(F.text == "🎲 Tasodifiy qo'shiqlar")
async def start_random_music(message: types.Message):
    loading_msg = await message.answer("🔍 Qidirilmoqda...")
    
    all_tracks = random_music()

    if not all_tracks:
        await loading_msg.edit_text("❌ Hozircha bazada musiqa yo'q.", parse_mode="Markdown")
        return

    selected = sample(all_tracks, min(10, len(all_tracks))) 

    user_results_paged[message.from_user.id] = {
        "query": "random",  
        "offset": 0,
        "results": [(None, name, doc_id) for name, doc_id in selected]  
    }

    await send_music_list(loading_msg, user_results_paged[message.from_user.id]["results"], offset=0)


@root.message(F.text == "🎵 Musiqa qo'shish")
async def start_add_music(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Ruxsat yo'q!", show_alert=True)
        return
    await message.answer("Musiqa nomini yuboring:", parse_mode = "Markdown")
    await state.set_state(AddMusic.waiting_for_name)


@root.message(F.text == "📊 Statistika")
async def start_add_music(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Ruxsat yo'q!", show_alert=True, parse_mode = "Markdown")
        return
    stats = get_stats()
    await message.answer(f"📊 Statistika:\n🔍 Qidiruvlar soni: {stats['total_searches']}\n📤 Yuborilgan qo'shiqlar: {stats['total_sent']}", parse_mode = "Markdown")


@root.message(F.text == "🎼 Musiqa soni")
async def start_add_music(message: types.Message):
    total = await check_music()
    admin = await check_music_add()

    await message.answer(f"🎼 Umumiy: {total + admin} ta musiqa\n👤 Admin qo'shgan: {admin} ta", parse_mode = "Markdown")

@root.message(AddMusic.waiting_for_name)
async def music_name_handler(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("Endi Telegram linkni yuboring (https://t.me/...)", parse_mode = "Markdown")
    await state.set_state(AddMusic.waiting_for_link)

@root.message(AddMusic.waiting_for_link)
async def music_link_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data["name"]
    link = message.text.strip()

    if not link.startswith("https://t.me/"):
        await message.answer("Noto'g'ri link. Qaytadan urinib ko'ring.", parse_mode = "Markdown")
        return

    conn = sqlite3.connect("admin_added.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO data (name, doc_id) VALUES (?, ?)", (name, link))
    conn.commit()
    conn.close()

    await message.answer("✅ Musiqa saqlandi!\n" + name, parse_mode = "Markdown")
    await state.clear()


@root.message(F.text & ~F.text.startswith("/"))
async def search_music_handler(message: types.Message):
    query = message.text.strip()
    offset = 0

    loading_msg = await message.answer("🔍 Qidirilmoqda...")

    result = await search_music(query, offset=offset)

    if not result:
        await loading_msg.edit_text("❌ Hech narsa topilmadi.")
        return

    user_results_paged[message.from_user.id] = {
        "query": query,
        "offset": offset,
        "results": result
    }

    await send_music_list(loading_msg, result, offset)
    increment_searches()


async def send_music_list(message_or_cb, result, offset):
    text = "🎶 *Topilgan qo'shiqlar:*\n\n"
    for idx, (_, name, _) in enumerate(result, start=1):
        text += f"{idx}. {name}\n"

    buttons = [
        InlineKeyboardButton(text=str(i + 1), callback_data=f"music_{i}")
        for i in range(len(result))
    ]
    button_rows = [buttons[i:i + 5] for i in range(0, len(buttons), 5)]

    nav_buttons = [
        InlineKeyboardButton(text="⬅️", callback_data="music_page_prev"),
        InlineKeyboardButton(text="❌", callback_data="music_cancel"),
        InlineKeyboardButton(text="➡️", callback_data="music_page_next")
    ]
    button_rows.append(nav_buttons)

    keyboard = InlineKeyboardMarkup(inline_keyboard=button_rows)


    if isinstance(message_or_cb, types.Message):
        await message_or_cb.delete()
        await message_or_cb.answer(text, reply_markup=keyboard, parse_mode="Markdown")
    else:
        await message_or_cb.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")


@root.callback_query(F.data == "music_cancel")
async def cancel_music_list(callback: types.CallbackQuery):
    try:
        await callback.message.delete()  
        await callback.answer("✅ Bekor qilindi.")
    except TelegramBadRequest as e:
        if "message to delete not found" in str(e):
            await callback.answer("❌ Xabar allaqachon o'chirilgan.", show_alert=True)
        else:
            print("TelegramBadRequest:", e)
            await callback.answer("⚠️ Xatolik yuz berdi.", show_alert=True)
    except Exception as e:
        print("O'chirishda umumiy xatolik:", e)
        await callback.answer("⚠️ O'chirishda xatolik.", show_alert=True)


@root.callback_query(F.data.in_({"music_page_prev", "music_page_next"}))
async def paginate_music(callback: types.CallbackQuery):
    user_id = callback.from_user.id 
    data = user_results_paged.get(user_id)
    if not data:
        await callback.message.answer("❌ Avval izlashni boshlang.")
        return

    offset = data["offset"]
    query = data["query"]

    if callback.data == "music_page_prev":
        if offset == 0:
            await callback.answer("❗️Siz birinchi sahifadasiz.", show_alert=True)
            return
        offset -= 10
    elif callback.data == "music_page_next":
        new_result = await search_music(query, offset + 10) 
        if not new_result:
            await callback.answer("❗️Boshqa natijalar yo'q.", show_alert=True)
            return
        offset += 10

    result = await search_music(query, offset) 
    user_results_paged[user_id]["offset"] = offset
    user_results_paged[user_id]["results"] = result

    await send_music_list(callback, result, offset)
    await callback.answer()


@root.callback_query(F.data.startswith("music_"))
async def music_send_callback(callback: types.CallbackQuery):
    try:
        index = int(callback.data.split("_")[1])
        user_id = callback.from_user.id
        data = user_results_paged.get(user_id)
        if not data or index >= len(data["results"]):
            await callback.message.answer("⚠️ Xatolik yuz berdi.")
            return

        doc_id = data["results"][index][2]
        if doc_id.startswith("https://t.me/"):
            await callback.message.bot.send_chat_action(callback.message.chat.id, "upload_audio")


            await callback.message.answer_audio(audio=doc_id)
            increment_sent()
            await callback.answer()
        else:
            await callback.message.answer("❌ Noto'g'ri havola.")
    except Exception as e:
        print("Xatolik", e)
        await callback.message.answer("Hatolik chiqdi!")

