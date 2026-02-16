import os
import subprocess

from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.filters import Filters


from telegram.update import Update

import datetime
from .. import DB_URI, OWNER_ID, SYS_ADMIN, application, log, BACKUP_PASS

from .helper_funcs.decorators import kigcmd
import shutil
from time import sleep




@kigcmd(command="backupdb", filters=filters.User(SYS_ADMIN) | filters.User(OWNER_ID))
async def backup_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cronjob.run(application=application)

@kigcmd(command="jobs", filters=filters.User(SYS_ADMIN) | filters.User(OWNER_ID))
async def get_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    a = cronjob.job_queue.jobs().count(j)
    print(a)
    await update.effective_message.reply_text(a)

@kigcmd(command="stopjobs", filters=filters.User(SYS_ADMIN) | filters.User(OWNER_ID))
async def stop_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(j.stop())
    await update.effective_message.reply_text("Scheduler has been shut down")

@kigcmd(command="startjobs", filters=filters.User(SYS_ADMIN) | filters.User(OWNER_ID))
async def start_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(j.start())
    await update.effective_message.reply_text("Scheduler started")

zip_pass = BACKUP_PASS

def backup_db(ctx: CallbackContext):
    bot = application.bot
    tmpmsg = "Performing backup, Please wait..."
    tmp = await bot.send_message(OWNER_ID, tmpmsg)
    datenow = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dbbkpname = "db_{}_{}.tar".format(bot.username, datenow)
    bkplocation = "backups/{}".format(datenow)
    bkpcmd = "pg_dump {} --format=tar > {}/{}".format(DB_URI, bkplocation, dbbkpname)

    if not os.path.exists(bkplocation):
        os.makedirs(bkplocation)
    log.info("performing db backup")
    loginfo = "db backup"
    term(bkpcmd, loginfo)
    if not os.path.exists('{}/{}'.format(bkplocation, dbbkpname)):
        await bot.send_message(OWNER_ID, "An error occurred during the db backup")
        tmp.edit_text("Backup Failed!")
        sleep(8)
        tmp.delete()
        return 
    else:
        log.info("copying config, logs, and updates to backup location")
        if os.path.exists('logs.txt'):
            print("logs copied")
            shutil.copyfile('logs.txt', '{}/logs.txt'.format(bkplocation))
        if os.path.exists('updates.txt'):
            print("updates copied")
            shutil.copyfile('updates.txt', '{}/updates.txt'.format(bkplocation))
        if os.path.exists('config.ini'):
            print("config copied")
            shutil.copyfile('config.ini', '{}/config.ini'.format(bkplocation))
        log.info("zipping the backup")
        zipcmd = "zip --password '{}' {} {}/*".format(zip_pass, bkplocation, bkplocation)
        zipinfo = "zipping db backup"
        log.info("zip intiated")
        term(zipcmd, zipinfo)
        log.info("zip done")
        sleep(1)
        with open('backups/{}'.format(f'{datenow}.zip'), 'rb') as bkp:
            nm = "{} backup \n".format(bot.username) + datenow
            await bot.send_document(OWNER_ID,
                              document=bkp,
                              caption=nm,
                              timeout=20
                              )
        log.info("removing zipped files")
        shutil.rmtree("backups/{}".format(datenow))
        log.info("backup done")
        tmp.edit_text("Backup complete!")
        sleep(5)
        tmp.delete()


@kigcmd(command="purgebackups", filters=filters.User(SYS_ADMIN) | filters.User(OWNER_ID))
async def stop_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    shutil.rmtree("backups")
    await update.effective_message.reply_text("'backups' directory has been purged!")

def term(cmd, info):
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    stdout, stderr = process.communicate()
    stderr = stderr.decode()
    stdout = stdout.decode()
    if stdout:
        log.info(f"{info} successful!")
        log.info(f"{stdout}")
    if stderr:
        log.error(f"error while running {info}")
        log.info(f"{stderr}")


from tg_bot import updater as u
j = u.job_queue
twhen = datetime.datetime.strptime('01:00', '%H:%M').time()
cronjob = j.run_daily(callback=backup_db, name="database backups", time=twhen)

