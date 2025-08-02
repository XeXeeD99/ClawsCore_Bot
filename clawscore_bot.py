from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
from flask import Flask, request
import os
import logging

# 🌐 Flask app
app = Flask(__name__)

# 🔐 Telegram bot token
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)

# ✅ Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# 🔄 Dispatcher for handling updates
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=4, use_context=True)

# 🔧 Command handler
def start(update, context):
    update.message.reply_text("🤖 CLAWSCore activated. I'm ready to learn and trade, Commander!")

# 🔧 Message handler
def handle_message(update, context):
    update.message.reply_text(f"🧠 Learned: \"{update.message.text}\" (but my memory isn't saved yet 😉)")

# 🔧 Error handler
def error(update, context):
    logger.warning(f'Update {update} caused error {context.error}')

# ✅ Register handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
dispatcher.add_error_handler(error)

# 🧠 Webhook endpoint
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

# 🏠 Home page (for Render ping)
@app.route("/")
def index():
    return "CLAWSCore is online.", 200

# 🚀 Start app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)dispatcher.add_error_handler(error)

# 🌐 Flask app
app = Flask(__name__)

@app.route("/")
def home():
    return "CLAWSCore is live.", 200

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = threading.Thread(target=run)
    t.daemon = True
    t.start()

# 🔄 Main bot entry point
def main():
    if not TOKEN:
        raise ValueError("❌ BOT_TOKEN environment variable not set!")

    # Start Flask server to keep Render container alive
    keep_alive()

    # ✅ Set webhook to your Render app URL
    webhook_url = f"https://clawscore-bot-1.onrender.com/{TOKEN}"
    bot.set_webhook(url=webhook_url)
    print(f"📡 Webhook set to: {webhook_url}")

if __name__ == '__main__':
    main()    # ✅ Use Render's assigned port from environment (defaults to 8080 if local)
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = threading.Thread(target=run)
    t.daemon = True
    t.start()

# 🔄 Main bot loop
def main():
    if not TOKEN:
        raise ValueError("❌ BOT_TOKEN environment variable not set!")

    # 🔌 Start keep-alive ping server
    keep_alive()

    # 🤖 Start Telegram bot
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
