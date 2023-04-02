import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from telegraph import upload_file
#from info import TMP_DOWNLOAD_DIRECTORY
#from plugins.helper_functions.cust_p_filters import f_onw_fliter
from plugins.helper_functions.get_file_id import get_file_id


@Client.on_message(filters.command("telegraph") & filters.private)
async def telegraph_upload(bot, update):
    replied = update.reply_to_message
    if not replied:
        await update.reply_text("𝑹𝒆𝒑𝒍𝒚 𝒕𝒐 𝒂 𝒑𝒉𝒐𝒕𝒐 𝒐𝒓 𝒗𝒊𝒅𝒆𝒐 𝒖𝒏𝒅𝒆𝒓 5𝒎𝒃...😊")
        return
    file_info = get_file_id(replied)
    if not file_info:
        await update.reply_text("𝑵𝒐𝒕 𝒔𝒖𝒑𝒑𝒐𝒓𝒕𝒆𝒅 𝒎𝒆𝒅𝒊𝒂 𝒕𝒚𝒑𝒆 !")
        return
    text = await update.reply_text(text="<code>𝒅𝒐𝒘𝒏𝒍𝒐𝒂𝒅𝒊𝒏𝒈 𝒊𝒏 𝒎𝒚 𝒔𝒆𝒓𝒗𝒆𝒓...🦋</code>", disable_web_page_preview=True)   
    media = await update.reply_to_message.download()   
    await text.edit_text(text="<code>𝒅𝒐𝒘𝒏𝒍𝒐𝒂𝒅 𝒕𝒐 𝒎𝒚 𝒔𝒆𝒓𝒗𝒆𝒓 𝒊𝒔 𝒄𝒐𝒎𝒑𝒍𝒆𝒕𝒆. 𝒏𝒐𝒘 𝒊 𝒂𝒎 𝒖𝒑𝒅𝒂𝒕𝒊𝒏𝒈 𝒕𝒐 𝒕𝒆𝒍𝒆𝒈𝒓𝒂𝒑𝒉...🪄</code>", disable_web_page_preview=True)                                            
    try:
        response = upload_file(media)
    except Exception as error:
        print(error)
        await text.edit_text(text=f"Eʀʀᴏʀ :- {error}", disable_web_page_preview=True)       
        return    
    try:
        os.remove(media)
    except Exception as error:
        print(error)
        return    
    await text.edit_text(
        text=f"<b>𝒍𝒊𝒏𝒌 :-</b>\n\n<code>https://graph.org{response[0]}</code>\n",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup( [[
            InlineKeyboardButton(text="ᴏᴩᴇɴ ʟɪɴᴋ", url=f"https://graph.org{response[0]}"),
            InlineKeyboardButton(text="ꜱʜᴀʀᴇ ʟɪɴᴋ", url=f"https://telegram.me/share/url?url=https://graph.org{response[0]}")
            ],[
            InlineKeyboardButton(text="✗ ᴄʟᴏsᴇ ✗", callback_data="close")
            ]])
        )
