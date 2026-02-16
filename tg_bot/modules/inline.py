import html
import json
from datetime import datetime
from platform import python_version
from typing import List
from uuid import uuid4

import requests
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, Update, InlineKeyboardMarkup, \
    InlineKeyboardButton
from telegram import __version__
from telegram.error import BadRequest
from telegram.ext import CallbackContext
from telegram.utils.helpers import escape_markdown, mention_html

import tg_bot.modules.sql.users_sql as sql
from tg_bot import (
    MOD_USERS,
    OWNER_ID,
    SUDO_USERS,
    SUPPORT_USERS,
    DEV_USERS,
    WHITELIST_USERS,
    SYS_ADMIN,
    log
)
from .helper_funcs.misc import article
from .helper_funcs.decorators import kiginline
from tg_bot.__main__ import USER_INFO

def remove_prefix(text, prefix):
    if text.startswith(prefix):
        text = text.replace(prefix, "", 1)
    return text

@kiginline()
async def inlinequery(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Main InlineQueryHandler callback.
    """
    query = update.inline_query.query
    user = update.effective_user

    results: List = []
    inline_help_dicts = [
        {
            "title": " “info” Account info on Ōɖìղ • オーディン",
            "description": "Look up a Telegram account in Ōɖìղ • オーディン database",
            "message_text": "Click the button below to look up a person in Ōɖìղ • オーディン database using their Telegram ID",
            "thumb_urL": "https://telegra.ph/file/c741074ba2291655a8546.jpg",
            "keyboard": "info ",
        },
        {
            "title": " “about” About",
            "description": "Know about Ōɖìղ • オーディン",
            "message_text": "Click the button below to get to know about Ōɖìղ • オーディン.",
            "thumb_urL": "https://telegra.ph/file/c741074ba2291655a8546.jpg",
            "keyboard": "about ",
        },
    ]

    inline_funcs = {
        "info": inlineinfo,
        "about": about,
    }

    if (f := await query.split(" ", 1)[0]) in inline_funcs:
        inline_funcs[f](remove_prefix(query, f).strip(), update, user)
    else:
        for ihelp in inline_help_dicts:
            results.append(
                article(
                    title=ihelp["title"],
                    description=ihelp["description"],
                    message_text=ihelp["message_text"],
                    thumb_url=ihelp["thumb_urL"],
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="Click Here",
                                    switch_inline_query_current_chat=ihelp[
                                        "keyboard"
                                    ],
                                )
                            ]
                        ]
                    ),
                )
            )

        await update.inline_query.answer(results, cache_time=5)


def inlineinfo(query: str, update: Update, context: CallbackContext) -> None:
    """Handle the inline query."""
    bot = context.bot
    query = update.inline_query.query
    log.info(query)
    user_id = update.effective_user.id

    try:
        search = await query.split(" ", 1)[1]
    except IndexError:
        search = user_id

    try:
        user = await bot.get_chat(int(search))
    except (BadRequest, ValueError):
        user = await bot.get_chat(user_id)

    chat = update.effective_chat
    sql.update_user(user.id, user.username)

    text = (
        f"<b>User Info:</b>\n"
        f"ㅤ<b>First Name:</b> {mention_html(user.id, user.first_name)}"
    )
    if user.last_name:
        text += f"\nㅤ<b>Last Name:</b> {html.escape(user.last_name)}"
    if user.username:
        text += f"\nㅤ<b>Username:</b> @{html.escape(user.username)}"
    text += f"\nㅤ<b>User ID:</b> <code>{user.id}</code>"

    if user.id not in [777000, 1087968824, OWNER_ID, SYS_ADMIN, bot.id]:
        num_chats = sql.get_user_num_chats(user.id)
        text += f"\nㅤ<b>Chats:</b> <code>{num_chats}</code>"

    if user.id == OWNER_ID:
        text += "\nㅤ<b>User status:</b> <a href='https://t.me/{}?start=nations'>Owner</a>".format(escape_markdown(bot.username))
    elif user.id == SYS_ADMIN:
        text += ""
    elif user.id in DEV_USERS:
        text += "\nㅤ<b>User status:</b> <a href='https://t.me/{}?start=nations'>Developer</a>".format(escape_markdown(bot.username))
    elif user.id in SUDO_USERS:
        text += "\nㅤ<b>User status:</b> <a href='https://t.me/{}?start=nations'>Sudo</a>".format(escape_markdown(bot.username))
    elif user.id in SUPPORT_USERS:
        text += "\nㅤ<b>User status:</b> <a href='https://t.me/{}?start=nations'>Support</a>".format(escape_markdown(bot.username))
    elif user.id in MOD_USERS:
        text += "\nㅤ<b>User status:</b> <a href='https://t.me/{}?start=nations'>Moderator</a>".format(escape_markdown(bot.username))
    elif user.id in WHITELIST_USERS:
        text += "\nㅤ<b>User status:</b> <a href='https://t.me/{}?start=nations'>Whitelist</a>".format(escape_markdown(bot.username))

    text += "\n"
    try:
        from .blacklistusers import __user_info__ as bl
        user_info = bl(user.id)
        text += user_info
    except:
        pass


    kb = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="Report Error", url='https://t.me/TheBotsSupport'
                ),
                InlineKeyboardButton(
                    text="Search again",
                    switch_inline_query_current_chat="info ",
                ),
            ]
        ]
    )


    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title=f"User info of {html.escape(user.first_name)}",
            input_message_content=InputTextMessageContent(text, parse_mode=ParseMode.HTML,
                                                          disable_web_page_preview=True),
            thumb_url="https://telegra.ph/file/c741074ba2291655a8546.jpg",
            reply_markup=kb
        ),
    ]

    await update.inline_query.answer(results, cache_time=5)


def about(query: str, update: Update, context: CallbackContext) -> None:
    """Handle the inline query."""
    query = update.inline_query.query
    user_id = update.effective_user.id
    user = await context.bot.get_chat(user_id)
    sql.update_user(user.id, user.username)
    about_text = f"""
    Ōɖìղ • オーディン (@{context.bot.username})
    Maintained by [ルーク](t.me/itsLuuke)
    Built with ❤️ using python-telegram-bot v{str(__version__)}
    Running on Python {python_version()}
    """
    results: list = []
    kb = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="Support",
                    url=f"https://t.me/TheBotsSupport",
                ),
                InlineKeyboardButton(
                    text="Channel",
                    url=f"https://t.me/LukeBots",
                ),
                InlineKeyboardButton(
                    text="Maintainer",
                    url=f"https://t.me/itsLuuke",
                ),

            ],
            [
                InlineKeyboardButton(
                    text="GitLab",
                    url=f"https://www.gitlab.com/OdinRobot/OdinRobot",
                ),
                InlineKeyboardButton(
                    text="GitHub",
                    url="https://www.github.com/OdinRobot/OdinRobot",
                ),
            ],
        ])

    results.append(

        InlineQueryResultArticle
            (
            id=str(uuid4()),
            title=f"About Ōɖìղ • オーディン (@{context.bot.username})",
            input_message_content=InputTextMessageContent(about_text, parse_mode=ParseMode.MARKDOWN,
                                                          disable_web_page_preview=True),
            thumb_url="https://telegra.ph/file/c741074ba2291655a8546.jpg",
            reply_markup=kb
        )
    )
    await update.inline_query.answer(results)
