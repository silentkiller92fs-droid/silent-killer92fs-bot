import os
import yt_dlp
import asyncio
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

# TOKEN from environment (Render safe)
TOKEN ="8640972183:AAFoA5tHlABgdo4s6VWPkT_DP9rpauPJYMk"

QUALITY = 1

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Silent Killer Bot\nSend a video link"
    )

# URL CHECK
def is_valid_url(url):
    return url.startswith("http")

# HANDLE LINK
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text.strip()

    if not is_valid_url(link):
        await update.message.reply_text("Invalid link")
        return ConversationHandler.END

    # save link safely
    context.user_data["link"] = link

    keyboard = [
        ["360p", "720p"],
        ["1080p", "Best"],
        ["Audio", "Cancel"]
    ]

    await update.message.reply_text(
        "Choose quality:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

    return QUALITY

# DOWNLOAD
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    link = context.user_data.get("link")

    if not link:
        await update.message.reply_text("Send link again")
        return ConversationHandler.END

    if choice == "Cancel":
        await update.message.reply_text("Cancelled", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    await update.message.reply_text("Processing...")

    # SMART FORMAT FIX
    if "instagram" in link or "facebook" in link:
        fmt = "best"
    elif choice == "360p":
        fmt = "bestvideo[height<=360]+bestaudio/best[height<=360]"
    elif choice == "720p":
        fmt = "bestvideo[height<=720]+bestaudio/best[height<=720]"
    elif choice == "1080p":
        fmt = "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
    elif choice == "Audio":
        fmt = "bestaudio/best"
    else:
        fmt = "best"

    filename_template = f"{update.message.from_user.id}_file.%(ext)s"

    ydl_opts = {
        'format': fmt,
        'outtmpl': filename_template,
        'merge_output_format': 'mp4',
        'quiet': True,
        'noplaylist': True,
        'socket_timeout': 30,
        'retries': 3,
        'fragment_retries': 3,
        'ffmpeg_location': '/data/data/com.termux/files/usr/bin/ffmpeg'
    }

    try:
        await update.message.reply_text("Downloading...")

        loop = asyncio.get_event_loop()

        def run_download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=True)
                return ydl.prepare_filename(info)

        filename = await loop.run_in_executor(None, run_download)

        if not os.path.exists(filename):
            await update.message.reply_text("Download failed")
            return ConversationHandler.END

        size = os.path.getsize(filename) / (1024 * 1024)

        if size > 49:
            os.remove(filename)
            await update.message.reply_text("File too large (50MB limit)")
            return ConversationHandler.END

        await update.message.reply_text("Uploading...")

        with open(filename, 'rb') as f:
            if choice == "Audio":
                await update.message.reply_audio(audio=f)
            else:
                await update.message.reply_video(video=f)

        os.remove(filename)

        await update.message.reply_text("Done", reply_markup=ReplyKeyboardRemove())

        # clear memory (important fix)
        context.user_data.clear()

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

    return ConversationHandler.END

# MAIN
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link)],
        states={
            QUALITY: [MessageHandler(filters.TEXT, download_video)]
        },
        fallbacks=[]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
