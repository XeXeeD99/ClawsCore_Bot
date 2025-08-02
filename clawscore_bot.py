from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
import logging
import os
import json
import random
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
XP_FILE = "memory_bank/xp_data.json"

# ✅ Ensure the memory_bank folder exists
os.makedirs("memory_bank", exist_ok=True)

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

# ➕ Add XP
def add_xp(user_id, amount):
    data = load_xp()
    user_id = str(user_id)
    data[user_id] = data.get(user_id, 0) + amount
    save_xp(data)
    return data[user_id]

# 📊 Get XP
def get_xp(user_id):
    data = load_xp()
    return data.get(str(user_id), 0)

# 🏅 Ranks
RANKS = [
    (0, "🔰 Newbie"),
    (50, "📈 Beginner"),
    (150, "🎯 Trader"),
    (300, "💼 Analyst"),
    (600, "🧠 Strategist"),
    (1000, "🧠 Elite Strategist"),
    (2000, "🧠 Supreme Mind"),
    (3000, "💀 Sniper Master"),
    (5000, "🔮 Visionary"),
    (10000, "💰 Profit Reaper")
]

def get_rank(user_id):
    xp = get_xp(user_id)
    rank = RANKS[0][1]
    for threshold, title in RANKS:
        if xp >= threshold:
            rank = title
        else:
            break
    return rank

# 🚀 Phase 3 XP update logic

def handle_user_message(update, context):
    user_id = update.effective_user.id
    xp_gain = random.randint(1, 5)
    add_xp(user_id, xp_gain)

# 🎯 Sniper actions (use these in bot logic)
def sniper_confirmed(user_id):
    return add_xp(user_id, 70)

def sniper_missed(user_id):
    return add_xp(user_id, -40)

# 🧠 Pattern actions
def pattern_learned(user_id):
    return add_xp(user_id, 20)

def pattern_tested(user_id):
    return add_xp(user_id, 20)

def pattern_deleted(user_id):
    pass  # No XP deduction

# 🔍 Debug command to test

def xp_status(update, context):
    user_id = update.effective_user.id
    xp = get_xp(user_id)
    rank = get_rank(user_id)
    update.message.reply_text(f"XP: {xp}\nRank: {rank}")

# Register handlers

dispatcher.add_handler(CommandHandler("xp", xp_status))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_user_message))
