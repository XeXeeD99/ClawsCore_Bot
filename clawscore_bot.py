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

# 📁 Memory Bank file
MEMORY_FILE = "memory_bank.txt"

# 🧠 Command: /start
def start(update, context):
    update.message.reply_text("🤖 CLAWSCore activated. Ready to learn and trade, Commander!")

# 💾 Command: /save [pattern]
def save_pattern(update, context):
    pattern = " ".join(context.args)
    if not pattern:
        update.message.reply_text("⚠️ Usage: /save [pattern]")
        return

    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(pattern + "\n")

    update.message.reply_text(f"✅ Pattern saved:\n\n{pattern}")

# 📖 Command: /view
def view_patterns(update, context):
    if not os.path.exists(MEMORY_FILE):
        update.message.reply_text("📂 No patterns saved yet.")
        return

    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        patterns = f.readlines()

    if not patterns:
        update.message.reply_text("📂 Your memory bank is empty.")
    else:
        message = "\n".join([f"{i+1}. {p.strip()}" for i, p in enumerate(patterns)])
        update.message.reply_text(f"🧠 Stored Patterns:\n\n{message}")

# ❌ Command: /delete [index]
def delete_pattern(update, context):
    try:
        index = int(context.args[0]) - 1
    except (IndexError, ValueError):
        update.message.reply_text("⚠️ Usage: /delete [pattern number]")
        return

    if not os.path.exists(MEMORY_FILE):
        update.message.reply_text("📂 No patterns saved yet.")
        return

    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        patterns = f.readlines()

    if index < 0 or index >= len(patterns):
        update.message.reply_text("🚫 Invalid pattern number.")
        return

    deleted = patterns.pop(index)

    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        f.writelines(patterns)

    update.message.reply_text(f"🗑️ Deleted:\n\n{deleted.strip()}")

# 📩 Message handler
def handle_message(update, context):
    user_message = update.message.text
    update.message.reply_text(f"🧠 Learned: \"{user_message}\" (but my memory isn't saved yet 😉)")

# ❗ Error handler
def error(update, context):
    logger.warning(f'Update {update} caused error {context.error}')

# ✅ Register handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("save", save_pattern))
dispatcher.add_handler(CommandHandler("view", view_patterns))
dispatcher.add_handler(CommandHandler("delete", delete_pattern))
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
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
