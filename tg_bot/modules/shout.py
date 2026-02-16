from tg_bot import application, spamcheck
from telegram import Update
from telegram.ext import CallbackContext
from .helper_funcs.decorators import kigcmd

@kigcmd(command='shout')
@spamcheck
async def shout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
    except IndexError:
        return await update.effective_message.reply_text("What do you want me to shout?", parse_mode="MARKDOWN")
    text = " ".join(args)
    result = [" ".join(list(text))]
    for pos, symbol in enumerate(text[1:]):
        result.append(symbol + " " + "  " * pos + symbol)
    result = list("\n".join(result))
    result[0] = text[0]
    result = "".join(result)
    msg = "```\n" + result + "```"
    return await update.effective_message.reply_text(msg, parse_mode="MARKDOWN")
