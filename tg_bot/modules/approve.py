import html

from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, Update, User
from telegram.error import BadRequest
from telegram.ext import CallbackContext, Filters
from telegram.utils.helpers import mention_html

import tg_bot.modules.sql.approve_sql as sql

from .helper_funcs.decorators import kigcmd, kigcallback
from .helper_funcs.extraction import extract_user
from .log_channel import loggable
from tg_bot import SUDO_USERS, spamcheck
from .helper_funcs.admin_status import (
    user_admin_check,
    AdminPerms,
)


def build_mention(user) -> str:
    return mention_html(user.user.id, user.user.first_name) if user.user \
        else f'<a href="t.me/{user.username}">{html.escape(user.title)}</a>'


@kigcmd(command='approve', filters=filters.ChatType.GROUPS)
@spamcheck
@user_admin_check(AdminPerms.CAN_CHANGE_INFO)
@loggable
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    bot = context.bot

    user_id = extract_user(message, args)
    if not user_id:
        await message.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!"
        )
        return ""
    member = None
    chan = None
    try:
        member = chat.get_member(user_id)
    except BadRequest:
        try:
            chan = await bot.get_chat(user_id)
        except BadRequest as excp:
            if excp.message != "Chat not found":
                raise
            await message.reply_text("Can't seem to find this person.")
            return ""
    if member and (member.status == "administrator" or member.status == "creator"):
        await message.reply_text(
            "User is already admin - locks, blocklists, and antiflood already don't apply to them."
        )
        return ""
    user_mention = build_mention(member or chan)
    if sql.is_approved(message.chat_id, user_id):
        await message.reply_text(
            f"{user_mention} is already approved in {html.escape(chat_title)}",
            parse_mode=ParseMode.HTML,
        )
        return ""
    sql.approve(message.chat_id, user_id)
    await message.reply_text(
        f"{user_mention} has been approved in {html.escape(chat_title)}! They "
        f"will now be ignored by automated admin actions like locks, blocklists, and antiflood.",
        parse_mode=ParseMode.HTML,
    )
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#APPROVED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {user_mention}")

    return log_message


@kigcmd(command='unapprove', filters=filters.ChatType.GROUPS)
@spamcheck
@user_admin_check(AdminPerms.CAN_CHANGE_INFO)
@loggable
async def disapprove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    bot = context.bot
    user_id = extract_user(message, args)

    member = None
    chan = None
    try:
        member = chat.get_member(user_id)
    except BadRequest:
        try:
            chan = await bot.get_chat(user_id)
        except BadRequest as excp:
            if excp.message != "Chat not found":
                raise
            await message.reply_text("Can't seem to find this person.")
            return ""
    if member and (member.status == "administrator" or member.status == "creator"):
        await message.reply_text(
            "User is already admin - locks, blocklists, and antiflood already don't apply to them."
        )
        return ""
    user_mention = build_mention(member or chan)
    if not sql.is_approved(message.chat_id, user_id):
        await message.reply_text(f"{user_mention} isn't approved yet!", parse_mode = ParseMode.HTML)
        return ""
    sql.disapprove(message.chat_id, user_id)
    await message.reply_text(
        f"{user_mention} is no longer approved in {chat_title}.", parse_mode = ParseMode.HTML)
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#UNAPPROVED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {user_mention}")

    return log_message


@kigcmd(command='approved', filters=filters.ChatType.GROUPS)
@spamcheck
@user_admin_check()
async def approved(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    bot = context.bot
    msg = "The following users are approved.\n"
    approved_users = sql.list_approved(message.chat_id)
    for i in approved_users:
        try:
            member = chat.get_member(int(i.user_id))
        except:
            member = await bot.get_chat(int(i.user_id))
        msg += f"- `{i.user_id}`: {member.user['first_name'] or member.title}\n"
    if msg.endswith("approved.\n"):
        await message.reply_text(f"No users are approved in {chat_title}.")
        return ""
    else:
        await message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


@kigcmd(command='approval', filters=filters.ChatType.GROUPS)
@spamcheck
@user_admin_check()
async def approval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message  # type: Optional[Message]
    chat = update.effective_chat
    args = context.args
    bot = context.bot
    user_id = extract_user(message, args)
    if not user_id:
        await message.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!"
        )
        return ""

    member = None
    chan = None
    try:
        member = chat.get_member(user_id)
    except BadRequest:
        try:
            chan = await bot.get_chat(user_id)
        except BadRequest as excp:
            if excp.message != "Chat not found":
                raise
            await message.reply_text("Can't seem to find this person.")
            return ""

    if member and member.status in ["administrator", "creator"]:
        await message.reply_text(
            "User is already admin - locks, blocklists, and antiflood already don't apply to them."
        )
        return ""
    user_mention = build_mention(member or chan)

    if sql.is_approved(message.chat_id, user_id):
        await message.reply_text(
            f"{user_mention} is an approved user. Locks, antiflood, and blocklists won't apply to them.",
                parse_mode = ParseMode.HTML
        )
    else:
        await message.reply_text(
            f"{user_mention} is not an approved user. They are affected by normal commands.",
                parse_mode = ParseMode.HTML
        )


@kigcmd(command='unapproveall', filters=filters.ChatType.GROUPS)
@spamcheck
async def unapproveall(update: Update, _: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    member = chat.get_member(user.id)
    if member.status != "creator" and user.id not in SUDO_USERS:
        await update.effective_message.reply_text(
            "Only the chat owner can unapprove all users at once.")
    else:
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text="Unapprove all users",
                    callback_data="unapproveall_user")
            ],
            [
                InlineKeyboardButton(
                    text="Cancel", callback_data="unapproveall_cancel")
            ],
        ])
        await update.effective_message.reply_text(
            f"Are you sure you would like to unapprove ALL users in {chat.title}? This action cannot be undone.",
            reply_markup=buttons,
            parse_mode=ParseMode.MARKDOWN,
        )


@kigcallback(pattern=r"unapproveall_.*")
async def unapproveall_btn(update: Update, _: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat = update.effective_chat
    message = update.effective_message
    member = chat.get_member(query.from_user.id)
    if query.data == "unapproveall_user":
        if member.status == "creator" or query.from_user.id in SUDO_USERS:
            approved_users = sql.list_approved(chat.id)
            users = [int(i.user_id) for i in approved_users]
            for user_id in users:
                sql.disapprove(chat.id, user_id)

        else:
            await query.answer("Only owner of the chat can do this.")

    elif query.data == "unapproveall_cancel":
        if member.status == "creator" or query.from_user.id in SUDO_USERS:
            await message.edit_text(
                "Removing of all approved users has been cancelled.")
            return ""
        else:
            await query.answer("Only owner of the chat can do this.")


from .language import gs


def get_help(chat):
    return gs(chat, "approve_help")


__mod_name__ = "Approvals"
