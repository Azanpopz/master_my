import re
from os import environ
from Script import script
from dotenv import load_dotenv
load_dotenv()


id_pattern = re.compile(r'^.\d+$')
def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

# Bot information
SESSION = environ.get('SESSION', 'Media_search')
API_ID = int(environ.get('API_ID', '10261086'))
API_HASH = environ.get('API_HASH', '9195dc0591fbdb22b5711bcd1f437dab')
BOT_TOKEN = environ.get('BOT_TOKEN', "5886125841:AAExUZBuaKFgiunozEKXXvNNfyvZKMoBkaM")

# Bot settings
CACHE_TIME = int(environ.get('CACHE_TIME', 300))
USE_CAPTION_FILTER = bool(environ.get('USE_CAPTION_FILTER', True))

PICS = (environ.get('PICS', 'https://graph.org/file/0b9151030fff5f35c4e11.jpg https://graph.org/file/630fd5fbc59fe83cefc34.jpg https://graph.org/file/5ed6c28c61ea6212e91f9.jpg https://graph.org/file/489c6b8058709c52ee31c.jpg https://graph.org/file/2c30c1452c2c4bccc3046.jpg https://graph.org/file/4f4c6bfc6a016b11ddef4.jpg https://graph.org/file/daf2b545d8b9b732b71d7.jpg https://graph.org/file/b711a112dc78f0bcc2cad.jpg https://graph.org/file/0858959a66bb00a29fd95.jpg https://graph.org/file/8ca62e6ad091a7cf4d86d.jpg https://graph.org/file/08ed0cd0bc6ac0bc37f49.jpg https://graph.org/file/4dc11ffde60a857316abe.jpg https://graph.org/file/3bce5258bede563a9c559.jpg https://graph.org/file/6cb914abbb21a755b601c.jpg https://graph.org/file/58a6861cf47953a596573.jpg https://graph.org/file/f7d482b08d48c2dc8a30a.jpg https://graph.org/file/a949483ebc4c3fe89bdc0.jpg https://graph.org/file/7b13e39550b56b82bd9f7.jpg https://graph.org/file/1cbe46cd74e11c704bbe2.jpg https://telegra.ph/file/e9c7a37f2522a1f4e494d.jpg')).split()
NOR_IMG = environ.get("NOR_IMG", "https://telegra.ph/file/75d4149a9a971c77508fc.jpg")
MELCOW_VID = environ.get("MELCOW_VID", "https://telegra.ph/file/f7f2a532fe4b990044507.mp4")
SPELL_IMG = environ.get("SPELL_IMG", "https://telegra.ph/file/17b82ea772e4bc357bbf5.jpg")

# Admins, Channels & Users
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '1426588906').split()]
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS', '-1001878854070').split()]
auth_users = [int(user) if id_pattern.search(user) else user for user in environ.get('AUTH_USERS', '').split()]
AUTH_USERS = (auth_users + ADMINS) if auth_users else []
auth_grp = environ.get('AUTH_GROUP')
AUTH_GROUPS = [int(ch) for ch in auth_grp.split()] if auth_grp else None
support_chat_id = environ.get('SUPPORT_CHAT_ID')
reqst_channel = environ.get('REQST_CHANNEL_ID')
REQST_CHANNEL = int(reqst_channel) if reqst_channel and id_pattern.search(reqst_channel) else None
SUPPORT_CHAT_ID = int(support_chat_id) if support_chat_id and id_pattern.search(support_chat_id) else None

#Downloader
DOWNLOAD_LOCATION = environ.get("DOWNLOAD_LOCATION", "./DOWNLOADS/AudioBoT/")

# This is required for the plugins involving the file system.
TMP_DOWNLOAD_DIRECTORY = environ.get("TMP_DOWNLOAD_DIRECTORY", "./DOWNLOADS/")

# Command
COMMAND_HAND_LER = environ.get("COMMAND_HAND_LER", "/")

# MongoDB information
DATABASE_URI = environ.get('DATABASE_URI', "mongodb+srv://koyeb1:koyeb1@cluster0.ig5ttb5.mongodb.net/?retryWrites=true&w=majority")
DATABASE_NAME = environ.get('DATABASE_NAME', "koyeb1")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'Telegram_files')

# FSUB
auth_channel = environ.get('AUTH_CHANNEL')
AUTH_CHANNEL = int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else None
# Set to False inside the bracket if you don't want to use Request Channel else set it to Channel ID
REQ_CHANNEL = environ.get("REQ_CHANNEL", False)
REQ_CHANNEL = int(REQ_CHANNEL) if REQ_CHANNEL and id_pattern.search(REQ_CHANNEL) else False
JOIN_REQS_DB = environ.get("JOIN_REQS_DB", DATABASE_URI)

#Auto approve 
CHAT_ID = [int(app_chat_id) if id_pattern.search(app_chat_id) else app_chat_id for app_chat_id in environ.get('CHAT_ID', '').split()]
TEXT = environ.get("APPROVED_WELCOME_TEXT", "<b>Dᴇᴀʀ {mention}\n\nYour Request To Jᴏɪɴ {title}  Was Approved 🔆</b>")
APPROVED = environ.get("APPROVED_WELCOME", "on").lower()

# Others
VERIFY = bool(environ.get('VERIFY', False))
SHORTLINK_URL = environ.get('SHORTLINK_URL', 'shorturllink.in')
SHORTLINK_API = environ.get('SHORTLINK_API', 'b4d510e7b1e56da54f43c9e27569ee0a281121db')
IS_SHORTLINK = bool(environ.get('IS_SHORTLINK', False))
NO_RESULTS_MSG = bool(environ.get('NO_RESULTS_MSG', False))
DELETE_CHANNELS = [int(dch) if id_pattern.search(dch) else dch for dch in environ.get('DELETE_CHANNELS', '0').split()]
MAX_B_TN = environ.get("MAX_B_TN", "7")
MAX_BTN = is_enabled((environ.get('MAX_BTN', "True")), True)
PORT = environ.get("PORT", "8080")
S_GROUP = environ.get('S_GROUP',"https://t.me/czdbotz_support")
RUL_LNK = environ.get('RUL_LNK',"https://graph.org/%F0%9D%97%A0%F0%9D%9E%93%F0%9D%97%A6%F0%9D%97%A7%F0%9D%9E%9D%F0%9D%97%A5-02-15")
MAIN_CHANNEL = environ.get('MAIN_CHANNEL',"https://t.me/czdbotz")
GRP_LNK = environ.get('GRP_LNK', 'https://t.me/czdbotz_support')
CHNL_LNK = environ.get('CHNL_LNK', 'https://t.me/czdbotz')
OWN_LNK = environ.get('S_GROUP',"https://t.me/AFxSU")
MVG_LNK = environ.get('S_GROUP',"https://t.me/at3movies")
MSG_ALRT = environ.get('MSG_ALRT', 'Piracy Is Crime')
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '-1001606248152'))
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', 'czdbotz_support')
P_TTI_SHOW_OFF = is_enabled((environ.get('P_TTI_SHOW_OFF', "True")), True)
IMDB = is_enabled((environ.get('IMDB', "True")), True)
AUTO_FFILTER = is_enabled((environ.get('AUTO_FFILTER', "True")), True)
AUTO_DELETE = is_enabled((environ.get('AUTO_DELETE', "True")), True)
SINGLE_BUTTON = is_enabled((environ.get('SINGLE_BUTTON', "True")), True)
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", f"{script.CAPTION}")
BATCH_FILE_CAPTION = environ.get("BATCH_FILE_CAPTION", None)
IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE", f"{script.IMDB_TEMPLATE_TXT}")
LONG_IMDB_DESCRIPTION = is_enabled(environ.get("LONG_IMDB_DESCRIPTION", "False"), False)
SPELL_CHECK_REPLY = is_enabled(environ.get("SPELL_CHECK_REPLY", "True"), True)
MAX_LIST_ELM = environ.get("MAX_LIST_ELM", None)
INDEX_REQ_CHANNEL = int(environ.get('INDEX_REQ_CHANNEL', LOG_CHANNEL))
FILE_STORE_CHANNEL = [int(ch) for ch in (environ.get('FILE_STORE_CHANNEL', '')).split()]
MELCOW_NEW_USERS = is_enabled((environ.get('MELCOW_NEW_USERS', "True")), True)
PROTECT_CONTENT = is_enabled((environ.get('PROTECT_CONTENT', "False")), False)
PUBLIC_FILE_STORE = is_enabled((environ.get('PUBLIC_FILE_STORE', "True")), True)

LANGUAGES = ["tamil", "english", "hindi", "telugu", "malayalam"]

LOG_STR = "Current Cusomized Configurations are:-\n"
LOG_STR += ("IMDB Results are enabled, Bot will be showing imdb details for you queries.\n" if IMDB else "IMBD Results are disabled.\n")
LOG_STR += ("P_TTI_SHOW_OFF found , Users will be redirected to send /start to Bot PM instead of sending file file directly\n" if P_TTI_SHOW_OFF else "P_TTI_SHOW_OFF is disabled files will be send in PM, instead of sending start.\n")
LOG_STR += ("SINGLE_BUTTON is Found, filename and files size will be shown in a single button instead of two separate buttons\n" if SINGLE_BUTTON else "SINGLE_BUTTON is disabled , filename and file_sixe will be shown as different buttons\n")
LOG_STR += (f"CUSTOM_FILE_CAPTION enabled with value {CUSTOM_FILE_CAPTION}, your files will be send along with this customized caption.\n" if CUSTOM_FILE_CAPTION else "No CUSTOM_FILE_CAPTION Found, Default captions of file will be used.\n")
LOG_STR += ("Long IMDB storyline enabled." if LONG_IMDB_DESCRIPTION else "LONG_IMDB_DESCRIPTION is disabled , Plot will be shorter.\n")
LOG_STR += ("Spell Check Mode Is Enabled, bot will be suggesting related movies if movie not found\n" if SPELL_CHECK_REPLY else "SPELL_CHECK_REPLY Mode disabled\n")
LOG_STR += (f"MAX_LIST_ELM Found, long list will be shortened to first {MAX_LIST_ELM} elements\n" if MAX_LIST_ELM else "Full List of casts and crew will be shown in imdb template, restrict them by adding a value to MAX_LIST_ELM\n")
LOG_STR += f"Your current IMDB template is {IMDB_TEMPLATE}"
