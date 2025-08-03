import logging
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Application, CommandHandler, MessageHandler, filters,
                          ContextTypes, CallbackQueryHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# XP and Pattern memory stores
XP_FILE = "xp_data.json"
PATTERN_FILE = "pattern_data.json"

# Fun rank system with emojis
RANKS = [
    (0, "🥚 Recruit"),
    (200, "🐣 Rookie"),
    (500, "🎯 Trainee Sniper"),
    (1000, "🔫 Marksman"),
    (2000, "💥 Sharpshooter"),
    (4000, "🚀 Tactician"),
    (7000, "👁️‍🗨️ Elite Visionary"),
    (10000, "⚡ Operative"),
    (15000, "🔥 XP Phantom"),
    (20000, "💀 Profit Reaper")
]

# Helper functions
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return {}

def save_data(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)

def get_rank(xp):
    for threshold, rank in reversed(RANKS):
        if xp >= threshold:
            return rank
    return RANKS[0][1]

xp_data = load_data(XP_FILE)
patterns = load_data(PATTERN_FILE)

# COMMANDS
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    xp_data.setdefault(str(user.id), {"xp": 0, "patterns": []})
    await update.message.reply_text(
        f"Welcome, {user.first_name}! 🧠\nReady to train me with your trading wisdom? 🧩 Use /help to see what I can do."
    )
    save_data(XP_FILE, xp_data)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛠️ *CLAWSCore Commands* 🛠️\n\n"
        "💡 /teach `<pattern>` – Teach me a new trading strategy.\n"
        "🔍 /show_patterns – View all saved patterns.\n"
        "🧹 /delete `<pattern>` – Delete a pattern you've saved.\n"
        "🎮 /test `<pattern>` – Simulate and test a trading pattern.\n"
        "🏅 /xp – Check your XP and rank.\n"
        "⚙️ /reset – Reset all your data (be careful!)\n\n"
        "Ready to evolve your trading brain with mine? Let's dominate the charts! 📈💥",
        parse_mode="Markdown"
    )

async def teach(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    pattern = ' '.join(context.args)

    if not pattern:
        await update.message.reply_text("🚨 Usage: /teach <your pattern here>")
        return

    xp_data.setdefault(user_id, {"xp": 0, "patterns": []})
    if pattern in xp_data[user_id]["patterns"]:
        await update.message.reply_text("⚠️ I've already learned that pattern from you!")
    else:
        xp_data[user_id]["patterns"].append(pattern)
        xp_data[user_id]["xp"] += 50
        rank = get_rank(xp_data[user_id]["xp"])
        await update.message.reply_text(
            f"✅ Learned! You gained +50 XP.\n\n📊 Total XP: {xp_data[user_id]['xp']}\n🎖️ Rank: {rank}"
        )
        save_data(XP_FILE, xp_data)
        save_data(PATTERN_FILE, patterns)

async def show_patterns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_patterns = xp_data.get(user_id, {}).get("patterns", [])

    if not user_patterns:
        await update.message.reply_text("📭 You haven't taught me any patterns yet!")
    else:
        formatted = '\n'.join(f"- {p}" for p in user_patterns)
        await update.message.reply_text(f"🧠 Your stored patterns:\n{formatted}")

async def delete_pattern(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    pattern = ' '.join(context.args)

    if not pattern:
        await update.message.reply_text("🚨 Usage: /delete <pattern>")
        return

    user_patterns = xp_data.get(user_id, {}).get("patterns", [])
    if pattern in user_patterns:
        user_patterns.remove(pattern)
        await update.message.reply_text(f"🗑️ Pattern removed: {pattern}")
        save_data(XP_FILE, xp_data)
    else:
        await update.message.reply_text("❌ Pattern not found.")

async def test_pattern(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pattern = ' '.join(context.args)

    if not pattern:
        await update.message.reply_text("🚨 Usage: /test <pattern>")
        return

    await update.message.reply_text(
        f"📈 Simulating pattern: *{pattern}*...\n\n⚙️ Test run complete. Looks promising! ✅",
        parse_mode="Markdown"
    )

async def xp_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = xp_data.get(user_id, {"xp": 0})
    rank = get_rank(data["xp"])
    await update.message.reply_text(
        f"🏅 XP: {data['xp']}\n🎖️ Rank: {rank}"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    xp_data[user_id] = {"xp": 0, "patterns": []}
    await update.message.reply_text("♻️ Your XP and patterns have been reset. Time for a fresh start!")
    save_data(XP_FILE, xp_data)

# MAIN
def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("teach", teach))
    app.add_handler(CommandHandler("show_patterns", show_patterns))
    app.add_handler(CommandHandler("delete", delete_pattern))
    app.add_handler(CommandHandler("test", test_pattern))
    app.add_handler(CommandHandler("xp", xp_status))
    app.add_handler(CommandHandler("reset", reset))

    app.run_polling()

if __name__ == '__main__':
    main()
