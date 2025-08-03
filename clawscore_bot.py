import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# In-memory XP tracker
user_xp = {}

# Fun and vibrant rank system 🎮🚀
def get_rank(xp):
    if xp >= 20000:
        return "🔥 Profit Reaper 🔥📊💀"
    elif xp >= 10000:
        return "💎 Synth Lord 💎🤖"
    elif xp >= 7000:
        return "⚡ Data Phantom ⚡👁️"
    elif xp >= 4000:
        return "🌀 Pulse Seeker 🌀🔬"
    elif xp >= 2000:
        return "🧠 Core Analyst 🧠⚙️"
    elif xp >= 1000:
        return "🦾 Signal Slinger 🦾📈"
    elif xp >= 500:
        return "🎯 Pattern Hunter 🎯🔍"
    elif xp >= 200:
        return "🧪 Logic Learner 🧠📘"
    else:
        return "🐣 Init Node 🐣"

# XP increment handler
async def add_xp(update: Update, context: ContextTypes.DEFAULT_TYPE, amount: int, reason: str):
    user_id = update.effective_user.id
    user_xp[user_id] = user_xp.get(user_id, 0) + amount
    xp = user_xp[user_id]
    rank = get_rank(xp)
    await update.message.reply_text(
        f"✅ XP +{amount} ({reason})\n🎖️ New XP: {xp}\n🏅 Rank: {rank}"
    )

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Yo! Welcome to *CLAWSCore*, your AI trading buddy in beast mode! 💹🤖\nUse /help to unlock my secrets!",
        parse_mode='Markdown'
    )
    await add_xp(update, context, 10, "Boot-Up Bonus")

# /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧠 *CLAWSCore Help Menu* 🧠\n\n"
        "🔹 /start — Boot the system ⚡\n"
        "🔹 /profile — Check your trader rank 🧬\n"
        "🔹 /learn [pattern] — Teach me your trading logic 🧠\n"
        "🔹 /patterns — View saved patterns 📚\n"
        "🔹 /deletepattern [name] — Remove a pattern ❌\n"
        "🔹 /testpattern [name] — Simulate a strategy 🧪📈\n"
        "🔹 /badgecase — View badges you've unlocked 🏅\n\n"
        "✨ More systems activating soon... stay sharp, operator."
        , parse_mode='Markdown'
    )

# /profile command
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    xp = user_xp.get(user_id, 0)
    rank = get_rank(xp)
    await update.message.reply_text(
        f"🧾 *Your Profile*\n\n"
        f"👤 User: {update.effective_user.first_name}\n"
        f"⚡ XP: {xp}\n"
        f"🏅 Rank: {rank}"
        , parse_mode='Markdown')

if __name__ == '__main__':
    import os
    TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        raise ValueError("Missing bot token!")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("profile", profile))

    app.run_polling()
