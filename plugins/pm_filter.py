# Kanged From @TroJanZheX
import asyncio
import re
import ast
import math
import random

from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
import pyrogram
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, \
    make_inactive
from info import LANGUAGES, MAX_BTN, ADMINS, AUTH_CHANNEL, AUTH_USERS, SUPPORT_CHAT_ID, CUSTOM_FILE_CAPTION, MSG_ALRT, PICS, AUTH_GROUPS, P_TTI_SHOW_OFF, GRP_LNK, CHNL_LNK, NOR_IMG, LOG_CHANNEL, SPELL_IMG, MAX_B_TN, IMDB, \
    SINGLE_BUTTON, SPELL_CHECK_REPLY, IMDB_TEMPLATE, NO_RESULTS_MSG, REQ_CHANNEL, MVG_LNK, OWN_LNK, HOW_TO_DOWNLOAD, SELF_DELETE, SELF_DELETE_SECONDS
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import get_size, is_subscribed, get_poster, search_gagala, temp, get_settings, save_group_settings, get_shortlink
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results, get_bad_files
from database.filters_mdb import (
    del_all,
    find_filter,
    get_filters,
)
from database.gfilters_mdb import (
    find_gfilter,
    get_gfilters,
    del_allg
)
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
SPELL_CHECK = {}

@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    k = await manual_filters(client, message)
    if k == False:
        await global_filter(client, message)

@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    content = message.text
    settings = await get_settings(message.chat.id)        
    if settings["auto_ffilter"]:
        userid = message.from_user.id if message.from_user else None
        if not userid:
            search = message.text
            k = await message.reply(f"You'r anonymous admin! Sorry you can't get '{search}' from here.\nYou can get '{search}' from bot inline search.")
            await asyncio.sleep(30)
            await k.delete()
            try:
                await message.delete()
            except:
                pass
            return

        if AUTH_CHANNEL and not await is_subscribed(client, message):
            try:
                invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL))
            except ChatAdminRequired:
                logger.error("Make sure Bot is admin in Forcesub channel")
                return
            buttons = [[
                InlineKeyboardButton("📢 𝐉𝐨𝐢𝐧 𝐂𝐡𝐚𝐧𝐧𝐞𝐥 📢", url=invite_link.invite_link)
            ],[
                InlineKeyboardButton("🔁 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐀𝐠𝐚𝐢𝐧 🔁", callback_data="grp_checksub")
            ]]
            reply_markup = InlineKeyboardMarkup(buttons)
#            try:
#                await client.restrict_chat_member(message.chat.id, message.from_user.id, ChatPermissions(), datetime.now() + timedelta(minutes=1))
#            except:
#                pass
            k = await message.reply_photo(
                photo=random.choice(SP),
                caption=f"👋 𝐇𝐞𝐥𝐥𝐨 {message.from_user.mention},\n\n{content} 𝐀𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞..!!\n\n𝐏𝐥𝐞𝐚𝐬𝐞 𝐉𝐨𝐢𝐧 𝐌𝐲 '𝐔𝐩𝐝𝐚𝐭𝐞𝐬 𝐂𝐡𝐚𝐧𝐧𝐞𝐥' 𝐀𝐧𝐝 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐀𝐠𝐚𝐢𝐧. 😇",
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
            await asyncio.sleep(300)
            await k.delete()
            try:
                await message.delete()
            except:
                pass
        else:
            await auto_filter(client, message)
    else:
        k = await message.reply_text(f"𝐇𝐞𝐥𝐥𝐨 {message.from_user.mention},\n\n{content} 𝐀𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞..!! \n\n❌️𝐀𝐮𝐭𝐨 𝐅𝐢𝐥𝐭𝐞𝐫 𝐎𝐟𝐟..!!!❌️ \n𝐏𝐥𝐞𝐚𝐬𝐞 𝐖𝐚𝐢𝐭..")
        await asyncio.sleep(5)
        await k.delete()
        try:
            await message.delete()
        except:
            pass
            return
        if message.chat.id != SUPPORT_CHAT_ID:
            await global_filters(client, message)          
        manual = await manual_filters(client, message)
        if manual == False:
            settings = await get_settings(message.chat.id)
            try:
                if settings['auto_ffilter']:
                    await auto_filter(client, message)
            except KeyError:
                grpid = await active_connection(str(message.from_user.id))
                await save_group_settings(grpid, 'auto_ffilter', False)
                settings = await get_settings(message.chat.id)
                if settings['auto_ffilter']:
                    await auto_filter(client, message) 
                    try:
                        await message.delete()
                    except:
                        pass 

@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_text(bot, message):
    content = message.text
    user = message.from_user.first_name
    user_id = message.from_user.id
    if content.startswith("/") or content.startswith("#"): return  # ignore commands and hashtags
    await message.reply_text("<b>Hᴇʏ Dᴜᴅᴇ🥰,\n\nYᴏᴜ ᴄᴀɴ'ᴛ Gᴇᴛ ᴍᴏᴠɪᴇ ʜᴇʀᴇ........\nAꜱᴋ ᴍᴏᴠɪᴇ ᴏɴ ᴏᴜʀ ɢʀᴏᴜᴘ\nCʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴛᴏ 𝚓ᴏɪɴ👇</b>",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📝 ʀᴇǫᴜᴇsᴛ ʜᴇʀᴇ ", url=f"https://t.me/TAMIL_FLIMS_HD/467")]]))
    await bot.send_message(
        chat_id=LOG_CHANNEL,
        text=f"<b>#ᴍʙ_ᴍᴇɢ\n\nɴᴀᴍᴇ : {user}\n\nɪᴅ : {user_id}\n\nᴍᴇꜱꜱᴀɢᴇ : {content}</b>"
    )

@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name),show_alert=True)
        return

    files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    settings = await get_settings(query.message.chat.id)
    if 'is_shortlink' in settings.keys():
        ENABLE_SHORTLINK = settings['is_shortlink']
    else:
        await save_group_settings(query.message.chat.id, 'is_shortlink', False)
        ENABLE_SHORTLINK = False
    if ENABLE_SHORTLINK == True:
        if settings['button']:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)} {file.file_name}", url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                ]
                for file in files
            ]
        else:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{file.file_name}", url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)}",
                        url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                ]
                for file in files
            ]
    else:
        if settings['button']:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)} {file.file_name}", callback_data=f'files#{file.file_id}'
                    ),
                ]
                for file in files
            ]
        else:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{file.file_name}", callback_data=f'files#{file.file_id}'
                    ),
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)}",
                        callback_data=f'files_#{file.file_id}',
                    ),
                ]
                for file in files
            ]
    try:
        if settings['auto_delete']:
            btn.insert(0, 
                [
                    InlineKeyboardButton(f'ɪɴꜰᴏ', 'info'),
                    InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇꜱ", callback_data=f"languages#{search.replace(' ', '_')}#{key}"),
                    InlineKeyboardButton(f'ᴛɪᴘs​', 'tips')
                ]
            )

        else:
            btn.insert(0, 
                [
                    InlineKeyboardButton(f'ɪɴꜰᴏ', 'info'),
                    InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇꜱ", callback_data=f"languages#{search.replace(' ', '_')}#{key}"),
                    InlineKeyboardButton(f'ᴛɪᴘs​', 'tips')
                ]
            )
                
    except KeyError:
        grpid = await active_connection(str(query.message.from_user.id))
        await save_group_settings(grpid, 'auto_delete', True)
        settings = await get_settings(query.message.chat.id)
        if settings['auto_delete']:
            btn.insert(0, 
                [
                    InlineKeyboardButton(f'ɪɴꜰᴏ', 'info'),
                    InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇꜱ", callback_data=f"languages#{search.replace(' ', '_')}#{key}"),
                    InlineKeyboardButton(f'ᴛɪᴘs​', 'tips')
                ]
            )

        else:
            btn.insert(0, 
                [
                    InlineKeyboardButton(f'ɪɴꜰᴏ', 'info'),
                    InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇꜱ", callback_data=f"languages#{search.replace(' ', '_')}#{key}"),
                    InlineKeyboardButton(f'ᴛɪᴘs​', 'tips')
                ]
            )
    try:
        settings = await get_settings(query.message.chat.id)
        if settings['max_btn']:
            if 0 < offset <= MAX_BTN:
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - 10
            if n_offset == 0:
                btn.append(
                    [InlineKeyboardButton("☜ ʙᴀᴄᴋ​", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset) / MAX_BTN)+1} / {math.ceil(total / MAX_BTN)}", callback_data="pages")]
                )
            elif off_set is None:
                btn.append([InlineKeyboardButton("ᴘᴀɢᴇ​", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset) / MAX_BTN)+1} / {math.ceil(total / MAX_BTN)}", callback_data="pages"), InlineKeyboardButton("ɴᴇxᴛ​ ≫", callback_data=f"next_{req}_{key}_{n_offset}")])
            else:
                btn.append(
                    [
                        InlineKeyboardButton("☜ ʙᴀᴄᴋ​", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(f"{math.ceil(int(offset) / MAX_BTN)+1} / {math.ceil(total / MAX_BTN)}", callback_data="pages"),
                        InlineKeyboardButton("ɴᴇxᴛ​ ☞", callback_data=f"next_{req}_{key}_{n_offset}")
                    ],
                )
        else:
            if 0 < offset <= int(MAX_B_TN):
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - int(MAX_B_TN)
            if n_offset == 0:
                btn.append(
                    [InlineKeyboardButton("☜ ʙᴀᴄᴋ​", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages")]
                )
            elif off_set is None:
                btn.append([InlineKeyboardButton("ᴘᴀɢᴇ​", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"), InlineKeyboardButton("ɴᴇxᴛ​ ≫", callback_data=f"next_{req}_{key}_{n_offset}")])
            else:
                btn.append(
                    [
                        InlineKeyboardButton("☜ ʙᴀᴄᴋ​", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"),
                        InlineKeyboardButton("ɴᴇxᴛ​ ☞", callback_data=f"next_{req}_{key}_{n_offset}")
                    ],
                )
    except KeyError:
        await save_group_settings(query.message.chat.id, 'max_btn', False)
        settings = await get_settings(query.message.chat.id)
        if settings['max_btn']:
            if 0 < offset <= 10:
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - 10
            if n_offset == 0:
                btn.append(
                    [InlineKeyboardButton("ɴᴇxᴛ​ ☞", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages")]
                )
            elif off_set is None:
                btn.append([InlineKeyboardButton("ᴘᴀɢᴇ​", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"), InlineKeyboardButton("ɴᴇxᴛ​ ≫", callback_data=f"next_{req}_{key}_{n_offset}")])
            else:
                btn.append(
                    [
                        InlineKeyboardButton("☜ ʙᴀᴄᴋ​", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
                        InlineKeyboardButton("ɴᴇxᴛ​ ☞", callback_data=f"next_{req}_{key}_{n_offset}")
                    ],
                )
        else:
            if 0 < offset <= int(MAX_B_TN):
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - int(MAX_B_TN)
            if n_offset == 0:
                btn.append(
                    [InlineKeyboardButton("☜ ʙᴀᴄᴋ​", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages")]
                )
            elif off_set is None:
                btn.append([InlineKeyboardButton("ᴘᴀɢᴇ​", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"), InlineKeyboardButton("ɴᴇxᴛ​ ≫", callback_data=f"next_{req}_{key}_{n_offset}")])
            else:
                btn.append(
                    [
                        InlineKeyboardButton("☜ ʙᴀᴄᴋ​", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"),
                        InlineKeyboardButton("ɴᴇxᴛ​ ☞", callback_data=f"next_{req}_{key}_{n_offset}")
                    ],
                )
    btn.insert(0, [
        InlineKeyboardButton("⚡ ʜᴏᴡ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ⚡", url=f"{HOW_TO_DOWNLOAD}")
    ])
    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()


@Client.on_callback_query(filters.regex(r"^spol"))
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    movies = SPELL_CHECK.get(query.message.reply_to_message.id)
    if not movies:
        return await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movie = movies[(int(movie_))]
    await query.answer(script.TOP_ALRT_MSG)
    k = await manual_filters(bot, query.message, text=movie)
    if k == False:
        files, offset, total_results = await get_search_results(query.message.chat.id, movie, offset=0, filter=True)
        if files:
            k = (movie, files, offset, total_results)
            await auto_filter(bot, query, k)
        else:
            reqstr1 = query.from_user.id if query.from_user else 0
            reqstr = await bot.get_users(reqstr1)
            if NO_RESULTS_MSG:
                await bot.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, movie)))
            k = await query.message.edit(script.MVE_NT_FND)
            await asyncio.sleep(10)
            await k.delete()

#languages

@Client.on_callback_query(filters.regex(r"^languages#"))
async def languages_cb_handler(client: Client, query: CallbackQuery):

    if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
        return await query.answer(
            f"⚠️ ʜᴇʟʟᴏ{query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇQᴜᴇꜱᴛ,\nʀᴇ𝚀ᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
            show_alert=True,
        )
    
    _, search, key = query.data.split("#")

    btn = [
        [
            InlineKeyboardButton(
                text=lang.title(),
                callback_data=f"fl#{lang.lower()}#{search}#{key}"
                ),
        ]
        for lang in LANGUAGES
    ]

    btn.insert(
        0,
        [
            InlineKeyboardButton(
                text="☟ 𝖲𝖾𝗅𝖾𝖼𝗍 𝗒𝗈𝗎𝗋 𝗅𝖺𝗇𝗀𝗎𝖺𝗀𝖾𝗌 ☟", callback_data="ident"
            )
        ],
    )
    req = query.from_user.id
    offset = 0
    btn.append([InlineKeyboardButton(text="Back to files", callback_data=f"next_{req}_{key}_{offset}")])

    await query.edit_message_reply_markup(InlineKeyboardMarkup(btn))


@Client.on_callback_query(filters.regex(r"^fl#"))
async def filter_languages_cb_handler(client: Client, query: CallbackQuery):
    _, lang, search, key = query.data.split("#")

    search = search.replace("_", " ")
    req = query.from_user.id
    chat_id = query.message.chat.id
    message = query.message
    if int(req) not in [query.message.reply_to_message.from_user.id, 0]:
        return await query.answer(
            f"⚠️ ʜᴇʟʟᴏ{query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇQᴜᴇꜱᴛ,\nʀᴇ𝚀ᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
            show_alert=True,
        )

    search = f"{search} {lang}" 

    files, _, _ = await get_search_results(chat_id, search, max_results=10)
    files = [file for file in files if re.search(lang, file.file_name, re.IGNORECASE)]
    if not files:
        await query.answer("No files were found", show_alert=1)
        return

    settings = await get_settings(message.chat.id)
    if 'is_shortlink' in settings.keys():
        ENABLE_SHORTLINK = settings['is_shortlink']
    else:
        await save_group_settings(message.chat.id, 'is_shortlink', False)
        ENABLE_SHORTLINK = False
    pre = 'filep' if settings['file_secure'] else 'file'
    if ENABLE_SHORTLINK == True:
        btn = (
            [
                [
                    InlineKeyboardButton(
                        text=f"[{get_size(file.file_size)}] {file.file_name}",
                        url=await get_shortlink(
                            message.chat.id,
                            f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}",
                        ),
                    ),
                ]
                for file in files
            ]
            if settings["button"]
            else [
                [
                    InlineKeyboardButton(
                        text=f"{file.file_name}",
                        url=await get_shortlink(
                            message.chat.id,
                            f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}",
                        ),
                    ),
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)}",
                        url=await get_shortlink(
                            message.chat.id,
                            f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}",
                        ),
                    ),
                ]
                for file in files
            ]
        )
    elif settings["button"]:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"[{get_size(file.file_size)}] {file.file_name}", callback_data=f'{pre}#{file.file_id}'
                ),
            ]
            for file in files
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{file.file_name}",
                    callback_data=f'{pre}#{file.file_id}',
                ),
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)}",
                    callback_data=f'{pre}#{file.file_id}',
                ),
            ]
            for file in files
        ]
    try:
        if settings['auto_delete']:
            btn.insert(
                0,
                [
                    InlineKeyboardButton('ɪɴꜰᴏ', 'reqinfo'),
                    InlineKeyboardButton('ᴍᴏᴠɪᴇ', 'minfo'),
                    InlineKeyboardButton('ꜱᴇʀɪᴇꜱ', 'sinfo'),
                ],
            )

        else:
            btn.insert(
                0,
                [
                    InlineKeyboardButton('ᴍᴏᴠɪᴇ', 'minfo'),
                    InlineKeyboardButton('ꜱᴇʀɪᴇꜱ', 'sinfo'),
                ],
            )

    except KeyError:
        grpid = await active_connection(str(message.from_user.id))
        await save_group_settings(grpid, 'auto_delete', True)
        settings = await get_settings(message.chat.id)
        if settings['auto_delete']:
            btn.insert(
                0,
                [
                    InlineKeyboardButton('ɪɴꜰᴏ', 'reqinfo'),
                    InlineKeyboardButton('ᴍᴏᴠɪᴇ', 'minfo'),
                    InlineKeyboardButton('ꜱᴇʀɪᴇꜱ', 'sinfo'),
                ],
            )

        else:
            btn.insert(
                0,
                [
                    InlineKeyboardButton('ᴍᴏᴠɪᴇ', 'minfo'),
                    InlineKeyboardButton('ꜱᴇʀɪᴇꜱ', 'sinfo'),
                ],
            )

    btn.insert(0, [
        InlineKeyboardButton("⚡ ʜᴏᴡ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ⚡", url=f"{HOW_TO_DOWNLOAD}")
    ])
    offset = 0

    btn.append(        [
            InlineKeyboardButton(
                text="↺ ʙᴀᴄᴋ ᴛᴏ ꜰɪʟᴇ ↻",
                callback_data=f"next_{req}_{key}_{offset}"
                ),
        ])


    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))




#languages


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "gfiltersdeleteallconfirm":
        await del_allg(query.message, 'gfilters')
        await query.answer("Done !")
        return
    elif query.data == "gfiltersdeleteallcancel": 
        await query.message.reply_to_message.delete()
        await query.message.delete()
        await query.answer("Process Cancelled !")
        return
    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            grpid = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("Mᴀᴋᴇ sᴜʀᴇ I'ᴍ ᴘʀᴇsᴇɴᴛ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ!!", quote=True)
                    return await query.answer(MSG_ALRT)
            else:
                await query.message.edit_text(
                    "I'ᴍ ɴᴏᴛ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ ᴀɴʏ ɢʀᴏᴜᴘs!\nCʜᴇᴄᴋ /connections ᴏʀ ᴄᴏɴɴᴇᴄᴛ ᴛᴏ ᴀɴʏ ɢʀᴏᴜᴘs",
                    quote=True
                )
                return await query.answer(MSG_ALRT)

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return await query.answer(MSG_ALRT)

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
            await del_all(query.message, grp_id, title)
        else:
            await query.answer("Yᴏᴜ ɴᴇᴇᴅ ᴛᴏ ʙᴇ Gʀᴏᴜᴘ Oᴡɴᴇʀ ᴏʀ ᴀɴ Aᴜᴛʜ Usᴇʀ ᴛᴏ ᴅᴏ ᴛʜᴀᴛ!", show_alert=True)
    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer("Tʜᴀᴛ's ɴᴏᴛ ғᴏʀ ʏᴏᴜ!!", show_alert=True)
    elif "groupcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton("DELETE", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("BACK", callback_data="backcb")]
        ])

        await query.message.edit_text(
            f"Gʀᴏᴜᴘ Nᴀᴍᴇ : **{title}**\nGʀᴏᴜᴘ ID : `{group_id}`",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return await query.answer(MSG_ALRT)
    elif "connectcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title

        user_id = query.from_user.id

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"Cᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text('Sᴏᴍᴇ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ!!', parse_mode=enums.ParseMode.MARKDOWN)
        return await query.answer(MSG_ALRT)
    elif "disconnect" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"Dɪsᴄᴏɴɴᴇᴄᴛᴇᴅ ғʀᴏᴍ **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text(
                f"Sᴏᴍᴇ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer(MSG_ALRT)
    elif "deletecb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ᴄᴏɴɴᴇᴄᴛɪᴏɴ !"
            )
        else:
            await query.message.edit_text(
                f"Sᴏᴍᴇ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer(MSG_ALRT)
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "Tʜᴇʀᴇ ᴀʀᴇ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴄᴏɴɴᴇᴄᴛɪᴏɴs!! Cᴏɴɴᴇᴄᴛ ᴛᴏ sᴏᴍᴇ ɢʀᴏᴜᴘs ғɪʀsᴛ.",
            )
            return await query.answer(MSG_ALRT)
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Yᴏᴜʀ ᴄᴏɴɴᴇᴄᴛᴇᴅ ɢʀᴏᴜᴘ ᴅᴇᴛᴀɪʟs ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    elif "gfilteralert" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_gfilter('gfilters', keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    if query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('Nᴏ sᴜᴄʜ ғɪʟᴇ ᴇxɪsᴛ.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        settings = await get_settings(query.message.chat.id)
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"

        try:
            if (AUTH_CHANNEL or REQ_CHANNEL) and not await is_subscribed(client, query):
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            elif settings['botpm']:
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            else:
                await client.send_cached_media(
                    chat_id=query.from_user.id,
                    file_id=file_id,
                    caption=f_caption,
                    protect_content=True if ident == "filep" else False,
                    reply_markup=InlineKeyboardMarkup(
                        [
                         [
                          InlineKeyboardButton("🔰 ᴊᴏɪɴ ꜰᴏʀ ᴍᴏᴠɪᴇs​ 🔰", url="https://t.me/at3movies")
                         ]
                        ]
                    )
                )
                await query.answer('Cʜᴇᴄᴋ PM, I ʜᴀᴠᴇ sᴇɴᴛ ғɪʟᴇs ɪɴ PM', show_alert=True)
        except UserIsBlocked:
            await query.answer('Uɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ ᴍᴀʜɴ !', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
        except Exception as e:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
    elif query.data.startswith("checksub"):
        if (AUTH_CHANNEL or REQ_CHANNEL) and not await is_subscribed(client, query):
            await query.answer("Jᴏɪɴ ᴏᴜʀ Bᴀᴄᴋ-ᴜᴘ ᴄʜᴀɴɴᴇʟ ᴍᴀʜɴ! 😒", show_alert=True)
            return
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('Nᴏ sᴜᴄʜ ғɪʟᴇ ᴇxɪsᴛ.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption
        if f_caption is None:
            f_caption = f"{title}"
        await query.answer()
        await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f_caption,
            protect_content=True if ident == 'checksubp' else False,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                  InlineKeyboardButton('🚸 ᴅᴇʟᴇᴛᴇ​', callback_data='delf')
                 ]
                ]
            )
        )
    elif query.data == "pages":
        await query.answer()

    elif query.data.startswith("opnsetgrp"):
        ident, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        st = await client.get_chat_member(grp_id, userid)
        if (
                st.status != enums.ChatMemberStatus.ADMINISTRATOR
                and st.status != enums.ChatMemberStatus.OWNER
                and str(userid) not in ADMINS
        ):
            await query.answer("Yᴏᴜ Dᴏɴ'ᴛ Hᴀᴠᴇ Tʜᴇ Rɪɢʜᴛs Tᴏ Dᴏ Tʜɪs !", show_alert=True)
            return
        title = query.message.chat.title
        settings = await get_settings(grp_id)
        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Fɪʟᴛᴇʀ Bᴜᴛᴛᴏɴ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Sɪɴɢʟᴇ' if settings["button"] else 'Dᴏᴜʙʟᴇ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Fɪʟᴇ Sᴇɴᴅ Mᴏᴅᴇ', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Mᴀɴᴜᴀʟ Sᴛᴀʀᴛ' if settings["botpm"] else 'Aᴜᴛᴏ Sᴇɴᴅ',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Pʀᴏᴛᴇᴄᴛ Cᴏɴᴛᴇɴᴛ',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["file_secure"] else '✘ Oғғ',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Iᴍᴅʙ', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["imdb"] else '✘ Oғғ',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Sᴘᴇʟʟ Cʜᴇᴄᴋ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["spell_check"] else '✘ Oғғ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Wᴇʟᴄᴏᴍᴇ Msɢ', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["welcome"] else '✘ Oғғ',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Aᴜᴛᴏ-Dᴇʟᴇᴛᴇ',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                    InlineKeyboardButton('10 Mɪɴs' if settings["auto_delete"] else '✘ Oғғ',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Aᴜᴛᴏ-Fɪʟᴛᴇʀ',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["auto_ffilter"] else '✘ Oғғ',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Mᴀx Bᴜᴛᴛᴏɴs',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                    InlineKeyboardButton('10' if settings["max_btn"] else f'{MAX_B_TN}',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ShortLink',
                                         callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["is_shortlink"] else '✘ Oғғ',
                                         callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_text(
                text=f"<b>Cʜᴀɴɢᴇ Yᴏᴜʀ Sᴇᴛᴛɪɴɢs Fᴏʀ {title} As Yᴏᴜʀ Wɪsʜ ⚙</b>",
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML
            )
            await query.message.edit_reply_markup(reply_markup)
        
    elif query.data.startswith("opnsetpm"):
        ident, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        st = await client.get_chat_member(grp_id, userid)
        if (
                st.status != enums.ChatMemberStatus.ADMINISTRATOR
                and st.status != enums.ChatMemberStatus.OWNER
                and str(userid) not in ADMINS
        ):
            await query.answer("Yᴏᴜ Dᴏɴ'ᴛ Hᴀᴠᴇ Tʜᴇ Rɪɢʜᴛs Tᴏ Dᴏ Tʜɪs !", show_alert=True)
            return
        title = query.message.chat.title
        settings = await get_settings(grp_id)
        btn2 = [[
                 InlineKeyboardButton("Cʜᴇᴄᴋ PM", url=f"t.me/{temp.U_NAME}")
               ]]
        reply_markup = InlineKeyboardMarkup(btn2)
        await query.message.edit_text(f"<b>Yᴏᴜʀ sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ ғᴏʀ {title} ʜᴀs ʙᴇᴇɴ sᴇɴᴛ ᴛᴏ ʏᴏᴜʀ PM</b>")
        await query.message.edit_reply_markup(reply_markup)
        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Fɪʟᴛᴇʀ Bᴜᴛᴛᴏɴ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Sɪɴɢʟᴇ' if settings["button"] else 'Dᴏᴜʙʟᴇ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Fɪʟᴇ Sᴇɴᴅ Mᴏᴅᴇ', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Mᴀɴᴜᴀʟ Sᴛᴀʀᴛ' if settings["botpm"] else 'Aᴜᴛᴏ Sᴇɴᴅ',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Pʀᴏᴛᴇᴄᴛ Cᴏɴᴛᴇɴᴛ',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["file_secure"] else '✘ Oғғ',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Iᴍᴅʙ', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["imdb"] else '✘ Oғғ',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Sᴘᴇʟʟ Cʜᴇᴄᴋ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["spell_check"] else '✘ Oғғ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Wᴇʟᴄᴏᴍᴇ Msɢ', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["welcome"] else '✘ Oғғ',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Aᴜᴛᴏ-Dᴇʟᴇᴛᴇ',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                    InlineKeyboardButton('10 Mɪɴs' if settings["auto_delete"] else '✘ Oғғ',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Aᴜᴛᴏ-Fɪʟᴛᴇʀ',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["auto_ffilter"] else '✘ Oғғ',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Mᴀx Bᴜᴛᴛᴏɴs',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                    InlineKeyboardButton('10' if settings["max_btn"] else f'{MAX_B_TN}',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ShortLink',
                                         callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["is_shortlink"] else '✘ Oғғ',
                                         callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await client.send_message(
                chat_id=userid,
                text=f"<b>Cʜᴀɴɢᴇ Yᴏᴜʀ Sᴇᴛᴛɪɴɢs Fᴏʀ {title} As Yᴏᴜʀ Wɪsʜ ⚙</b>",
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
                reply_to_message_id=query.message.id
            )

    elif query.data.startswith("show_option"):
        ident, from_user = query.data.split("#")
        btn = [[
                InlineKeyboardButton("Uɴᴀᴠᴀɪʟᴀʙʟᴇ", callback_data=f"unavailable#{from_user}"),
                InlineKeyboardButton("Uᴘʟᴏᴀᴅᴇᴅ", callback_data=f"uploaded#{from_user}")
             ],[
                InlineKeyboardButton("Aʟʀᴇᴀᴅʏ Aᴠᴀɪʟᴀʙʟᴇ", callback_data=f"already_available#{from_user}")
              ]]
        btn2 = [[
                 InlineKeyboardButton("Vɪᴇᴡ Sᴛᴀᴛᴜs", url=f"{query.message.link}")
               ]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Hᴇʀᴇ ᴀʀᴇ ᴛʜᴇ ᴏᴘᴛɪᴏɴs !")
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)
        
    elif query.data.startswith("unavailable"):
        ident, from_user = query.data.split("#")
        btn = [[
                InlineKeyboardButton("⚠️ Uɴᴀᴠᴀɪʟᴀʙʟᴇ ⚠️", callback_data=f"unalert#{from_user}")
              ]]
        btn2 = [[
                 InlineKeyboardButton("Vɪᴇᴡ Sᴛᴀᴛᴜs", url=f"{query.message.link}")
               ]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Sᴇᴛ ᴛᴏ Uɴᴀᴠᴀɪʟᴀʙʟᴇ !")
            try:
                await client.send_message(chat_id=int(from_user), text=f"<b>Hᴇʏ {user.mention}, Sᴏʀʀʏ Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ɪs ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ. Sᴏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs ᴄᴀɴ'ᴛ ᴜᴘʟᴏᴀᴅ ɪᴛ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
            except UserIsBlocked:
                await client.send_message(chat_id=int(SUPPORT_CHAT_ID), text=f"<b>Hᴇʏ {user.mention}, Sᴏʀʀʏ Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ɪs ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ. Sᴏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs ᴄᴀɴ'ᴛ ᴜᴘʟᴏᴀᴅ ɪᴛ.\n\nNᴏᴛᴇ: Tʜɪs ᴍᴇssᴀɢᴇ ɪs sᴇɴᴛ ᴛᴏ ᴛʜɪs ɢʀᴏᴜᴘ ʙᴇᴄᴀᴜsᴇ ʏᴏᴜ'ᴠᴇ ʙʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ. Tᴏ sᴇɴᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ ʏᴏᴜʀ PM, Mᴜsᴛ ᴜɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

    elif query.data.startswith("uploaded"):
        ident, from_user = query.data.split("#")
        btn = [[
                InlineKeyboardButton("✅ Uᴘʟᴏᴀᴅᴇᴅ ✅", callback_data=f"upalert#{from_user}")
              ]]
        btn2 = [[
                 InlineKeyboardButton("Vɪᴇᴡ Sᴛᴀᴛᴜs", url=f"{query.message.link}")
               ]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Sᴇᴛ ᴛᴏ Uᴘʟᴏᴀᴅᴇᴅ !")
            try:
                await client.send_message(chat_id=int(from_user), text=f"<b>Hᴇʏ {user.mention}, Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ʜᴀs ʙᴇᴇɴ ᴜᴘʟᴏᴀᴅᴇᴅ ʙʏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs. Kɪɴᴅʟʏ sᴇᴀʀᴄʜ ᴀɢᴀɪɴ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
            except UserIsBlocked:
                await client.send_message(chat_id=int(SUPPORT_CHAT_ID), text=f"<b>Hᴇʏ {user.mention}, Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ʜᴀs ʙᴇᴇɴ ᴜᴘʟᴏᴀᴅᴇᴅ ʙʏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs. Kɪɴᴅʟʏ sᴇᴀʀᴄʜ ᴀɢᴀɪɴ.\n\nNᴏᴛᴇ: Tʜɪs ᴍᴇssᴀɢᴇ ɪs sᴇɴᴛ ᴛᴏ ᴛʜɪs ɢʀᴏᴜᴘ ʙᴇᴄᴀᴜsᴇ ʏᴏᴜ'ᴠᴇ ʙʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ. Tᴏ sᴇɴᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ ʏᴏᴜʀ PM, Mᴜsᴛ ᴜɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

    elif query.data.startswith("already_available"):
        ident, from_user = query.data.split("#")
        btn = [[
                InlineKeyboardButton("🟢 Aʟʀᴇᴀᴅʏ Aᴠᴀɪʟᴀʙʟᴇ 🟢", callback_data=f"alalert#{from_user}")
              ]]
        btn2 = [[
                 InlineKeyboardButton("Vɪᴇᴡ Sᴛᴀᴛᴜs", url=f"{query.message.link}")
               ]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Sᴇᴛ ᴛᴏ Aʟʀᴇᴀᴅʏ Aᴠᴀɪʟᴀʙʟᴇ !")
            try:
                await client.send_message(chat_id=int(from_user), text=f"<b>Hᴇʏ {user.mention}, Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ɪs ᴀʟʀᴇᴀᴅʏ ᴀᴠᴀɪʟᴀʙʟᴇ ᴏɴ ᴏᴜʀ ʙᴏᴛ's ᴅᴀᴛᴀʙᴀsᴇ. Kɪɴᴅʟʏ sᴇᴀʀᴄʜ ᴀɢᴀɪɴ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
            except UserIsBlocked:
                await client.send_message(chat_id=int(SUPPORT_CHAT_ID), text=f"<b>Hᴇʏ {user.mention}, Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ɪs ᴀʟʀᴇᴀᴅʏ ᴀᴠᴀɪʟᴀʙʟᴇ ᴏɴ ᴏᴜʀ ʙᴏᴛ's ᴅᴀᴛᴀʙᴀsᴇ. Kɪɴᴅʟʏ sᴇᴀʀᴄʜ ᴀɢᴀɪɴ.\n\nNᴏᴛᴇ: Tʜɪs ᴍᴇssᴀɢᴇ ɪs sᴇɴᴛ ᴛᴏ ᴛʜɪs ɢʀᴏᴜᴘ ʙᴇᴄᴀᴜsᴇ ʏᴏᴜ'ᴠᴇ ʙʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ. Tᴏ sᴇɴᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ ʏᴏᴜʀ PM, Mᴜsᴛ ᴜɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

    elif query.data.startswith("alalert"):
        ident, from_user = query.data.split("#")
        if int(query.from_user.id) == int(from_user):
            user = await client.get_users(from_user)
            await query.answer(f"Hᴇʏ {user.first_name}, Yᴏᴜʀ Rᴇᴏ̨ᴜᴇsᴛ ɪs Aʟʀᴇᴀᴅʏ Aᴠᴀɪʟᴀʙʟᴇ !", show_alert=True)
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

    elif query.data.startswith("upalert"):
        ident, from_user = query.data.split("#")
        if int(query.from_user.id) == int(from_user):
            user = await client.get_users(from_user)
            await query.answer(f"Hᴇʏ {user.first_name}, Yᴏᴜʀ Rᴇᴏ̨ᴜᴇsᴛ ɪs Uᴘʟᴏᴀᴅᴇᴅ !", show_alert=True)
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)
        
    elif query.data.startswith("unalert"):
        ident, from_user = query.data.split("#")
        if int(query.from_user.id) == int(from_user):
            user = await client.get_users(from_user)
            await query.answer(f"Hᴇʏ {user.first_name}, Yᴏᴜʀ Rᴇᴏ̨ᴜᴇsᴛ ɪs Uɴᴀᴠᴀɪʟᴀʙʟᴇ !", show_alert=True)
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

    elif query.data == "info":
        await query.answer(text=script.INFO, show_alert=True)

    elif query.data == "format":
        await query.answer(text=script.FORMAT, show_alert=True)

    elif query.data == "tips":
        await query.answer(text=script.TIPS, show_alert=True)

    elif query.data == "whyjoin":
        await query.answer(text=script.WHYJOIN, show_alert=True)

    elif query.data == "delf":
        await query.answer(text=script.DELF, show_alert=True)
   
    elif query.data == "rendering_info":
        await query.answer(text=script.RENDERING_TXT, show_alert=True)

    elif query.data == "start":
        buttons = [[
            InlineKeyboardButton('➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
            ],[
            InlineKeyboardButton('◈ ᴜᴩᴅᴀᴛᴇꜱ ◈', url='https://t.me/Hs_Botz'),
            InlineKeyboardButton('♚ ᴏᴡɴᴇʀ ♚', callback_data='owner_info')
            ],[      
            InlineKeyboardButton('〄 ʜᴇʟᴘ 〄', callback_data='help2'),
            InlineKeyboardButton('⍟ ᴀʙᴏᴜᴛ ⍟', callback_data='about')
            ],[
            InlineKeyboardButton('✘ ꜱᴜᴩᴩᴏʀᴛ ᴍʏ ᴄʜᴀɴɴᴇʟꜱ ✘', callback_data='support_group')
        ]]                          
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        await query.answer(MSG_ALRT)

    elif query.data == "group_info":
        buttons = [[
            InlineKeyboardButton('ꜱɪᴛᴀ ʙᴏᴛ ʟᴏɢs', url="https://t.me"),
        ],[
            InlineKeyboardButton('ɢʀᴏᴜᴘ', url="https://t.me/at3movies"),
            InlineKeyboardButton('ᴄʜᴀɴɴᴇʟ', url="https://t.me/CinemaKovilakam")
        ],[
            InlineKeyboardButton('ᴜᴘᴅᴀᴛᴇs', url="https://t.me/MLZ_BOTZ"),
            InlineKeyboardButton('ꜱᴜᴘᴘᴏʀᴛ', url="https://t.me/MLZ_BOTZ_SUPPORT")
        ],[
            InlineKeyboardButton('⇍ʙᴀᴄᴋ​', callback_data='about')
        ]]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.GROUP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "filters":
        buttons = [[
            InlineKeyboardButton('ᴍᴀɴᴜᴀʟ ꜰɪʟᴛᴇʀ', callback_data='manuelfilter'),
            InlineKeyboardButton('ᴀᴜᴛᴏ ꜰɪʟᴛᴇʀ', callback_data='autofilter')
        ],[
            InlineKeyboardButton('⇍ʙᴀᴄᴋ', callback_data='help2'),
            InlineKeyboardButton('ɢʟᴏʙᴀʟ ꜰɪʟᴛᴇʀs​', callback_data='global_filters')
        ]]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.ALL_FILTERS.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "global_filters":
        buttons = [[
            InlineKeyboardButton('⇍ʙᴀᴄᴋ', callback_data='filters')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.GFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "support_group":
        buttons = [[
            InlineKeyboardButton('⇍ʙᴀᴄᴋ', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.GRP_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "share_txt":
        buttons = [[
            InlineKeyboardButton('⇍ʙᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.SHARE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "restric":
        buttons = [[
            InlineKeyboardButton('⇍ʙᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.RESTRIC_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "pin":
        buttons = [[
            InlineKeyboardButton('⇍ʙᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.PIN_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "zombies":
        buttons = [[
            InlineKeyboardButton('⇍ʙᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.ZOMBIES_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )    
    elif query.data == "help2":
        buttons = [[
            InlineKeyboardButton('🔋  ᴍᴏʀᴇ ꜰᴇᴀᴛᴜʀᴇꜱ  🔋', callback_data='help')
        ], [
            InlineKeyboardButton('ꜰɪʟᴛᴇʀs', callback_data='filters'),
            InlineKeyboardButton('ꜰɪʟᴇ sᴛᴏʀᴇ', callback_data='store_file')
        ], [
            InlineKeyboardButton('ᴄᴏɴɴᴇᴄᴛɪᴏɴ', callback_data='coct'),
            InlineKeyboardButton('ᴇxᴛʀᴀ ᴍᴏᴅs', callback_data='extra')
        ], [
            InlineKeyboardButton('♙ ʜᴏᴍᴇ', callback_data='start'),
            InlineKeyboardButton('♖ ꜱᴛᴀᴛᴜꜱ', callback_data='stats')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.HELPER_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('sʜᴀʀᴇ ᴛᴇxᴛ​', callback_data='share_txt'),
            InlineKeyboardButton('ɢᴇɴ-ᴘᴀss​', callback_data='gen_pass'),
            InlineKeyboardButton('ᴛᴇʟᴇɢʀᴀᴘʜ​', callback_data='tele')    
         ], [
            InlineKeyboardButton('ᴘɪɴ​', callback_data='pin'),
            InlineKeyboardButton('ᴋɪᴄᴋ', callback_data='zombies'),
            InlineKeyboardButton('ᴍᴜᴛᴇ', callback_data='restric')
         ], [
            InlineKeyboardButton('ᴀᴜᴅʙᴏᴏᴋ', callback_data='abook'),
            InlineKeyboardButton('ᴄᴏᴜɴᴛʀʏ', callback_data='country'),
            InlineKeyboardButton('ᴄᴀʀʙᴏɴ', callback_data='carb')    
         ], [
            InlineKeyboardButton('ᴘɪɴɢ', callback_data='pings'),
            InlineKeyboardButton('ᴊsᴏɴᴇ', callback_data='json'),
            InlineKeyboardButton('sᴛɪᴄᴋɪᴅ', callback_data='sticker')
         ], [
            InlineKeyboardButton('ᴡʜᴏɪs', callback_data='whois'),
            InlineKeyboardButton('ᴜʀʟsʜᴏʀᴛ', callback_data='urlshort'),
            InlineKeyboardButton('ɢᴛʀᴀɴs', callback_data='gtrans')
         ], [
            InlineKeyboardButton('sᴏɴɢ', callback_data='song'),
            InlineKeyboardButton('ᴛᴛs', callback_data='tts'),  
            InlineKeyboardButton('ɢᴀᴍᴇs', callback_data='fun')     
         ], [
            InlineKeyboardButton('ᴠɪᴅᴇᴏ', callback_data='video'),
            InlineKeyboardButton('ғᴏɴᴛ', callback_data='font'),
            InlineKeyboardButton('ᴅᴇᴘʟᴏʏ', callback_data='deploy')
         ], [ 
            InlineKeyboardButton('↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ​↭', callback_data='help2')
         ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(                     
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "about":
        buttons = [[
            InlineKeyboardButton('✧ ᴜᴘᴅᴀᴛᴇs ​✧', callback_data='group_info'),
            InlineKeyboardButton('✧ sᴏᴜʀᴄᴇ​ ✧', callback_data='source')
        ],[
            InlineKeyboardButton('🛰 ʀᴇɴᴅᴇʀɪɴɢ ɪɴꜰᴏ ☁️', callback_data='rendering_info')
        ],[
            InlineKeyboardButton('♙ ʜᴏᴍᴇ', callback_data='start'),
            InlineKeyboardButton('ᴄʟᴏsᴇ ⊝', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.ABOUT_TXT.format(temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "source":
        buttons = [[
            InlineKeyboardButton('⇍ʙᴀᴄᴋ', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.SOURCE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "gen_pass":
        buttons = [[
            InlineKeyboardButton('⇍ʙᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.GEN_PASS,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "manuelfilter":
        buttons = [[
            InlineKeyboardButton('⇍ʙᴀᴄᴋ', callback_data='filters'),
            InlineKeyboardButton('Bᴜᴛᴛᴏɴs', callback_data='button')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.MANUELFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "button":
        buttons = [[
            InlineKeyboardButton('⇍ʙᴀᴄᴋ', callback_data='manuelfilter')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.BUTTON_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "autofilter":
        buttons = [[
            InlineKeyboardButton('⇍ʙᴀᴄᴋ', callback_data='filters')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.AUTOFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "coct":
        buttons = [[
            InlineKeyboardButton('⇍ʙᴀᴄᴋ', callback_data='help2')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "extra":
        buttons = [[
            InlineKeyboardButton('⇍ʙᴀᴄᴋ', callback_data='help2')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.EXTRAMOD_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    
    elif query.data == "store_file":
        buttons = [[
            InlineKeyboardButton('⇍ʙᴀᴄᴋ', callback_data='help2')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )   
        await query.message.edit_text(
            text=script.FILE_STORE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "video":
        buttons = [[
            InlineKeyboardButton('⇍Bᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.VIDEO_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "song":
        buttons = [[
            InlineKeyboardButton('⇍Bᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.SONG_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "tts":
        buttons = [[
            InlineKeyboardButton('⇍Bᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.TTS_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "gtrans":
        buttons = [[
            InlineKeyboardButton('⇍Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('𝙻𝙰𝙽𝙶 𝙲𝙾𝙳𝙴𝚂', url='https://cloud.google.com/translate/docs/languages')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.GTRANS_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "country":
        buttons = [[
            InlineKeyboardButton('⇍Bᴀᴄᴋ', callback_data='help'),
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.CON_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "tele":
        buttons = [[
            InlineKeyboardButton('⇍Bᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.TELE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "corona":
        buttons = [[
            InlineKeyboardButton('⇍Bᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.CORONA_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "font":
        buttons = [[
            InlineKeyboardButton('⇍Bᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.FONT_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "carb":
        buttons = [[
            InlineKeyboardButton('⇍Bᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.CARB_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    
    elif query.data == "admin":
        buttons = [[
            InlineKeyboardButton('⇍ʙᴀᴄᴋ', callback_data='owner_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        if query.from_user.id in ADMINS:
            await query.message.edit_text(text=script.ADMIN_TXT, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
        else:
            await query.answer("⚠ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ⚠\n\nIᴛꜱ ᴏɴʟʏ ғᴏʀ ᴍʏ ADMINS\n\n©ᴍʟᴢ ʙᴏᴛᴢ", show_alert=True)

    elif query.data == "json":
        buttons = [[
            InlineKeyboardButton('⇍Bᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.JSON_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "urlshort":
        buttons = [[
            InlineKeyboardButton('⇍Bᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.URLSHORT_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "whois":
        buttons = [[
            InlineKeyboardButton('⇍Bᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.WHOIS_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "abook":
        buttons = [[
            InlineKeyboardButton('⇍Bᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.ABOOK_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "deploy":
        buttons = [[
           InlineKeyboardButton('ʀᴇᴘᴏ', url='https://github.com/CrazyDeveloperTG/Doctor-Strange'),
           InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', url='https://t.me/czdbotz_support')
        ], [
            InlineKeyboardButton('⇍Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('ᴜᴘᴅᴀᴛᴇs', url='https://t.me/MLZ_BOTZ')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.DEPLOY_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "sticker":
        buttons = [[
            InlineKeyboardButton('⇍Bᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.STICKER_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "pings":
        buttons = [[
            InlineKeyboardButton('⇍Bᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.PINGS_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "fun":
        buttons = [[
            InlineKeyboardButton('⇍Bᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )
        await query.message.edit_text(
            text=script.FUN_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "stats":
        buttons = [[
            InlineKeyboardButton('⇍Bᴀᴄᴋ', callback_data='help2'),
            InlineKeyboardButton('⟲ Rᴇғʀᴇsʜ', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )     
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )  
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "rfrsh":
        await query.answer("Fetching MongoDb DataBase")
        buttons = [[
            InlineKeyboardButton('⇍Bᴀᴄᴋ', callback_data='help2'),
            InlineKeyboardButton('⟲ Rᴇғʀᴇsʜ', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="▣ ▢ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▢"
        )
        await query.message.edit_text(
            text="▣ ▣ ▣"
        )      
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        ) 
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "owner_info":
            btn = [[
                    InlineKeyboardButton("⇍ʙᴀᴄᴋ", callback_data="start"),
                    InlineKeyboardButton("Sᴜᴅᴏ", callback_data="admin")
                  ]]
            reply_markup = InlineKeyboardMarkup(btn)
            await client.edit_message_media(
                query.message.chat.id, 
                query.message.id, 
                InputMediaPhoto(random.choice(PICS))
            )           
            await query.message.edit_text(
                text=(script.OWNER_INFO),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )

    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))

        if str(grp_id) != str(grpid):
            await query.message.edit("Yᴏᴜʀ Aᴄᴛɪᴠᴇ Cᴏɴɴᴇᴄᴛɪᴏɴ Hᴀs Bᴇᴇɴ Cʜᴀɴɢᴇᴅ. Gᴏ Tᴏ /connections ᴀɴᴅ ᴄʜᴀɴɢᴇ ʏᴏᴜʀ ᴀᴄᴛɪᴠᴇ ᴄᴏɴɴᴇᴄᴛɪᴏɴ.")
            return await query.answer(MSG_ALRT)

        if set_type == 'is_shortlink' and query.from_user.id not in ADMINS:
            return await query.answer(text=f"Hey {query.from_user.first_name}, You can't change shortlink settings for your group !\n\nIt's an admin only setting !", show_alert=True)

        if status == "True":
            await save_group_settings(grpid, set_type, False)
        else:
            await save_group_settings(grpid, set_type, True)

        settings = await get_settings(grpid)

        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Fɪʟᴛᴇʀ Bᴜᴛᴛᴏɴ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Sɪɴɢʟᴇ' if settings["button"] else 'Dᴏᴜʙʟᴇ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Fɪʟᴇ Sᴇɴᴅ Mᴏᴅᴇ', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Mᴀɴᴜᴀʟ Sᴛᴀʀᴛ' if settings["botpm"] else 'Aᴜᴛᴏ Sᴇɴᴅ',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Pʀᴏᴛᴇᴄᴛ Cᴏɴᴛᴇɴᴛ',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["file_secure"] else '✘ Oғғ',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Iᴍᴅʙ', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["imdb"] else '✘ Oғғ',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Sᴘᴇʟʟ Cʜᴇᴄᴋ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["spell_check"] else '✘ Oғғ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Wᴇʟᴄᴏᴍᴇ Msɢ', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["welcome"] else '✘ Oғғ',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Aᴜᴛᴏ-Dᴇʟᴇᴛᴇ',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                    InlineKeyboardButton('10 Mɪɴs' if settings["auto_delete"] else '✘ Oғғ',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Aᴜᴛᴏ-Fɪʟᴛᴇʀ',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["auto_ffilter"] else '✘ Oғғ',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Mᴀx Bᴜᴛᴛᴏɴs',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                    InlineKeyboardButton('10' if settings["max_btn"] else f'{MAX_B_TN}',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ShortLink',
                                         callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["is_shortlink"] else '✘ Oғғ',
                                         callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)
    await query.answer(MSG_ALRT)

    
async def auto_filter(client, msg, spoll=False):
    reqstr1 = msg.from_user.id if msg.from_user else 0
    reqstr = await client.get_users(reqstr1)
    if not spoll:
        message = msg
        settings = await get_settings(message.chat.id)
        if message.text.startswith("/"): return  # ignore commands
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if len(message.text) < 100:
            search = message.text
            files, offset, total_results = await get_search_results(message.chat.id ,search.lower(), offset=0, filter=True)
            if not files:
                if settings["spell_check"]:
                    return await advantage_spell_chok(client, msg)
                else:
                    if NO_RESULTS_MSG:
                        await client.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, search)))
                    return
        else:
            return
    else:
        message = msg.message.reply_to_message  # msg will be callback query
        search, files, offset, total_results = spoll
    settings = await get_settings(message.chat.id)
    if 'is_shortlink' in settings.keys():
        ENABLE_SHORTLINK = settings['is_shortlink']
    else:
        await save_group_settings(message.chat.id, 'is_shortlink', False)
        ENABLE_SHORTLINK = False
    pre = 'filep' if settings['file_secure'] else 'file'
    if ENABLE_SHORTLINK == True:
        if settings["button"]:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)} {file.file_name}", url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                ]
                for file in files
            ]
        else:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{file.file_name}",
                        url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)}",
                        url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                ]
                for file in files
            ]
    else:
        if settings["button"]:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)} {file.file_name}", callback_data=f'{pre}#{file.file_id}'
                    ),
                ]
                for file in files
            ]
        else:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{file.file_name}",
                        callback_data=f'{pre}#{file.file_id}',
                    ),
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)}",
                        callback_data=f'{pre}#{file.file_id}',
                    ),
                ]
                for file in files
            ]

    try:
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        if settings['auto_delete']:
            btn.insert(0, 
                [
                    InlineKeyboardButton(f'ɪɴꜰᴏ', 'info'),
                    InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇꜱ", callback_data=f"languages#{search.replace(' ', '_')}#{key}"),
                    InlineKeyboardButton(f'ᴛɪᴘs​', 'tips')
                ]
            )

        else:
            btn.insert(0, 
                [
                    InlineKeyboardButton(f'ɪɴꜰᴏ', 'info'),
                    InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇꜱ", callback_data=f"languages#{search.replace(' ', '_')}#{key}"),
                    InlineKeyboardButton(f'ᴛɪᴘs​', 'tips')
                ]
            )
                
    except KeyError:
        grpid = await active_connection(str(message.from_user.id))
        await save_group_settings(grpid, 'auto_delete', True)
        settings = await get_settings(message.chat.id)
        if settings['auto_delete']:
            btn.insert(0, 
                [
                    InlineKeyboardButton(f'ɪɴꜰᴏ', 'info'),
                    InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇꜱ", callback_data=f"languages#{search.replace(' ', '_')}#{key}"),
                    InlineKeyboardButton(f'ᴛɪᴘs​', 'tips')
                ]
            )

        else:
            btn.insert(0, 
                [
                    InlineKeyboardButton(f'ɪɴꜰᴏ', 'info'),
                    InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇꜱ", callback_data=f"languages#{search.replace(' ', '_')}#{key}"),
                    InlineKeyboardButton(f'ᴛɪᴘs​', 'tips')
                ]
            )

    btn.insert(0, [
        InlineKeyboardButton("⚡ ʜᴏᴡ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ⚡", url=f"{HOW_TO_DOWNLOAD}")
    ])

    if offset != "":
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        try:
            settings = await get_settings(message.chat.id)
            if settings['max_btn']:
                btn.append(
                    [InlineKeyboardButton("ᴘᴀɢᴇ​", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results) / MAX_BTN)}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ​ ≫",callback_data=f"next_{req}_{key}_{offset}")]
                )
            else:
                btn.append(
                    [InlineKeyboardButton("ᴘᴀɢᴇ​", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ​ ≫",callback_data=f"next_{req}_{key}_{offset}")]
                )
        except KeyError:
            await save_group_settings(message.chat.id, 'max_btn', False)
            settings = await get_settings(message.chat.id)
            if settings['max_btn']:
                btn.append(
                    [InlineKeyboardButton("ᴘᴀɢᴇ​", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results) / MAX_BTN)}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ​ ≫",callback_data=f"next_{req}_{key}_{offset}")]
                )
            else:
                btn.append(
                    [InlineKeyboardButton("ᴘᴀɢᴇ​", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ​ ≫",callback_data=f"next_{req}_{key}_{offset}")]
                )
    else:
        btn.append(
            [InlineKeyboardButton(text="🔋 ɴᴏ ᴍᴏʀᴇ ᴘᴀɢᴇs​ 🔋",callback_data="pages")]
        )
    imdb = await get_poster(search, file=(files[0]).file_name) if settings["imdb"] else None
    TEMPLATE = settings['template']
    if imdb:
        cap = TEMPLATE.format(
            query=search,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            **locals()
        )
    else:
        cap = f"<b>📟 ᴛɪᴛʟᴇ : {search} \n📂ᴛᴏᴛᴀʟ ꜰɪʟᴇs ꜰᴏᴜɴᴅᴇᴅ : {str(total_results)}\n\n👩🏻‍💻 ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ : {message.from_user.mention} \n\n\n⚠️ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇᴅ ᴀғᴛᴇʀ 𝟷𝟶 ᴍɪɴᴜᴛᴇs.</b>"
    if imdb and imdb.get('poster'):
        try:
            hehe =  await message.reply_photo(photo=imdb.get('poster'), caption=cap[:1024],
                                      reply_markup=InlineKeyboardMarkup(btn))
            if SELF_DELETE:
                await asyncio.sleep(SELF_DELETE_SECONDS)
                await hehe.delete()

        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            hmm = await message.reply_photo(photo=poster, caption=cap[:1024], reply_markup=InlineKeyboardMarkup(btn))
            if SELF_DELETE:
                await asyncio.sleep(SELF_DELETE_SECONDS)
                await hmm.delete()
        except Exception as e:
            logger.exception(e)
            fek = await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
            if SELF_DELETE:
                await asyncio.sleep(SELF_DELETE_SECONDS)
                await fek.delete()
    else:
        fuk = await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
        if SELF_DELETE:
            await asyncio.sleep(SELF_DELETE_SECONDS)
            await fuk.delete()


async def advantage_spell_chok(client, msg):
    mv_id = msg.id
    mv_rqst = msg.text
    reqstr1 = msg.from_user.id if msg.from_user else 0
    reqstr = await client.get_users(reqstr1)
    settings = await get_settings(msg.chat.id)
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", msg.text, flags=re.IGNORECASE)  # plis contribute some common words
    query = query.strip() + " movie"
    try:
        movies = await get_poster(mv_rqst, bulk=True)
    except Exception as e:
        logger.exception(e)
        reqst_gle = mv_rqst.replace(" ", "+")
        button = [[
                   InlineKeyboardButton("Gᴏᴏɢʟᴇ", url=f"https://www.google.com/search?q={reqst_gle}")
        ]]
        if NO_RESULTS_MSG:
            await client.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, mv_rqst)))
        k = await msg.reply_photo(
            photo=SPELL_IMG, 
            caption=script.I_CUDNT.format(mv_rqst),
            reply_markup=InlineKeyboardMarkup(button),
 essage_id=msg.id
        )
        await asyncio.sleep(30)
        await k.delete()
        return
    movielist = []
    if not movies:
        reqst_gle = mv_rqst.replace(" ", "+")
        button = [[
                   InlineKeyboardButton("Gᴏᴏɢʟᴇ", url=f"https://www.google.com/search?q={reqst_gle}")
        ]]
        if NO_RESULTS_MSG:
            await client.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, mv_rqst)))
        k = await msg.reply_photo(
            photo=SPELL_IMG, 
            caption=script.I_CUDNT.format(mv_rqst),
            reply_markup=InlineKeyboardMarkup(button),
            reply_to_message_id=msg.id
        )
        await asyncio.sleep(30)
        await k.delete()
        return
    movielist += [movie.get('title') for movie in movies]
    movielist += [f"{movie.get('title')} {movie.get('year')}" for movie in movies]
    SPELL_CHECK[mv_id] = movielist
    btn = [
        [
            InlineKeyboardButton(
                text=movie_name.strip(),
                callback_data=f"spol#{reqstr1}#{k}",
            )
        ]
        for k, movie_name in enumerate(movielist)
    ]
    btn.append([InlineKeyboardButton(text="Close", callback_data=f'spol#{reqstr1}#close_spellcheck')])
    spell_check_del = await msg.reply_photo(
        photo=(SPELL_IMG),
        caption=(script.CUDNT_FND.format(mv_rqst)),
        reply_markup=InlineKeyboardMarkup(btn),
        reply_to_message_id=msg.id
    )
    try:
        if settings['auto_delete']:
            await asyncio.sleep(600)
            await spell_check_del.delete()
    except KeyError:
            grpid = await active_connection(str(message.from_user.id))
            await save_group_settings(grpid, 'auto_delete', True)
            settings = await get_settings(message.chat.id)
            if settings['auto_delete']:
                await asyncio.sleep(600)
                await spell_check_del.delete()


async def manual_filters(client, message, text=False):
    settings = await get_settings(message.chat.id)
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            joelkb = await client.send_message(
                                group_id, 
                                reply_text, 
                                disable_web_page_preview=True,
                                protect_content=True if settings["file_secure"] else False,
                                reply_to_message_id=reply_id
                            )
                            try:
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                            try:
                                if settings['auto_delete']:
                                    await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_delete', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_delete']:
                                    await joelkb.delete()

                        else:
                            button = eval(btn)
                            hmm = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                protect_content=True if settings["file_secure"] else False,
                                reply_to_message_id=reply_id
                            )
                            try:
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                            try:
                                if settings['auto_delete']:
                                    await hmm.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_delete', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_delete']:
                                    await hmm.delete()

                    elif btn == "[]":
                        oto = await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            protect_content=True if settings["file_secure"] else False,
                            reply_to_message_id=reply_id
                        )
                        try:
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, 'auto_ffilter', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)
                        try:
                            if settings['auto_delete']:
                                await oto.delete()
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, 'auto_delete', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_delete']:
                                await oto.delete()

                    else:
                        button = eval(btn)
                        dlt = await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                        try:
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, 'auto_ffilter', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)
                        try:
                            if settings['auto_delete']:
                                await dlt.delete()
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, 'auto_delete', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_delete']:
                                await dlt.delete()

                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False

async def global_filters(client, message, text=False):
    settings = await get_settings(message.chat.id)
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_gfilters('gfilters')
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_gfilter('gfilters', keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            joelkb = await client.send_message(
                                group_id, 
                                reply_text, 
                                disable_web_page_preview=True,
                                reply_to_message_id=reply_id
                            )
                            
                        else:
                            button = eval(btn)
                            hmm = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id=reply_id
                            )

                    elif btn == "[]":
                        oto = await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id=reply_id
                        )

                    else:
                        button = eval(btn)
                        dlt = await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )

                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False
