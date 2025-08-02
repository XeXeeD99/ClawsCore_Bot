from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
import logging
import os
import json
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

# 📁 Files
MEMORY_FILE = "memory_bank.txt"
XP_FILE = "user_xp.json"

# 📊 Load XP data
def load_xp():
    if not os.path.exists(XP_FILE):
        return {}
    with open(XP_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# 💾 Save XP data
def save_xp(data):
    with open(XP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# ➕ Add XP to user
def add_xp(user_id, amount=10):
    xp_data = load_xp()
    xp_data[str(user_id)] = xp_data.get(str(user_id), 0) + amount
    save_xp(xp_data)

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

# 📈 Command: /xp
def check_xp(update, context):
    user_id = update.effective_user.id
    xp_data = load_xp()
    xp = xp_data.get(str(user_id), 0)
    update.message.reply_text(f"💠 Your XP: {xp}")

# 📩 Message handler
def handle_message(update, context):
    user_id = update.effective_user.id
    user_message = update.message.text
    add_xp(user_id, 10)
    update.message.reply_text(f"🧠 Learned: \"{user_message}\" (You gained 10 XP!)")

# ❗ Error handler
def error(update, context):
    logger.warning(f'Update {update} caused error {context.error}')

# ✅ Register handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("save", save_pattern))
dispatcher.add_handler(CommandHandler("view", view_patterns))
dispatcher.add_handler(CommandHandler("delete", delete_pattern))
dispatcher.add_handler(CommandHandler("xp", check_xp))
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

@app.route("/setwebhook")
def set_webhook():
    webhook_url = f"https://clawscore-bot-1.onrender.com/{TOKEN}"
    bot.set_webhook(url=webhook_url)
    return f"Webhook set to: {webhook_url}", 200

if __name__ == '__main__':
    if not TOKEN:
        raise ValueError("❌ BOT_TOKEN environment variable not set!")

    # 🔗 Set webhook URL on startup
    webhook_url = f"https://clawscore-bot-1.onrender.com/{TOKEN}"
    bot.set_webhook(url=webhook_url)
    print(f"📡 Webhook set to: {webhook_url}")

    # 🚀 Start Flask server (blocking)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
