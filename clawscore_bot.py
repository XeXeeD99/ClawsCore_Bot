from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
import logging
import os
from flask import Flask, request

# 🔐 Load token securely from environment variables
TOKEN = os.getenv("BOT_TOKEN")

# ✅ Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# 🤖 Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)

# 🧠 Command: /start
def start(update, context):
    update.message.reply_text("🤖 CLAWSCore activated. I'm ready to learn and trade, Commander!")

# 📩 Message handler
def handle_message(update, context):
    user_message = update.message.text
    update.message.reply_text(f"🧠 Learned: \"{user_message}\" (but my memory isn't saved yet 😉)")

# ❗ Error handler
def error(update, context):
    logger.warning(f'Update {update} caused error {context.error}')

# ✅ Register handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
dispatcher.add_error_handler(error)

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

if __name__ == '__main__':
    if not TOKEN:
        raise ValueError("❌ BOT_TOKEN environment variable not set!")

    # 🔗 Set the webhook URL
    webhook_url = f"https://clawscore-bot-1.onrender.com/{TOKEN}"
    bot.set_webhook(url=webhook_url)
    print(f"📡 Webhook set to: {webhook_url}")

    # 🚀 Start Flask server (blocking)
    port = int(os.environ.get("PORT", 10000))  # Render assigns this automatically
    app.run(host="0.0.0.0", port=port)
