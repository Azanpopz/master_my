import time
import random
from pyrogram import Client, filters
from Hsbotz import hsbotz

CMD = ["/", "."]

@Client.on_message(filters.command("alive", CMD))
async def check_alive(_, message):
    await message.reply_photo(
        photo="https://graph.org/file/2c30c1452c2c4bccc3046.jpg",
        caption=hsbotz.ALIVE_TXT.format(message.from_user.mention)
    )

@Client.on_message(filters.command("help", CMD))
async def help(_, message):
    await message.reply_photo(
        photo="https://telegra.ph/file/9396a7fe2dd787f9c018b.jpg",
        caption=hsbotz.HELP_TXT.format(message.from_user.mention)
    )

@Client.on_message(filters.command("credits", CMD))
async def credits(_, message):
    await message.reply_photo(
        photo="https://telegra.ph/file/585b5dda92b65b80ee7b9.jpg",
        caption=hsbotz.CREDITS_TXT.format(message.from_user.mention)
    )

@Client.on_message(filters.command("movies", CMD))
async def movie(_, message):
    await message.reply_photo(
        photo="https://telegra.ph/file/1575587a06e961426c74b.jpg",
        caption=hsbotz.MOVIES_TXT.format(message.from_user.mention)
    )

@Client.on_message(filters.command("series", CMD))
async def series(_, message):
    await message.reply_photo(
        photo="https://telegra.ph/file/f89e27fc915fbc38a952c.jpg",
        caption=hsbotz.SERIES_TXT.format(message.from_user.mention)
    )

@Client.on_message(filters.command("download", CMD))
async def tutorial(_, message):
    await message.reply_photo(
        photo="https://telegra.ph/file/8ede8a20e9770299aa7ee.jpg",
        caption=hsbotz.DOWNLOAD_TXT.format(message.from_user.mention)
    )

@Client.on_message(filters.command("ping", CMD))
async def ping(_, message):
    start_t = time.time()
    rm = await message.reply_text("...........")
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await rm.edit(f"😇ᴩɪɴɢ💌!\n\n{time_taken_s:.3f} ms")
