from aiogram import Bot, Dispatcher


from config import TOKEN
from app.handlers import root
from app.shazamio import roots

import asyncio
import logging
import sys


bot = Bot(token=TOKEN)
dp = Dispatcher()

dp.include_routers(root, roots)


async def main():
    logging.basicConfig(level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers = [
            logging.FileHandler("bot.log"),
            logging.StreamHandler(sys.stdout)
])
    await dp.start_polling(bot)

asyncio.run(main()) 