from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import os
from flask import Flask
import threading

# 🔐 Load token securely from environment variables
TOKEN = os.getenv("BOT_TOKEN")

# ✅ Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# 🧠 Command handler: /start
def start(update, context):
    update.message.reply_text("🤖 CLAWSCore activated. I'm ready to learn and trade, Commander!")

# 📥 Message handler: learns text
def handle_message(update, context):
    user_message = update.message.text
    update.message.reply_text(f"🧠 Learned: \"{user_message}\" (but my memory isn't saved yet 😉)")

# 🔁 Error handler
def error(update, context):
    logger.warning(f'Update {update} caused error {context.error}')

# 🌐 Flask app to keep Render instance alive
app = Flask(__name__)

@app.route("/")
def home():
    return "CLAWSCore is live.", 200

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

# 🔄 Main bot loop
def main():
    if not TOKEN:
        raise ValueError("❌ BOT_TOKEN environment variable not set!")

    # 🔌 Start keep-alive ping server
    keep_alive()

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
