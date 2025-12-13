# ================= SINGLE FILE TELEGRAM → FTP BOT =================
# Works in GitHub Codespaces / Workspace
# Copy → Paste → Run

import sys, os, subprocess, io, logging, asyncio
from ftplib import FTP, all_errors

# ---------- USER CONFIG (EDIT ONLY THIS PART) ----------
TELEGRAM_TOKEN = "8504397259:AAGYBFPC84AFOl7jYrIYOl3vq6GwEgfqGWA"

FTP_HOST = "ftp.indiatraderoute.com"
FTP_USER = "tele2ftp@indiatraderoute.com"
FTP_PASS = "ssB8Tx8bT7EH27PvzPDR"
FTP_DIR  = "domains/tharak.indiatraderoute.com/public_html/videos"
# ------------------------------------------------------

# ---------- LOGGING ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ---------- BASIC VALIDATION ----------
def die(msg):
    logging.error(msg)
    sys.exit(1)

if not TELEGRAM_TOKEN or "PASTE" in TELEGRAM_TOKEN:
    die("Telegram token missing or not replaced")

if not all([FTP_HOST, FTP_USER, FTP_PASS, FTP_DIR]):
    die("FTP credentials incomplete")

if sys.version_info < (3, 9):
    die("Python 3.9+ required")

# ---------- AUTO INSTALL DEPENDENCIES ----------
try:
    from telegram import Update
    from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
except Exception:
    logging.info("Installing python-telegram-bot...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "python-telegram-bot==20.7"
    ])
    from telegram import Update
    from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# ---------- FTP UPLOAD ----------
def upload_to_ftp(filename, data):
    try:
        with FTP(FTP_HOST, timeout=30) as ftp:
            ftp.login(FTP_USER, FTP_PASS)
            ftp.cwd(FTP_DIR)
            ftp.storbinary(f"STOR {filename}", io.BytesIO(data))
        logging.info(f"Uploaded: {filename}")
        return True
    except all_errors as e:
        logging.error(f"FTP error: {e}")
        return False

# ---------- TELEGRAM HANDLER ----------
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message:
            return

        file = (
            update.message.document
            or (update.message.photo[-1] if update.message.photo else None)
            or update.message.video
            or update.message.audio
        )

        if not file:
            await update.message.reply_text("❌ Send a file only")
            return

        tg_file = await context.bot.get_file(file.file_id)
        data = await tg_file.download_as_bytearray()
        filename = getattr(file, "file_name", f"file_{file.file_id}")

        if upload_to_ftp(filename, data):
            await update.message.reply_text(f"✅ Uploaded: {filename}")
        else:
            await update.message.reply_text("❌ FTP upload failed")

    except Exception as e:
        logging.exception("Handler error")
        if update.message:
            await update.message.reply_text("❌ Internal error")

# ---------- BOT START ----------
async def main():
    try:
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app.add_handler(MessageHandler(filters.ALL, handle))
        logging.info("🚀 Telegram → FTP Bot started")
        await app.run_polling()
    except Exception as e:
        die(f"Bot failed to start: {e}")

if __name__ == "__main__":
    asyncio.run(main())

# ================= END OF FILE =================
