import os
import json
import random
from flask import Flask, request
import telegram
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, filters, ApplicationBuilder, ContextTypes, CallbackQueryHandler

app = Flask(__name__)

TOKEN = os.getenv("BOT_TOKEN")
URL = os.getenv("RENDER_EXTERNAL_URL")
PORT = int(os.environ.get("PORT", 5000))
XP_FILE = "xp_data.json"
PATTERN_FILE = "patterns.json"

# XP CONFIG
XP_PER_MESSAGE = 0  # Disabled earning XP from messages
XP_PER_PATTERN = 50
XP_RANKS = [
    (0, "🌱 Newborn"),
    (100, "⚙️ Novice Coder"),
    (300, "🔧 Pattern Apprentice"),
    (700, "🧠 Tactical Analyst"),
    (1200, "🧬 Signal Specialist"),
    (2000, "📈 Momentum Seeker"),
    (3500, "🎯 Entry Optimizer"),
    (6000, "💼 Risk Strategist"),
    (10000, "🚀 Trade Visionary"),
    (20000, "💀 Profit Reaper")
]

# ========== UTILITY FUNCTIONS ==========

def load_data():
    try:
        with open(XP_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(XP_FILE, 'w') as f:
        json.dump(data, f)

def get_rank(xp):
    for threshold, rank in reversed(XP_RANKS):
        if xp >= threshold:
            return rank
    return "🌱 Newborn"

def load_patterns():
    try:
        with open(PATTERN_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_patterns(data):
    with open(PATTERN_FILE, 'w') as f:
        json.dump(data, f)

# ========== HANDLERS ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome to CLAWSCore! Use /help to view commands.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🧠 CLAWSCore Commands:\n"
        "/xp - View your XP and rank\n"
        "/learn <pattern> - Teach the bot a pattern\n"
        "/patterns - List learned patterns\n"
        "/editpattern <old>|<new> - Edit a pattern\n"
        "/delpattern <pattern> - Delete a pattern\n"
    )
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    text = update.message.text
    data = load_data()

    if user_id not in data:
        data[user_id] = {"xp": 0}

    save_data(data)

async def xp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    data = load_data()
    xp = data.get(user_id, {}).get("xp", 0)
    rank = get_rank(xp)
    await update.message.reply_text(f"📊 XP: {xp}\n🏆 Rank: {rank}")

async def learn_pattern(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    text = update.message.text.replace("/learn", "", 1).strip()

    if not text:
        await update.message.reply_text("⚠️ Please provide a pattern to learn.")
        return

    patterns = load_patterns()
    if user_id not in patterns:
        patterns[user_id] = []

    if text in patterns[user_id]:
        await update.message.reply_text("🌀 Already learned that pattern.")
        return

    patterns[user_id].append(text)
    save_patterns(patterns)

    data = load_data()
    if user_id not in data:
        data[user_id] = {"xp": 0}
    data[user_id]["xp"] += XP_PER_PATTERN
    save_data(data)

    await update.message.reply_text(f"🧠 Learned: \"{text}\" (You gained {XP_PER_PATTERN} XP!)")

async def list_patterns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    patterns = load_patterns().get(user_id, [])

    if not patterns:
        await update.message.reply_text("📭 No patterns learned yet.")
    else:
        msg = "📚 Your Patterns:\n"
        msg += "\n".join(f"- {p}" for p in patterns)
        await update.message.reply_text(msg)

async def delete_pattern(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    text = update.message.text.replace("/delpattern", "", 1).strip()

    if not text:
        await update.message.reply_text("⚠️ Provide a pattern to delete.")
        return

    patterns = load_patterns()
    if user_id not in patterns or text not in patterns[user_id]:
        await update.message.reply_text("❌ Pattern not found.")
        return

    patterns[user_id].remove(text)
    save_patterns(patterns)
    await update.message.reply_text(f"🗑️ Deleted pattern: {text}")

async def edit_pattern(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    text = update.message.text.replace("/editpattern", "", 1).strip()

    if "|" not in text:
        await update.message.reply_text("⚠️ Use format: /editpattern old|new")
        return

    old, new = map(str.strip, text.split("|", 1))

    patterns = load_patterns()
    if user_id not in patterns or old not in patterns[user_id]:
        await update.message.reply_text("❌ Pattern not found.")
        return

    patterns[user_id][patterns[user_id].index(old)] = new
    save_patterns(patterns)
    await update.message.reply_text(f"✏️ Updated pattern: {old} ➡️ {new}")

# ========== SETUP TELEGRAM ==========

tg_app = ApplicationBuilder().token(TOKEN).build()
tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(CommandHandler("help", help_command))
tg_app.add_handler(CommandHandler("xp", xp))
tg_app.add_handler(CommandHandler("learn", learn_pattern))
tg_app.add_handler(CommandHandler("patterns", list_patterns))
tg_app.add_handler(CommandHandler("editpattern", edit_pattern))
tg_app.add_handler(CommandHandler("delpattern", delete_pattern))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# ========== DEPLOYMENT FLASK ==========

@app.route("/")
def home():
    return "CLAWSCore Bot Running"

@app.route(f"/{TOKEN}", methods=["POST"])
def receive_update():
    update = telegram.Update.de_json(request.get_json(force=True), Bot(TOKEN))
    tg_app.update_queue.put(update)
    return "ok"

if __name__ == "__main__":
    tg_app.run_polling()
    app.run(host="0.0.0.0", port=PORT)
