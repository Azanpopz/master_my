#Made
#by
#Don_Sflix

from pyrogram import Client, filters

@Client.on_message(filters.command(["stickerid"]))
async def stickerid(bot, message):   
    if message.reply_to_message.sticker:
       await message.reply(f"** 😇 ꜱᴛɪᴄᴋᴇʀ ɪᴅ ɪꜱ :**  \n\n `{message.reply_to_message.sticker.file_id}` \n \n ** ᴜɴɪ𝚀ᴜᴇ ɪᴅ ɪꜱ ** \n\n`{message.reply_to_message.sticker.file_unique_id}`", quote=True)
    else: 
       await message.reply("<b>𝑶𝒐𝒑𝒔 !! 𝑵𝒐𝒕 𝒂 𝒔𝒕𝒊𝒄𝒌𝒆𝒓 𝒇𝒊𝒍𝒆</b>")
