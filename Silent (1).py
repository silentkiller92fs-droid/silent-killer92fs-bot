import os
import yt_dlp
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8640972183:AAFoA5tHlABgdo4s6VWPkT_DP9rpauPJYMk"

# keyboard
keyboard = [["360p", "720p"], ["1080p", "Audio"]]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

user_choice = {}

# start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send video link", reply_markup=reply_markup)

# handle quality buttons
async def handle_quality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_choice[update.message.chat_id] = update.message.text
    await update.message.reply_text(f"Selected: {update.message.text}\nNow send link")

# handle link
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    choice = user_choice.get(chat_id, "720p")

    await update.message.reply_text("Downloading...")

    try:
        ydl_opts = {
            "outtmpl": "video.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "extractor_args": {"youtube": {"player_client": ["android"]}},
        }

        # quality logic
        if choice == "360p":
            ydl_opts["format"] = "bestvideo[height<=360]+bestaudio/best[height<=360]"
        elif choice == "720p":
            ydl_opts["format"] = "bestvideo[height<=720]+bestaudio/best[height<=720]"
        elif choice == "1080p":
            ydl_opts["format"] = "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
        elif choice == "Audio":
            ydl_opts["format"] = "bestaudio"
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
            }]
        else:
            ydl_opts["format"] = "best"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info)

        # send file
        if choice == "Audio":
            file_name = file_name.replace(".webm", ".mp3").replace(".m4a", ".mp3")
            await update.message.reply_audio(audio=open(file_name, "rb"))
        else:
            await update.message.reply_video(video=open(file_name, "rb"))

        os.remove(file_name)

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

# main
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
app.add_handler(MessageHandler(filters.Regex("^(360p|720p|1080p|Audio)$"), handle_quality))

app.run_polling()
