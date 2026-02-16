import logging
import os
import sys
import time
from typing import List
import telegram.ext as tg
from telegram.ext import Dispatcher, JobQueue, Updater
from configparser import ConfigParser
from functools import wraps
from dataclasses import dataclass
try:
    os.system(os.environ['convert_config'])
    from .config import config_vars
except (ModuleNotFoundError, KeyError):
    config_vars = None
StartTime = time.time()

def get_user_list(key):
    # Import here to evade a circular import
    from tg_bot.modules.sql import nation_sql
    royals = nation_sql.get_royals(key)
    return [a.user_id for a in royals]

# setup loggers


file_formatter = logging.Formatter('%(asctime)s - %(levelname)s -- < - %(name)s - > -- %(message)s')
stream_formatter = logging.Formatter('< - %(name)s - > -- %(message)s')

file_handler = logging.FileHandler('logs.txt', 'w', encoding='utf-8')
debug_handler = logging.FileHandler('debug.log', 'w', encoding='utf-8')
stream_handler = logging.StreamHandler()

file_handler.setFormatter(file_formatter)
stream_handler.setFormatter(stream_formatter)
debug_handler.setFormatter(file_formatter)

file_handler.setLevel(logging.INFO)
stream_handler.setLevel(logging.WARNING)
debug_handler.setLevel(logging.DEBUG)

logging.basicConfig(handlers = [file_handler, stream_handler, debug_handler], level = logging.DEBUG)
log = logging.getLogger('[Enterprise]')

log.info("LOGGER is starting. | Project maintained by: github.com/itsLuuke (t.me/itsLuuke)")

# if version < 3.10, stop bot.
if sys.version_info[0] < 3 or sys.version_info[1] < 10:
    log.error(
        "You MUST have a python version of at least 3.10! Multiple features depend on this. Bot quitting."
    )
    quit(1)

from collections import ChainMap

class ConfigParser(ConfigParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _unify_values(self, section, vars):
        if not config_vars:
            return super()._unify_values(section, vars)
        log.debug("Using the supplied config vars!")
        var_dict = {
            self.optionxform(
                    key.split(str(section).upper() + "__")[1].lower()
            ): value
            for key, value in config_vars.items()
            if value is not None
            and str(key).startswith(str(section).upper() + "__")
        }
        return ChainMap(var_dict, {}, self._defaults)


parser = ConfigParser()
parser.read("config.ini")
kigconfig = parser["kigconfig"]

@dataclass
class KigyoINIT:
    def __init__(self, parser: ConfigParser):
        self.parser = parser
        self.SYS_ADMIN: int = self.parser.getint('SYS_ADMIN', '0')
        self.OWNER_ID: int = self.parser.getint('OWNER_ID', '0')
        self.OWNER_USERNAME: str = self.parser.get('OWNER_USERNAME', "0")
        self.WEBHOOK: bool = self.parser.getboolean('WEBHOOK', False)
        self.URL: str = self.parser.get('URL', None)
        self.CERT_PATH: str = self.parser.get('CERT_PATH', None)
        self.PORT: int = self.parser.getint('PORT', None)
        self.INFOPIC: bool = self.parser.getboolean('INFOPIC', False)
        self.DEL_CMDS: bool = self.parser.getboolean("DEL_CMDS", False)
        self.ALLOW_EXCL: bool = self.parser.getboolean("ALLOW_EXCL", False)
        self.CUSTOM_CMD: List[str] = ['/', '!', ">"]
        self.BAN_STICKER: str = self.parser.get("BAN_STICKER", None)
        self.TOKEN: str = self.parser.get("TOKEN")
        self.DB_URI: str = self.parser.get("SQLALCHEMY_DATABASE_URI")
        self.LOAD = self.parser.get("LOAD", "").split()
        self.LOAD: List[str] = list(map(str, self.LOAD))
        self.MESSAGE_DUMP: int = self.parser.getint('MESSAGE_DUMP', None)
        self.BOT_LOGS: int = self.parser.getint('BOT_LOGS', None)
        self.NO_LOAD = self.parser.get("NO_LOAD", "").split()
        self.NO_LOAD: List[str] = list(map(str, self.NO_LOAD))
        self.CASH_API_KEY: str = self.parser.get('CASH_API_KEY', None)
        self.TIME_API_KEY: str = self.parser.get('TIME_API_KEY', None)
        self.WALL_API: str = self.parser.get('WALL_API', None)
        self.LASTFM_API_KEY: str = self.parser.get('LASTFM_API_KEY', None)
        self.WEATHER_API: str = self.parser.get('WEATHER_API', None)
        self.CF_API_KEY: str =  self.parser.get("CF_API_KEY", None)
        self.bot_id = 0 #placeholder
        self.bot_name = " Ōɖìղ" #placeholder
        self.bot_username = "OdinRobot" #placeholder
        self.DEBUG: bool = self.parser.getboolean("IS_DEBUG", False)
        self.DROP_UPDATES: bool = self.parser.getboolean("DROP_UPDATES", True)
        self.BOT_API_URL: str = self.parser.get('BOT_API_URL', "https://api.telegram.org/bot")
        self.BOT_API_FILE_URL: str = self.parser.get('BOT_API_FILE_URL', "https://api.telegram.org/file/bot")

        self.ALLOW_CHATS =  self.parser.getboolean("ALLOW_CHATS", True)
        self.SUPPORT_GROUP =  self.parser.get("SUPPORT_GROUP", 0)
        self.IS_DEBUG =  self.parser.getboolean("IS_DEBUG", False)
        self.GROUP_BLACKLIST =  self.parser.get("GROUP_BLACKLIST", [])
        self.GLOBALANNOUNCE =  self.parser.getboolean("GLOBALANNOUNCE", False)
        self.BACKUP_PASS =  self.parser.get("BACKUP_PASS", None)


KInit = KigyoINIT(parser=kigconfig)

OWNER_ID = KInit.OWNER_ID
OWNER_USERNAME = KInit.OWNER_USERNAME
APP_ID = KInit.APP_ID
WEBHOOK = KInit.WEBHOOK
URL = KInit.URL
CERT_PATH = KInit.CERT_PATH
PORT = KInit.PORT
INFOPIC = KInit.INFOPIC
DEL_CMDS = KInit.DEL_CMDS
ALLOW_EXCL = KInit.ALLOW_EXCL
CUSTOM_CMD = KInit.CUSTOM_CMD
BAN_STICKER = KInit.BAN_STICKER
TOKEN = KInit.TOKEN
DB_URI = KInit.DB_URI
LOAD = KInit.LOAD
MESSAGE_DUMP = KInit.MESSAGE_DUMP
BOT_LOGS = KInit.BOT_LOGS
NO_LOAD = KInit.NO_LOAD
OWNER_USER = [OWNER_ID]
SYS_ADMIN = KInit.SYS_ADMIN
MOD_USERS = [OWNER_ID] + [SYS_ADMIN] + get_user_list("mods")
SUDO_USERS = [OWNER_ID] + [SYS_ADMIN] + get_user_list("sudos")
DEV_USERS = [OWNER_ID] + [SYS_ADMIN] + get_user_list("devs")
SUPPORT_USERS = get_user_list("supports")
WHITELIST_USERS = get_user_list("whitelists")
SPAMMERS = get_user_list("spammers")
CASH_API_KEY = KInit.CASH_API_KEY
TIME_API_KEY = KInit.TIME_API_KEY
# WALL_API = KInit.WALL_API
LASTFM_API_KEY = KInit.LASTFM_API_KEY
WEATHER_API = KInit.WEATHER_API
CF_API_KEY = KInit.CF_API_KEY
ALLOW_CHATS = KInit.ALLOW_CHATS
SUPPORT_GROUP = KInit.SUPPORT_GROUP
IS_DEBUG = KInit.IS_DEBUG
GROUP_BLACKLIST = KInit.GROUP_BLACKLIST
bot_username = KInit.bot_username
GLOBALANNOUNCE = KInit.GLOBALANNOUNCE
BACKUP_PASS = KInit.BACKUP_PASS
BOT_ID = TOKEN.split(":")[0]


if IS_DEBUG:
    log.debug("Debug mode is on")
    stream_handler.setLevel(logging.DEBUG)


try:
    IS_DEBUG = IS_DEBUG
except AttributeError:
    IS_DEBUG = False

from tg_bot.modules.sql import SESSION

updater: Updater = tg.Updater(token=TOKEN, base_url=KInit.BOT_API_URL, base_file_url=KInit.BOT_API_FILE_URL, workers=min(32, os.cpu_count() + 4), request_kwargs={"read_timeout": 10, "connect_timeout": 10})

dispatcher: Dispatcher = updater.dispatcher
j: JobQueue = updater.job_queue



# Load at end to ensure all prev variables have been set
from tg_bot.modules.helper_funcs.handlers import CustomCommandHandler

if CUSTOM_CMD and len(CUSTOM_CMD) >= 1:
    tg.CommandHandler = CustomCommandHandler


'''def spamfilters(text, user_id, chat_id):
    # print("{} | {} | {}".format(text, user_id, chat_id))
    if int(user_id) not in SPAMMERS:
        return False

    print("This user is a spammer!")
    return True'''


def spamcheck(func):
    @wraps(func)
    def check_user(update, context, *args, **kwargs):
        try:
            chat = update.effective_chat
            user = update.effective_message.sender_chat or update.effective_user
            message = update.effective_message
        except AttributeError:
            return
        if IS_DEBUG:
            print("{} | {} | {} | {}".format(message.text or message.caption, user.id, message.chat.title, chat.id))
        # If msg from self, return True
        if user.id == context.bot.id:
            return False
        elif user.id == "777000":
            return False
        elif int(user.id) in SPAMMERS:
            return False
        elif str(chat.id) in GROUP_BLACKLIST:
            dispatcher.bot.sendMessage(chat.id, "This group is blacklisted, I'm outa here...")
            dispatcher.bot.leaveChat(chat.id)
            return False
        return func(update, context, *args, **kwargs)
    return check_user


