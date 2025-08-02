from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
from flask import Flask, request
import os
import json
import logging
import random

# === CONFIGURATION === #
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)
app = Flask(__name__)

# === FILES === #
MEMORY_FILE = "memory_bank.txt"
XP_FILE = "user_xp.json"

# === LOGGING === #
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === XP SYSTEM === #
RANKS = [
    (0, "📘 Newbie"), (100, "📗 Initiate"), (300, "📕 Strategist"),
    (700, "📙 Pattern Adept"), (1500, "📒 Chart Whisperer"),
    (3000, "📓 Trade Alchemist"), (5000, "📔 Neural Trader"),
    (8000, "📚 Visionary"), (12000, "📖 AI Syncer"),
    (20000, "📜 Profit Reaper")
]

def load_xp():
    if not os.path.exists(XP_FILE):
        return {}
    with open(XP_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_xp(data):
    with open(XP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def update_xp(user_id, amount):
    data = load_xp()
    data[str(user_id)] = data.get(str(user_id), 0) + amount
    save_xp(data)
    return data[str(user_id)]

def get_rank(xp):
    for threshold, rank in reversed(RANKS):
        if xp >= threshold:
            return rank
    return RANKS[0][1]

# === MEMORY SYSTEM === #
def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return f.read().splitlines()

def save_memory(lines):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def learn_memory(text):
    lines = load_memory()
    if text not in lines:
        lines.append(text)
        save_memory(lines)
        return True
    return False

def delete_memory(text):
    lines = load_memory()
    if text in lines:
        lines.remove(text)
        save_memory(lines)
        return True
    return False

# === TELEGRAM COMMANDS === #
def start(update, context):
    update.message.reply_text("CLAWSCore online. Use /learn, /memory, /xp, /rank, /test_pattern")

def learn(update, context):
    text = " ".join(context.args)
    if not text:
        update.message.reply_text("Usage: /learn <pattern or message>")
        return
    success = learn_memory(text)
    if success:
        xp = update_xp(update.effective_user.id, 20)
        rank = get_rank(xp)
        update.message.reply_text(f"🧠 Learned: \"{text}\"\n+20 XP | Rank: {rank}")
    else:
        update.message.reply_text("Pattern already known.")

def memory(update, context):
    memories = load_memory()
    if memories:
        update.message.reply_text("📚 Memory Bank:\n" + "\n".join(memories))
    else:
        update.message.reply_text("Memory bank is empty.")

def delete(update, context):
    text = " ".join(context.args)
    if not text:
        update.message.reply_text("Usage: /delete <pattern>")
        return
    if delete_memory(text):
        update.message.reply_text(f"🗑️ Deleted: \"{text}\"")
    else:
        update.message.reply_text("Pattern not found.")

def test_pattern(update, context):
    patterns = load_memory()
    if not patterns:
        update.message.reply_text("No patterns in memory.")
        return
    text = " ".join(context.args)
    if text in patterns:
        update.message.reply_text(f"✅ Pattern match: \"{text}\"")
        update_xp(update.effective_user.id, 20)
    else:
        update.message.reply_text(f"❌ Pattern not found: \"{text}\"")

def xp(update, context):
    user_id = update.effective_user.id
    xp_amount = load_xp().get(str(user_id), 0)
    update.message.reply_text(f"🧬 XP: {xp_amount}")

def rank(update, context):
    user_id = update.effective_user.id
    xp_amount = load_xp().get(str(user_id), 0)
    rank_name = get_rank(xp_amount)
    update.message.reply_text(f"🎖️ Rank: {rank_name}")

# === REGISTER COMMANDS === #
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("learn", learn))
dispatcher.add_handler(CommandHandler("memory", memory))
dispatcher.add_handler(CommandHandler("delete", delete))
dispatcher.add_handler(CommandHandler("test_pattern", test_pattern))
dispatcher.add_handler(CommandHandler("xp", xp))
dispatcher.add_handler(CommandHandler("rank", rank))

# === FLASK HOOK === #
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

@app.route("/", methods=["GET"])
def home():
    return "CLAWSCore bot is alive."

# === MAIN ENTRY === #
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))def save_xp(data):
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
