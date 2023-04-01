from __future__ import unicode_literals

import os
import requests
import aiohttp
import yt_dlp
import asyncio
import math
import time

import wget
import aiofiles

from Hsbotz import hsbotz
from pyrogram import filters, Client, enums
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.types import Message
from youtube_search import YoutubeSearch
from youtubesearchpython import SearchVideos
from yt_dlp import YoutubeDL
import youtube_dl
import requests

def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(':'))))


@Client.on_message(filters.command('song'))
def song(client, message):

    user_id = message.from_user.id 
    user_name = message.from_user.first_name 
    rpk = "["+user_name+"](tg://user?id="+str(user_id)+")"

    query = ''
    for i in message.command[1:]:
        query += ' ' + str(i)
    print(query)
    m = message.reply("**𝑺𝒆𝒂𝒓𝒄𝒉𝒊𝒏𝒈 𝒚𝒐𝒖 𝒔𝒐𝒏𝒈 𝄟...!**")
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        #print(results)
        title = results[0]["title"][:40]       
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f'thumb{title}.jpg'
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, 'wb').write(thumb.content)


        performer = f"⚡️ʜꜱ ᠰ ʙᴏᴛꜱ⚡️" 
        duration = results[0]["duration"]
        url_suffix = results[0]["url_suffix"]
        views = results[0]["views"]

    except Exception as e:
        m.edit(
            "**𝑭𝒐𝒖𝒏𝒅 𝑵𝒐𝒕𝒉𝒊𝒏𝒈 𝑷𝒍𝒆𝒂𝒔𝒆 𝑪𝒐𝒓𝒓𝒆𝒄𝒕 𝑻𝒉𝒆 𝑺𝒑𝒆𝒍𝒍𝒊𝒏𝒈 𝑶𝒓 𝑺𝒆𝒂𝒓𝒄𝒉 𝑨𝒏𝒚 𝑶𝒕𝒉𝒆𝒓 𝑺𝒐𝒏𝒈**"
        )
        print(str(e))
        return
    m.edit("**𝒅𝒐𝒘𝒏𝒍𝒐𝒂𝒅𝒊𝒏𝒈 𝒚𝒐𝒖𝒓 𝒔𝒐𝒏𝒈....!**")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)
        rep =hsbotz.SONGOP_TXT.format(message.from_user.mention)
        secmul, dur, dur_arr = 1, 0, duration.split(':')
        for i in range(len(dur_arr)-1, -1, -1):
            dur += (int(dur_arr[i]) * secmul)
            secmul *= 60
        message.reply_audio(audio_file, caption=rep, parse_mode=enums.ParseMode.MARKDOWN,quote=False, title=title, duration=dur, performer=performer, thumb=thumb_name)
        m.delete()
    except Exception as e:
        m.edit("**⚠️ 𝒆𝒓𝒓𝒐𝒓**")
        print(e)

    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as e:
        print(e)

def get_text(message: Message) -> [None,str]:
    text_to_return = message.text
    if message.text is None:
        return None
    if " " not in text_to_return:
        return None
    try:
        return message.text.split(None, 1)[1]
    except IndexError:
        return None


@Client.on_message(filters.command(["video", "mp4"]))
async def vsong(client, message: Message):
    urlissed = get_text(message)

    pablo = await client.send_message(
        message.chat.id, f"**𝑭𝒊𝒏𝒅𝒊𝒏𝒈 𝒚𝒐𝒖𝒓 𝒗𝒊𝒅𝒆𝒐... 🗯️** `{urlissed}`"
    )
    if not urlissed:
        await pablo.edit("𝑰𝒏𝒗𝒂𝒍𝒊𝒅 𝑪𝒐𝒎𝒎𝒂𝒏𝒅 𝑺𝒚𝒏𝒕𝒂𝒙 𝑷𝒍𝒆𝒂𝒔𝒆 𝑪𝒉𝒆𝒄𝒌 𝒉𝒆𝒍𝒑 𝑴𝒆𝒏𝒖 𝑻𝒐 𝑲𝒏𝒐𝒘 𝑴𝒐𝒓𝒆!")
        return

    search = SearchVideos(f"{urlissed}", offset=1, mode="dict", max_results=1)
    mi = search.result()
    mio = mi["search_result"]
    mo = mio[0]["link"]
    thum = mio[0]["title"]
    fridayz = mio[0]["id"]
    mio[0]["channel"]
    kekme = f"https://img.youtube.com/vi/{fridayz}/hqdefault.jpg"
    await asyncio.sleep(0.6)
    url = mo
    sedlyf = wget.download(kekme)
    opts = {
        "format": "best",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
        "outtmpl": "%(id)s.mp4",
        "logtostderr": False,
        "quiet": True,
    }
    try:
        with YoutubeDL(opts) as ytdl:
            ytdl_data = ytdl.extract_info(url, download=True)
    except Exception as e:
        await event.edit(event, f"**𝒅𝒐𝒘𝒏𝒍𝒐𝒂𝒅 𝒇𝒂𝒊𝒍𝒆𝒅 𝒑𝒍𝒆𝒂𝒔𝒆 𝒕𝒓𝒚 𝒂𝒈𝒂𝒊𝒏...🫰** \n**⚠️ 𝒆𝒓𝒓𝒐𝒓 :** `{str(e)}`")
        return
    c_time = time.time()
    file_stark = f"{ytdl_data['id']}.mp4"
    capy = f"""
**ᴛɪᴛʟᴇ :** [{thum}]({mo})

**ʀᴇ𝚀ᴜᴇꜱᴛᴇᴅ ʙʏ:** {message.from_user.mention}

**ʜꜱ ᠰ ʙᴏᴛꜱ😇**
"""
    await client.send_video(
        message.chat.id,
        video=open(file_stark, "rb"),
        duration=int(ytdl_data["duration"]),
        file_name=str(ytdl_data["title"]),
        thumb=sedlyf,
        caption=capy,
        supports_streaming=True,        
        reply_to_message_id=message.id 
    )
    await pablo.delete()
    for files in (sedlyf, file_stark):
        if files and os.path.exists(files):
            os.remove(files)
