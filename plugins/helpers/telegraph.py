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
        await update.reply_text("Rᴇᴩʟʏ Tᴏ A Pʜᴏᴛᴏ / Vɪᴅᴇᴏ Uɴᴅᴇʀ 5ᴍʙ")
        return
    file_info = get_file_id(replied)
    if not file_info:
        await update.reply_text("Nᴏᴛ Sᴜᴩᴩᴏʀᴛᴇᴅ Mᴇᴅɪᴀ Tʏᴩᴇ !")
        return
    text = await update.reply_text(text="<code>Dᴏᴡɴʟᴏᴀᴅɪɴɢ Iɴ Mʏ Sᴇʀᴠᴇʀ...</code>", disable_web_page_preview=True)   
    media = await update.reply_to_message.download()   
    await text.edit_text(text="<code>Dᴏᴡɴʟᴏᴀᴅ Tᴏ Mʏ Sᴇʀᴠᴇʀ Is Cᴏᴍᴩʟᴇᴛᴇ. Nᴏᴡ IᴀM Uᴩʟᴏᴀᴅɪɴɢ Tᴏ Tᴇʟᴇɢʀᴀᴩʜ ...</code>", disable_web_page_preview=True)                                            
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
        text=f"<b>Lɪɴᴋ :-</b>\n\n<code>https://graph.org{response[0]}</code>",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup( [[
            InlineKeyboardButton(text="🔗 ᴏᴩᴇɴ ʟɪɴᴋ", url=f"https://graph.org{response[0]}"),
            InlineKeyboardButton(text="🧚 ꜱʜᴀʀᴇ ʟɪɴᴋ", url=f"https://telegram.me/share/url?url=https://graph.org{response[0]}")
            ],[
            InlineKeyboardButton(text="✗ ᴄʟᴏsᴇ ✗", callback_data="close")
            ]])
        )
