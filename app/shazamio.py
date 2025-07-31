from aiogram import Router, F, types
from shazamio import Shazam
from moviepy.audio.io.AudioFileClip import AudioFileClip


from config import DIR
from app.handlers import user_results_paged, send_music_list
from app.music import search_music
import asyncio
import os

SAVE_DIR = DIR

roots = Router()

@roots.message(F.voice | F.video | F.video_note | F.audio)
async def handle_media(message: types.Message):

    loading_msg = await message.answer("🔍 Qidirilmoqda...")

    file = message.voice or message.video or message.video_note or message.audio

    file_name = f"{message.from_user.id}_{file.file_unique_id}"
    ext = ".ogg" if not file.mime_type == "audio/mpeg" else ".mp3"
    input_path = os.path.join(SAVE_DIR, file_name + ext)

    tg_file = await message.bot.get_file(file.file_id)
    await message.bot.download_file(tg_file.file_path, destination=input_path)


    wav_path = input_path.rsplit('.', 1)[0] + ".wav"
    try:
        clip = AudioFileClip(input_path)
        clip.write_audiofile(wav_path, codec='pcm_s16le')
        clip.close()
    except Exception as e:
        await loading_msg.edit_text("🎵 Konvertatsiya qilishda xatolik bo'ldi.")
        print("FFMPEG xatolik:", e)
        return

    try:
        info = await recognize_music(wav_path)
        print("🎧 Shazam'dan qaytgan natija:", info)

        title = info.get("title")
        subtitle = info.get("subtitle")

        if title and subtitle:
            text = f"🎶 *{title}*\n🎤 _{subtitle}_"
            await message.answer(text, parse_mode="Markdown")


            query = f"{title}"
            result = await search_music(query)
            print(result)
            if result:
                user_results_paged[message.from_user.id] = {
                    "query": query,
                    "offset": 0,
                    "results": result
                }
                await send_music_list(loading_msg, result, offset=0)
            else:
                await loading_msg.edit_text("ℹ️ Bazada bu qo'shiq topilmadi.")
        else:
            await loading_msg.edit_text("❌ Musiqa aniqlanmadi.")
    except Exception as e:
        await loading_msg.edit_text("❌ Tanib olishda xatolik yuz berdi.")
        print("Shazam xatolik:", e)
        return

    for f in (input_path, wav_path):
        try:
            os.remove(f)
        except:
            pass

async def convert_to_mp3(input_path: str, output_path: str):
    cmd = ["ffmpeg", "-y", "-i", input_path, "-vn", "-acodec", "libmp3lame", output_path]
    process = await asyncio.create_subprocess_exec(*cmd)
    await process.communicate()
    return output_path


async def recognize_music(file_path: str):
    shazam = Shazam()
    result = await shazam.recognize(file_path)
    track = result.get("track", {})
    return {
        "title": track.get("title"),
        "subtitle": track.get("subtitle"),
        "url": track.get("url")
    }
