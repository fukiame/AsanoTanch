import requests
from tg_bot import spamcheck
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from .helper_funcs.decorators import kigcmd


cash_help_str = \
    "`/cash`, `/cc` : currency converter\
        example syntax: `/cash` 1 USD INR"

@kigcmd(command=['cash','cc'])
@spamcheck
def convert(update: Update, context: CallbackContext):
    args = update.effective_message.text.split(" ")

    if len(args) == 4:
        orig_cur = args[2].lower()
        new_cur = args[3].lower()

        if orig_cur == new_cur:
            update.effective_message.reply_text("old and new currency is the same")
            return

        incur = str(args[1]).strip().replace(',','.').lower()
        m = 1
        if len(incur) > 1:
            match incur[-1]:
                case 'k': m = 1000
                case 'm': m = 1000000
                case 'b': m = 1000000000

        if m != 1:
            s = incur[:-1]
        else: s = incur

        try:
            orig_cur_amount = float(s) * m

        except ValueError:
            update.effective_message.reply_text("Invalid Amount Of Currency")
            return

        request_url = (
            f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{orig_cur}.json"
        )
        try:
            rs = requests.get(request_url)
            response = rs.json()
        except:
            update.effective_message.reply_text(rs)
            return
        try:
            current_rate = float(
                response[orig_cur][new_cur]
            )
        except KeyError:
            update.effective_message.reply_text("Currency Not Supported.")
            return
        concur = orig_cur_amount * current_rate
        new_cur_amount = round(concur, 2 if concur > 1 else 5)
        update.effective_message.reply_text(
            f"{orig_cur_amount} {orig_cur.upper()} = {new_cur_amount} {new_cur.upper()}"
        )

    elif len(args) == 1:
        update.effective_message.reply_text(cash_help_str, parse_mode=ParseMode.MARKDOWN)

    else:
        update.effective_message.reply_text(
            f"*Invalid Args!!:* Required 3 But Passed {len(args) -1}",
            parse_mode=ParseMode.MARKDOWN,
        )
