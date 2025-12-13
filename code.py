import nest_asyncio
nest_asyncio.apply()

# Dependencies check
try:
    from telegram import Update
    from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
except ImportError:
    import subprocess, sys
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "python-telegram-bot==20.7",
        "nest_asyncio"
    ])
    from telegram import Update
    from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

from ftplib import FTP, all_errors
import io
import logging

# ====== LOGGING ======
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ====== CONFIG ======
TELEGRAM_TOKEN = "8504397259:AAF8JMbj-q235HxaxA5o3PMXE9sEx46a5k8"
FTP_HOST = "ftp.indiatraderoute.com"
FTP_USER = "tele2ftp@indiatraderoute.com"
FTP_PASS = "mnSyNPcrmtYELV3XKLZd"
FTP_DIR  = "/home/indiatra/domains/tharak.indiatraderoute.com/videos"

# ====== FTP UPLOAD FUNCTION ======
def upload_to_ftp(filename, file_bytes):
    try:
        ftp = FTP(FTP_HOST, timeout=30)
        ftp.login(FTP_USER, FTP_PASS)
        ftp.cwd(FTP_DIR)
        ftp.storbinary(f"STOR {filename}", io.BytesIO(file_bytes))
        ftp.quit()
        logging.info(f"Uploaded: {filename}")
        return True
    except all_errors as e:
        logging.error(f"FTP Upload failed: {e}")
        return False

# ====== TELEGRAM HANDLER ======
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = (
        update.message.document
        or (update.message.photo[-1] if update.message.photo else None)
        or update.message.video
        or update.message.audio
    )
    if not file:
        return

    tg_file = await context.bot.get_file(file.file_id)
    file_bytes = await tg_file.download_as_bytearray()
    filename = getattr(file, "file_name", f"file_{file.file_id}")

    success = upload_to_ftp(filename, file_bytes)
    if success:
        await update.message.reply_text(f"✅ Uploaded to FTP: {filename}")
    else:
        await update.message.reply_text(f"❌ FTP Upload Failed: {filename}")

# ====== RUN BOT ======
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, handle_file))
    logging.info("Telegram → FTP Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()
