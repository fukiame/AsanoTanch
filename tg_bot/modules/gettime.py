import datetime
from typing import List
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import requests
from tg_bot import dispatcher, spamcheck
from telegram import ParseMode, Update
from telegram.ext import CallbackContext
from .helper_funcs.decorators import kigcmd


def is_valid_timezone(tz: str) -> bool:
    try:
        ZoneInfo(tz)
        return True
    except ZoneInfoNotFoundError:
        return False


def find_tz(to_find: str) -> str:
    from geopy.geocoders import Nominatim
    nom = Nominatim(user_agent="tgbot_gettime")
    try:
        loc = nom.geocode(to_find)
    except:
        return None

    from timezonefinder import TimezoneFinder
    tzf = TimezoneFinder()
    timezone = tzf.timezone_at(lng=loc.longitude, lat=loc.latitude)

    #return (loc.address, timezone)
    return timezone


def generate_time(to_find: str) -> str:
    if not is_valid_timezone(to_find):
        tz = find_tz(to_find)
        if not is_valid_timezone(tz):
            return None
    else:
        tz=to_find

    #daylight_saving = "Yes" if zone["dst"] == 1 else "No"
    date_fmt = r"%d-%m-%Y"
    time_fmt = r"%H:%M:%S"
    day_fmt = r"%A"
    timestamp = datetime.datetime.now(ZoneInfo(tz))
    current_date = timestamp.strftime(date_fmt)
    current_time = timestamp.strftime(time_fmt)
    current_day = timestamp.strftime(day_fmt)

    try:
        result = (
            f"<b>Zone Name:</b> <code>{tz}</code>\n"
            f"<b>Day:</b> <code>{current_day}</code>\n"
            f"<b>Current Time:</b> <code>{current_time}</code>\n"
            f"<b>Current Date:</b> <code>{current_date}</code>\n"
            '<b>Timezones:</b> <a href="https://en.wikipedia.org/wiki/List_of_tz_database_time_zones">List here</a>'
        )
    except:
        result = None

    return result

@kigcmd(command='time')
@spamcheck
def gettime(update: Update, context: CallbackContext):
    message = update.effective_message

    try:
        query = message.text.strip().split(" ", 1)[1]
    except:
        message.reply_text("Provide a country name/abbreviation/timezone to find.")
        return
    send_message = message.reply_text(
        f"Checking timezone info for <b>{query}</b>", parse_mode=ParseMode.HTML
    )

    result = generate_time(query)

    if not result:
        send_message.edit_text(
            f"Timezone info not available for <b>{query}</b>\n"
            '<b>All Timezones:</b> <a href="https://en.wikipedia.org/wiki/List_of_tz_database_time_zones">List here</a>',
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
        return

    send_message.edit_text(
        result, parse_mode=ParseMode.HTML, disable_web_page_preview=True
    )

__mod_name__ = "Time"
