import json
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CACHE_DIR = "cache"

# ---------------- HELPERS ----------------
def load_cache(filename):
    path = os.path.join(CACHE_DIR, filename)
    if not os.path.exists(path):
        return "Data not ready. Please check later."
    with open(path) as f:
        return json.load(f)["content"]

# ---------------- COMMANDS ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 Welcome to MarketToday\n\n"
        "/free - Free market summary\n"
        "/premium - Premium insight (locked)"
    )

async def free(update: Update, context: ContextTypes.DEFAULT_TYPE):
    content = load_cache("free.json")
    await update.message.reply_text(content)

async def premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔒 Premium access required.\n"
        "Coming soon."
    )

# ---------------- MAIN ----------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("free", free))
    app.add_handler(CommandHandler("premium", premium))

    print("🤖 Bot running")
    app.run_polling()

if __name__ == "__main__":
    main()
