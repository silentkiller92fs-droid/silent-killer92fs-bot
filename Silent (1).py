import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

# 🔐 TOKEN
TOKEN = "8640972183:AAFoA5tHlABgdo4s6VWPkT_DP9rpauPJYMk"

# 🚀 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Link bhejo (Instagram / YouTube), main download karke dunga 🔥")

# 🎯 HANDLE MESSAGE
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    await update.message.reply_text("📥 Downloading...")

    try:
        ydl_opts = {
            'format': 'best',
            'noplaylist': True,
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file = ydl.prepare_filename(info)

        # 📤 SEND VIDEO
        await update.message.reply_video(video=open(file, 'rb'))

        # 🧹 DELETE FILE
        os.remove(file)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

# 🧠 MAIN
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

print("🤖 Bot running...")
app.run_polling()
