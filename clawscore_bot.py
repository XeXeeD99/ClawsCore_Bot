from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
import logging
import os
import json
import random
from flask import Flask, request

# 🔐 Secure token from environment
TOKEN = os.getenv("BOT_TOKEN")

# ✅ Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# 🤖 Bot and Dispatcher
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)

# 📁 Files
MEMORY_FILE = "memory_bank.txt"
XP_FILE = "memory_bank/xp_data.json"

# ✅ Ensure folder exists
os.makedirs("memory_bank", exist_ok=True)

# 🧠 Load XP
def load_xp():
    if not os.path.exists(XP_FILE):
        return {}
    with open(XP_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# 💾 Save XP
def save_xp(data):
    with open(XP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# ➕ Add XP
def add_xp(user_id, amount):
    data = load_xp()
    user_id = str(user_id)
    data[user_id] = data.get(user_id, 0) + amount
    save_xp(data)
    return data[user_id]

# 📊 Get XP
def get_xp(user_id):
    return load_xp().get(str(user_id), 0)

# 🏆 Rank System
def get_rank(xp):
    if xp >= 10000:
        return "💀 Profit Reaper"
    elif xp >= 5000:
        return "🎯 Master Strategist"
    elif xp >= 2500:
        return "🔥 Pattern Dominator"
    elif xp >= 1000:
        return "⚔️ Signal Slayer"
    elif xp >= 500:
        return "📈 Tactical Analyst"
    elif xp >= 200:
        return "📊 Rookie Trader"
    else:
        return "🧠 Learner"

# 📦 XP by action type
ACTION_XP = {
    "sniper_confirmed": 70,
    "missed_sniper": -40,
    "pattern_tested": 20,
    "pattern_learned": 20,
    "message_sent": lambda: random.randint(1, 5),
}

# ✅ XP update wrapper
def gain_xp(user_id, action):
    if action in ACTION_XP:
        amount = ACTION_XP[action]() if callable(ACTION_XP[action]) else ACTION_XP[action]
        return add_xp(user_id, amount)
    return get_xp(user_id)

# 🧪 Example command handlers (Update these for your actual logic)
def learn_pattern(update, context):
    user_id = update.effective_user.id
    gain_xp(user_id, "pattern_learned")

def test_pattern(update, context):
    user_id = update.effective_user.id
    gain_xp(user_id, "pattern_tested")

def sniper_confirmed(update, context):
    user_id = update.effective_user.id
    gain_xp(user_id, "sniper_confirmed")

def sniper_missed(update, context):
    user_id = update.effective_user.id
    gain_xp(user_id, "missed_sniper")

# 🗨️ Handle all messages (gain random XP silently)
def handle_message(update, context):
    user_id = update.effective_user.id
    gain_xp(user_id, "message_sent")

# 📈 Check XP (Optional command)
def check_xp(update, context):
    user_id = update.effective_user.id
    xp = get_xp(user_id)
    rank = get_rank(xp)
    update.message.reply_text(f"🧬 XP: {xp}\n🏅 Rank: {rank}")

# 🧩 Register handlers
dispatcher.add_handler(CommandHandler("learn", learn_pattern))
dispatcher.add_handler(CommandHandler("test", test_pattern))
dispatcher.add_handler(CommandHandler("sniper", sniper_confirmed))
dispatcher.add_handler(CommandHandler("miss", sniper_missed))
dispatcher.add_handler(CommandHandler("xp", check_xp))  # Optional: XP checker
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# 🚀 Flask webhook
app = Flask(__name__)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

@app.route("/")
def index():
    return "ClawsCore XP System Active"
