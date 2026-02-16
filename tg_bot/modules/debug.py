import datetime
import os

from telegram import Update
from telegram.ext import CallbackContext

from .. import BACKUP_PASS, CASH_API_KEY, CF_API_KEY, DB_URI, LASTFM_API_KEY, TIME_API_KEY, TOKEN, application
from .helper_funcs.chat_status import dev_plus
from .helper_funcs.decorators import kigcmd, register

DEBUG_MODE = False

@kigcmd(command='debug')
@dev_plus
async def debug(update: Update, _: ContextTypes.DEFAULT_TYPE):
    global DEBUG_MODE
    args = await update.effective_message.text.split(None, 1)
    message = update.effective_message
    print(DEBUG_MODE)
    if len(args) > 1:
        if args[1] in ("yes", "on"):
            DEBUG_MODE = True
            await message.reply_text("Debug mode is now on.")
        elif args[1] in ("no", "off"):
            DEBUG_MODE = False
            await message.reply_text("Debug mode is now off.")
    elif DEBUG_MODE:
        await message.reply_text("Debug mode is currently on.")
    else:
        await message.reply_text("Debug mode is currently off.")

@kigcmd(command='gannounce')
@dev_plus
async def asdebug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GLOBALANNOUNCE
    args = await update.effective_message.text.split(None, 1)
    message = update.effective_message
    print(GLOBALANNOUNCE)
    if len(args) > 1:
        if args[1] in ("yes", "on"):
            GLOBALANNOUNCE = True
            await message.reply_text("Global announcement is now on.")
        elif args[1] in ("no", "off"):
            GLOBALANNOUNCE = False
            await message.reply_text("Global announcement is now off.")
    elif GLOBALANNOUNCE:
        await message.reply_text("Global announcement is currently on.")
    else:
        await message.reply_text("Global announcement is currently off.")

@register(pattern='.*')
async def i_do_nothing_yes(event):
    global DEBUG_MODE
    if DEBUG_MODE:
        print(f"-{event.from_id} ({event.chat_id}) : {event.text}")
        if os.path.exists("updates.txt"):
            with open("updates.txt", "r") as f:
                text = f.read()
            with open("updates.txt", "w+") as f:
                f.write(text + f"\n-{event.from_id} ({event.chat_id}) : {event.text}")
        else:
            with open("updates.txt", "w+") as f:
                f.write(
                    f"- {event.from_id} ({event.chat_id}) : {event.text} | {datetime.datetime.now()}"
                )


@kigcmd(command='logs')
@dev_plus
async def logs(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not os.path.exists('logs.txt'):
        await update.effective_message.reply_text("File doesn't exist")
        return

    user = update.effective_user

    logsname = "{}_logs.txt".format(application.bot.username)

    # https://pythonexamples.org/python-replace-string-in-file/
    logstxt = open("logs.txt", "rt")
    with open(logsname, "wt") as logsout:
        for line in logstxt:
            logsout.write(line.replace(str(DB_URI), '$DATABASE').replace(str(TOKEN), '$TOKEN').replace(str(CASH_API_KEY), '$CASH_API_KEY').replace(str(TIME_API_KEY), '$TIME_API_KEY').replace(str(LASTFM_API_KEY), '$LASTFM_API_KEY').replace(str(CF_API_KEY), '$CF_API_KEY').replace(str(BACKUP_PASS), '$BACKUP_PASS'))
        logstxt.close()

    with open(logsname, "rb") as f:
        await context.bot.send_document(document=f, filename=f.name, chat_id=user.id)


@kigcmd(command='updates')
@dev_plus
async def updates_log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not os.path.exists('updates.txt'):
        await update.effective_message.reply_text("File doesn't exist")
        return
    updatesname = "{}_updates.txt".format(application.bot.username)

    # https://pythonexamples.org/python-replace-string-in-file/
    updatestxt = open("updates.txt", "rt")
    with open(updatesname, "wt") as updatesout:
        for line in updatestxt:
            updatesout.write(line.replace(str(DB_URI), '$DATABASE').replace(str(TOKEN), '$TOKEN').replace(str(CASH_API_KEY), '$CASH_API_KEY').replace(str(TIME_API_KEY), '$TIME_API_KEY').replace(str(LASTFM_API_KEY), '$LASTFM_API_KEY').replace(str(CF_API_KEY), '$CF_API_KEY').replace(str(BACKUP_PASS), '$BACKUP_PASS'))
        updatestxt.close()

    with open(updatesname, "rb") as f:

        await context.bot.send_document(document=f, filename=f.name, chat_id=user.id)


__mod_name__ = "Debug"
