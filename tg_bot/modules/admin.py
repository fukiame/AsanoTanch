import html
import time

from telegram import ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext

from telegram.utils.helpers import mention_html

from tg_bot import spamcheck
from .helper_funcs.chat_status import connection_status

from .helper_funcs.extraction import extract_user, extract_user_and_text
from .log_channel import loggable
from .language import gs
from .helper_funcs.decorators import kigcmd, register

from .helper_funcs.admin_status import (
    user_admin_check,
    bot_admin_check,
    AdminPerms,
    get_bot_member,
    A_CACHE, B_CACHE
)

from typing import Optional


@kigcmd(command="fullpromote", can_disable=False)
@spamcheck
@connection_status
@bot_admin_check(AdminPerms.CAN_PROMOTE_MEMBERS)
@user_admin_check(AdminPerms.CAN_PROMOTE_MEMBERS)
@loggable
async def fullpromote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    user_id, title = extract_user_and_text(message, args)

    if not user_id:
        await message.reply_text(
            "You don't seem to be referring to a user or the ID specified is incorrect.."
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except Exception as e:
        await message.reply_text(f"Error: {e}")
        return

    if user_member.status in ("administrator", "creator"):
        await message.reply_text("This user is already an admin!")
        return

    if user_id == bot.id:
        await message.reply_text("Yeah, I wish I could promote myself...")
        return

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = get_bot_member(chat.id)

    try:
        await bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=bot_member.can_change_info,
            can_post_messages=bot_member.can_post_messages,
            can_edit_messages=bot_member.can_edit_messages,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            can_promote_members=bot_member.can_promote_members,
            can_restrict_members=bot_member.can_restrict_members,
            can_pin_messages=bot_member.can_pin_messages,
            can_manage_video_chats=bot_member.can_manage_video_chats,
            is_anonymous=bot_member.is_anonymous,
        )
        if title:
            await bot.setChatAdministratorCustomTitle(chat.id, user_id, title)
        await bot.sendMessage(
            chat.id,
            "<b>{}</b> was promoted{} with full perms."
                .format(user_member.user.first_name or user_id,
                        f" by <b>{message.from_user.first_name}</b>" if not message.sender_chat else ""),
            parse_mode=ParseMode.HTML
        )
    except BadRequest as err:
        if err.message == "User_not_mutual_contact":
            await message.reply_text("How am I mean to promote someone who isn't in the group?")
        else:
            await message.reply_text("An error occurred while promoting.")
        return

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#PROMOTED\n"
        f"Full promote\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
    )

    return log_message

@kigcmd(command="promote", can_disable=False)
@spamcheck
@connection_status
@bot_admin_check(AdminPerms.CAN_PROMOTE_MEMBERS)
@user_admin_check(AdminPerms.CAN_PROMOTE_MEMBERS)
@loggable
async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    user_id, title = extract_user_and_text(message, args)

    if not user_id:
        await message.reply_text(
            "You don't seem to be referring to a user or the ID specified is incorrect.."
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except Exception as e:
        await message.reply_text(f"Error: {e}")
        return

    if user_member.status in ("administrator", "creator"):
        await message.reply_text("This user is already an admin!")
        return

    if user_id == bot.id:
        await message.reply_text("Yeah I wish I could promote myself...")
        return

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = get_bot_member(chat.id)

    try:
        await bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=bot_member.can_change_info,
            can_post_messages=bot_member.can_post_messages,
            can_edit_messages=bot_member.can_edit_messages,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            can_restrict_members=bot_member.can_restrict_members,
            can_pin_messages=bot_member.can_pin_messages,
            can_manage_video_chats=bot_member.can_manage_video_chats,
        )
        if title:
            await bot.setChatAdministratorCustomTitle(chat.id, user_id, title)
        await bot.sendMessage(
            chat.id,
            "<b>{}</b> was promoted{}.".format(
                    user_member.user.first_name or user_id,
                    f' by <b>{message.from_user.first_name}</b>' if not message.sender_chat else ''
                ),
            parse_mode=ParseMode.HTML,
        )

    except BadRequest as err:
        if err.message == "User_not_mutual_contact":
            await message.reply_text("How am I mean to promote someone who isn't in the group?")
        else:
            await message.reply_text(f"An error occurred while promoting:\n{err.message}")
        return

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#PROMOTED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
    )

    return log_message


@kigcmd(command="demote", can_disable=False)
@spamcheck
@connection_status
@bot_admin_check(AdminPerms.CAN_PROMOTE_MEMBERS)
@user_admin_check(AdminPerms.CAN_PROMOTE_MEMBERS)
@loggable
async def demote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user

    user_id = extract_user(message, args)
    if not user_id:
        await message.reply_text(
            "You don't seem to be referring to a user or the ID specified is incorrect.."
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except Exception as e:
        await message.reply_text(f"Error: {e}")
        return

    if user_member.status == "creator":
        await message.reply_text("This person is the chat CREATOR, find someone else to play with.")
        return

    if user_member.status != "administrator":
        await message.reply_text("This user isn't an admin!")
        return

    if user_id == bot.id:
        await message.reply_text("I can't demote myself! Get an admin to do it for me.")
        return

    try:
        await bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            can_manage_video_chats=False,
            is_anonymous=False,
        )
        await bot.sendMessage(
            chat.id,
            "<b>{}</b> was demoted{}.".format(
                    user_member.user.first_name or user_id,
                    f' by <b>{message.from_user.first_name}</b>' if not message.sender_chat else ''
            ),
            parse_mode=ParseMode.HTML,
        )

        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#DEMOTED\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
        )

        return log_message

    except BadRequest as e:
        await message.reply_text(
            f"Could not demote!\n{str(e)}"
        )
        return

@kigcmd(command="title", can_disable=False)
@spamcheck
@connection_status
@bot_admin_check(AdminPerms.CAN_PROMOTE_MEMBERS)
@user_admin_check(AdminPerms.CAN_PROMOTE_MEMBERS)
@loggable
async def set_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user

    user_id, title = extract_user_and_text(message, args)

    if not user_id:
        user_id = user.id
        title = " ".join(args)

    try:
        user_member = chat.get_member(user_id)
    except:
        await message.reply_text(
            "You don't seem to be referring to a user or the ID specified is incorrect.."
        )
        return

    if user_member.status == "creator" and user_id == user.id:
        await message.reply_text(
            "Okay -_-"
        )
        return

    if user_member.status == "creator":
        await message.reply_text(
            "This person is the chat CREATOR, only they can set their title."
        )
        return

    if user_member.status != "administrator":
        await message.reply_text(
            "Titles can only be set to admins."
        )
        return

    if user_id == bot.id:
        await message.reply_text(
            "I can't set my own title myself! Get the one who made me admin to do it for me."
        )
        return

    if not title:
        await message.reply_text("You can't set an empty title!")
        return

    if len(title) > 16:
        await message.reply_text(
            "The title length is longer than 16 characters.\nTruncating it to 16 characters."
        )

    try:
        await bot.setChatAdministratorCustomTitle(chat.id, user_id, title)
    except BadRequest:
        await message.reply_text("I can only set titles for the admins I promote!")
        return

    await bot.sendMessage(
        chat.id,
        f"Successfully set title for <code>{user_member.user.first_name or user_id}</code> "
        f"to <code>{html.escape(title[:16])}</code>!",
        parse_mode=ParseMode.HTML,
    )

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#ADMIN\nTitle set\n"
        f"<b>By Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>To Admin:</b> {mention_html(user_member.user.id, user_member.user.first_name)}\n"
        f"<b>New Title:</b> '<code>{html.escape(title[:16])}</code>'"

    )
    return log_message


@kigcmd(command=["invitelink", "link"], can_disable=False)
@spamcheck
@bot_admin_check(AdminPerms.CAN_INVITE_USERS)
@user_admin_check(AdminPerms.CAN_INVITE_USERS, allow_mods = True)
@loggable
async def invite(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    bot = context.bot
    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user

    if chat.username:
        await update.effective_message.reply_text(f"https://t.me/{chat.username}")
    elif chat.type in [chat.SUPERGROUP, chat.CHANNEL]:
        bot_member = chat.get_member(bot.id)
        if bot_member.can_invite_users:
            invitelink = await bot.exportChatInviteLink(chat.id)
            await update.effective_message.reply_text(invitelink)

            log_message = (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#ADMIN\nInvite link exported\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"<b>Invite Link:</b> '<code>{invitelink}</code>'"

            )
            return log_message

        else:
            await update.effective_message.reply_text(
                "I don't have access to the invite link, try changing my permissions!"
            )
    else:
        await update.effective_message.reply_text(
            "I can only give you invite links for supergroups and channels, sorry!"
        )


@kigcmd(command=["admincache"], can_disable=False)
@spamcheck
async def admincache(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user
    try:
        last = _admincache[chat.id]
    except KeyError:
        last = None
    now = time.time()
    if last and last + 600 > now:
        return msg.reply_text("this command can only be used once every 10 minutes")

    if chat.type in ["channel", "private"]:
        return msg.reply_text("this command can only be used in groups")

    if chat.get_member(user.id).status not in ["administrator", "creator"] and user.id != 1087968824:
        return msg.reply_text("this command can only be used by admins")

    A_CACHE[update.effective_chat.id] = await update.effective_chat.get_administrators()
    B_CACHE[update.effective_chat.id] = await update.effective_chat.get_member(context.bot.id)
    msg.reply_text("Admin cache updated")
    _admincache[chat.id] = time.time()


_admincache = dict()


@kigcmd(command=["admin", "admins"])
@spamcheck
async def adminlist(update: Update, _: ContextTypes.DEFAULT_TYPE):
    administrators = A_CACHE[update.effective_chat.id]
    text = "Admins in *{}*:".format(update.effective_chat.title or "this chat")
    for admin in administrators:
        if not admin.is_anonymous:
            user = admin.user
            name = user.mention_markdown()
            text += "\n -> {} • `{}` • `{}` • `{}`".format(name, user.id, admin.status,
                                                           escape_markdown(
                                                               admin.custom_title) if admin.custom_title else "")

    await update.effective_message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


def get_help(chat):
    return gs(chat, "admin_help")


__mod_name__ = "Admin"

