# pip install fastapi
# pip install uvicorn[standard]
# uvicorn api:app --reload


from fastapi import FastAPI
import tg_bot.modules.sql.blacklistusers_sql as sql2
from telegram import __version__ as v

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "online", "ptb_ver": v }


@app.get("/getuser/{user_id}")
def read_item(user_id: int):
    try:
        b = sql2.is_user_blacklisted(user_id)
        if b:
            breason = sql2.get_reason(user_id)
        else:
            breason = None
        return {"status": "ok", "user_id": user_id, "blacklisted" : b, "blacklist_reason" : breason}
    except Exception:
        b = None
        breason = None
        return {"status": "ok", "user_id": user_id, "blacklisted" : b, "blacklist_reason" : breason}
