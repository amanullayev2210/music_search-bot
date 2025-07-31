# 🎵 Music Finder Bot

Telegram uchun sun’iy intellekt asosidagi bot — foydalanuvchi yuborgan **voice**, **video**, yoki **video note** orqali musiqa nomini aniqlaydi.

## ⚙️ Xususiyatlar

- 🎤 **Shazam** integratsiyasi — audio orqali musiqa topish
- 🎞️ **FFmpeg** yordamida video/audio konvertatsiya
- 📎 Inline tugmalar orqali natijani tanlash
- 🔎 Qidiruv tarixini saqlash (agar mavjud bo‘lsa)

## 🚀 Boshlash

1. Ushbu repozitoriyani klon qiling:
   ```bash
   git clone https://github.com/amanullayev2210/music-finder-bot.git
   cd music-search-bot
   ```

2. Zarur kutubxonalarni o‘rnating:
   ```bash
   pip install -r requirements.txt
   ```

3. `config.py` fayl yarating va quyidagilarni qo‘shing:
   ```config
   TOKEN = "BOT_TOKEN"
   ID = profil id 
   DIR = "downloads"
   ```

4. Botni ishga tushiring:
   ```bash
   python main.py
   ```

## 🗂 Texnologiyalar

- Python 3.10+
- [Aiogram 3.x](https://docs.aiogram.dev/)
- FFmpeg
- Shazam API yoki xizmat

## 📦 Versiyalar

- `v1.0` – Boshlang‘ich versiya
- `v1.1` – Inline natijalar qo‘shildi
- `v1.2` – Shazam + FFmpeg qo‘shildi (yangi)

## 🤝 Hissa qo‘shish

Pull request’lar ochiq. Takliflar va muammolar uchun `Issues` bo‘limiga yozing.

## 📜 Litsenziya

MIT License — bemalol foydalaning.
