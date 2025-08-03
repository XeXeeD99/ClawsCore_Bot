import os
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, CallbackQueryHandler
)

# === LOGGER ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# === FILE PATHS ===
XP_FILE = "xp_data.json"
PATTERN_FILE = "patterns.json"

# === XP RANK SYSTEM ===
ranks = [
    (0, "🔹 Rookie"),
    (100, "🔸 Learner"),
    (300, "🛡️ Apprentice"),
    (700, "🎯 Analyst"),
    (1500, "⚔️ Strategist"),
    (3000, "🔮 Pattern Master"),
    (5000, "🧠 Tactician"),
    (8000, "💻 Visionary"),
    (12000, "♟️ Trade Warlock"),
    (20000, "☠️ Profit Reaper")
]

# === UTILITIES ===
def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return {}

def save_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

def get_rank(xp):
    for threshold, rank in reversed(ranks):
        if xp >= threshold:
            return rank
    return ranks[0][1]

# === XP SYSTEM ===
def add_xp(user_id, amount):
    data = load_json(XP_FILE)
    user_id = str(user_id)
    xp = data.get(user_id, 0)
    xp += amount
    data[user_id] = xp
    save_json(XP_FILE, data)
    return xp, get_rank(xp)

def get_user_xp(user_id):
    data = load_json(XP_FILE)
    xp = data.get(str(user_id), 0)
    return xp, get_rank(xp)

# === TELEGRAM COMMANDS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome to CLAWSCore, your AI Trading Ally! Type /help to begin your XP journey.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🤖 *CLAWSCore Command List*:
        
        /start – Welcome message 👐
        /help – Show this help menu 📘
        /xp – Check your XP and rank 📊
        /learn [pattern] – Teach me a pattern 🧠
        /patterns – View all saved patterns 📂
        /test [pattern_name] – Test a saved pattern 🧪
        /forget [pattern_name] – Delete a pattern 🗑️"
    )
    await update.message.reply_markdown(text)

async def xp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    xp, rank = get_user_xp(user_id)
    await update.message.reply_text(f"📈 XP: {xp}\n🏅 Rank: {rank}")

# === PATTERN MEMORY ===
def load_patterns():
    return load_json(PATTERN_FILE)

def save_patterns(data):
    save_json(PATTERN_FILE, data)

async def learn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.split(" ", 1)
    if len(text) < 2:
        await update.message.reply_text("⚠️ Usage: /learn [pattern_name]: [pattern_content]")
        return

    try:
        name, content = text[1].split(":", 1)
        name = name.strip()
        content = content.strip()
    except ValueError:
        await update.message.reply_text("⚠️ Use format: /learn [pattern_name]: [pattern_content]")
        return

    patterns = load_patterns()
    patterns[name] = content
    save_patterns(patterns)
    xp, rank = add_xp(user_id, 70)
    await update.message.reply_text(f"✅ Pattern '{name}' saved! (+70 XP)\n📈 Total XP: {xp}\n🏅 Rank: {rank}")

async def list_patterns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    patterns = load_patterns()
    if not patterns:
        await update.message.reply_text("🔍 No patterns saved yet!")
    else:
        reply = "📚 *Saved Patterns:*\n\n" + "\n".join([f"🔹 {k}" for k in patterns])
        await update.message.reply_markdown(reply)

async def test_pattern(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("⚠️ Usage: /test [pattern_name]")
        return

    name = " ".join(context.args)
    patterns = load_patterns()
    content = patterns.get(name)
    if content:
        await update.message.reply_text(f"🧪 Testing Pattern '{name}':\n\n{content}")
    else:
        await update.message.reply_text("❌ Pattern not found.")

async def forget_pattern(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("⚠️ Usage: /forget [pattern_name]")
        return

    name = " ".join(context.args)
    patterns = load_patterns()
    if name in patterns:
        del patterns[name]
        save_patterns(patterns)
        await update.message.reply_text(f"🗑️ Pattern '{name}' deleted.")
    else:
        await update.message.reply_text("❌ Pattern not found.")

# === MAIN APP ===
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Sorry, I didn’t understand that command.")

if __name__ == "__main__":
    TOKEN = os.environ.get("BOT_TOKEN")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("xp", xp_command))
    app.add_handler(CommandHandler("learn", learn))
    app.add_handler(CommandHandler("patterns", list_patterns))
    app.add_handler(CommandHandler("test", test_pattern))
    app.add_handler(CommandHandler("forget", forget_pattern))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    app.run_polling()
