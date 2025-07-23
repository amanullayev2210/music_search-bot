from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from random import sample

from config import TOKEN, ID

import asyncio
import logging
import sqlite3
import sys
import os
import json

 
API_TOKEN = TOKEN
ADMIN_ID = ID  

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

STAT_FILE = "stats.json"
# total_sent = 0
# total_searches = 0

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


class AddMusic(StatesGroup):
    waiting_for_name = State()
    waiting_for_link = State()


def init_admin_db():
    conn = sqlite3.connect("admin_added.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        doc_id TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

init_admin_db()


def search_music(query: str):
    result = []
    for db in ("admin_added.db", "music.db"):
        try:
            conn = sqlite3.connect(db)
            conn.create_function("LOWER", 1, str.lower)
            cur = conn.cursor()
            cur.execute("""
                SELECT id, name, doc_id FROM data
                WHERE LOWER(name) LIKE LOWER(?)
                LIMIT 12
            """, (f"%{query}%",))
            result += cur.fetchall()
            conn.close()
        except Exception:
            pass
    return result


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


@dp.message(CommandStart())
async def start(message: types.Message):
    kb = user_buttons(message.from_user.id)
    await message.answer("Salom!\nQaysi musiqani qidiryapsiz?\nShunchaki nomini yozing:", reply_markup=kb, parse_mode = "Markdown")

@dp.message(F.text == "🎲 Tasodifiy qo'shiqlar")
async def start_random_music(message: types.Message):
    all_tracks = []

    conn1 = sqlite3.connect("music.db")
    cur1 = conn1.cursor()
    cur1.execute("SELECT name, doc_id FROM data")
    all_tracks.extend(cur1.fetchall())
    conn1.close()

    # try:
    #     conn2 = sqlite3.connect("admin_added.db")
    #     cur2 = conn2.cursor()
    #     cur2.execute("SELECT name, doc_id FROM data")
    #     all_tracks.extend(cur2.fetchall())
    #     conn2.close()
    # except sqlite3.OperationalError:
    #     pass  # agar jadval mavjud bo'lmasa jim o'tadi

    if not all_tracks:
        await message.answer("❌ Hozircha bazada musiqa yo'q.", parse_mode = "Markdown")
        return


    selected = sample(all_tracks, min(10, len(all_tracks)))

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=name, callback_data=doc_id)]
        for name, doc_id in selected
    ],
        resize_keyboard=True)
    await message.answer("🎲 Tasodifiy tanlangan qo'shiqlar:", reply_markup=kb, parse_mode = "Markdown")

@dp.message(F.text == "🎵 Musiqa qo'shish")
async def start_add_music(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Ruxsat yo'q!", show_alert=True)
        return
    await message.answer("Musiqa nomini yuboring:", parse_mode = "Markdown")
    await state.set_state(AddMusic.waiting_for_name)


@dp.message(F.text == "📊 Statistika")
async def start_add_music(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Ruxsat yo'q!", show_alert=True, parse_mode = "Markdown")
        return
    stats = get_stats()
    await message.answer(f"📊 Statistika:\n🔍 Qidiruvlar soni: {stats['total_searches']}\n📤 Yuborilgan qo'shiqlar: {stats['total_sent']}", parse_mode = "Markdown")


@dp.message(F.text == "🎼 Musiqa soni")
async def start_add_music(message: types.Message):
    total = 0
    admin = 0

    try:
        conn1 = sqlite3.connect("music.db")
        cur1 = conn1.cursor()
        cur1.execute("SELECT COUNT(*) FROM data")
        total = cur1.fetchone()[0]
        conn1.close()
    except Exception:
            pass

    try:
        conn2 = sqlite3.connect("admin_added.db")
        cur2 = conn2.cursor()
        cur2.execute("SELECT COUNT(*) FROM data")
        admin = cur2.fetchone()[0]
        conn2.close()
    except Exception:
        pass

    await message.answer(f"🎼 Umumiy: {total + admin} ta musiqa\n👤 Admin qo'shgan: {admin} ta", parse_mode = "Markdown")


@dp.message(AddMusic.waiting_for_name)
async def music_name_handler(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("Endi Telegram linkni yuboring (https://t.me/...)", parse_mode = "Markdown")
    await state.set_state(AddMusic.waiting_for_link)

@dp.message(AddMusic.waiting_for_link)
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


@dp.message(F.text & ~F.text.startswith("/"))
async def search_music_handler(message: types.Message):
    query = message.text.strip()
    result = search_music(query)
    # global total_searches

    if not result:
        await message.answer("❌ Hech narsa topilmadi.", parse_mode = "Markdown")
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=name, callback_data=doc_id)]
        for _, name, doc_id in result
    ],
        resize_keyboard=True
    )
    await message.answer("Topilgan qo'shiqlar:", reply_markup=kb, parse_mode = "Markdown")
    increment_searches()


@dp.callback_query()
async def music_send_callback(callback: types.CallbackQuery):
    # global total_sent
    try:
        doc_id = callback.data
        if doc_id.startswith("https://t.me/"):
            await bot.send_chat_action(callback.message.chat.id, "upload_audio")
            await callback.message.answer_audio(audio=doc_id)
            # total_sent += 1
            increment_sent()
            await callback.answer()
    except:
        await callback.message.answer("Hatolik chiqdi!")


# async def prank_spam():
#     for i in range(10000000):
#         try:
#             await bot.send_message(5144030413, f"🤖 Bot ishlamoqda... ")
#             await asyncio.sleep(0.3)  # Har xabar orasida kutish
#         except Exception as e:
#             print(f"Xato yuz berdi: {e}")
#             break

async def main():
    logging.basicConfig(level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers = [
            logging.FileHandler("bot.log"),
            logging.StreamHandler(sys.stdout)
])
    # asyncio.create_task(prank_spam())
    await dp.start_polling(bot)

asyncio.run(main()) 