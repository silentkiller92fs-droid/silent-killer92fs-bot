import os
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 🔐 ENV VARIABLES
TOKEN = os.getenv("TOKEN")
GROQ_API = os.getenv("GROQ_API")

# 🎛 BUTTONS
keyboard = [["Python", "JavaScript"], ["HTML", "CSS"]]
markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# 💾 USER DATA
user_idea = {}

# 🚀 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Apna idea bhejo")

# 🧠 MAIN FUNCTION
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.message.chat_id

    # 👉 Language select
    if text in ["Python", "JavaScript", "HTML", "CSS"]:
        if chat_id not in user_idea:
            await update.message.reply_text("Pehle idea bhejo")
            return

        idea = user_idea[chat_id]
        await update.message.reply_text("Code bana raha hu...")

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama3-70b-8192",
                    "messages": [
                        {"role": "system", "content": "Only return clean code"},
                        {"role": "user", "content": f"{text} code for: {idea}"}
                    ]
                }
            )

            data = response.json()
            code = data["choices"][0]["message"]["content"]

            # 👉 safe send
            if len(code) > 4000:
                with open("code.txt", "w", encoding="utf-8") as f:
                    f.write(code)
                await update.message.reply_document(open("code.txt", "rb"))
            else:
                await update.message.reply_text(code)

        except Exception as e:
            await update.message.reply_text(f"Error: {str(e)}")

    # 👉 Idea save
    else:
        user_idea[chat_id] = text
        await update.message.reply_text("Language choose karo", reply_markup=markup)

# 🤖 APP
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

print("Bot running...")
app.run_polling()
