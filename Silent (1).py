import os
import yt_dlp
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8640972183:AAFoA5tHlABgdo4s6VWPkT_DP9rpauPJYMk"

# buttons
keyboard = [
    ["360p", "720p"],
    ["1080p", "Audio"],
]
markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send video link", reply_markup=markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # quality select
    if text in ["360p", "720p", "1080p", "Audio"]:
        user_data[update.message.chat_id] = text
        await update.message.reply_text("Now send link")
        return

    url = text
    quality = user_data.get(update.message.chat_id, "best")

    await update.message.reply_text("Downloading...")

    try:
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'quiet': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0'
            }
        }

        if quality == "Audio":
            ydl_opts['format'] = 'bestaudio'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file = ydl.prepare_filename(info)

        # send file
        if quality == "Audio":
            await update.message.reply_audio(audio=open(file, 'rb'))
        else:
            await update.message.reply_video(video=open(file, 'rb'))

        os.remove(file)

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot Running...")
app.run_polling()
