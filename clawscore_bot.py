import logging
import os
import asyncio
from aiohttp import web
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)

# === LOGGING ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# === ENV VARIABLES ===
TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_HOST = os.environ.get("WEBHOOK_HOST")
PORT = int(os.environ.get("PORT", 5000))

if not TOKEN or not WEBHOOK_HOST:
    raise RuntimeError("Missing BOT_TOKEN or WEBHOOK_HOST in environment variables.")

WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# === DATA STORE ===
user_data = {}

ranks = [
    (0, "📘 Newbie Analyst"),
    (300, "📈 Chart Reader"),
    (800, "📊 Candle Whisperer"),
    (1500, "🔍 Market Watcher"),
    (2500, "🧠 Pattern Disciple"),
    (4000, "📡 Signal Seeker"),
    (6000, "💠 Technical Adept"),
    (9000, "🎯 Entry Strategist"),
    (13000, "🧙‍♂️ Indicator Sage"),
    (17000, "🚀 Profit Chaser"),
    (20000, "💀 Profit Reaper"),
    (25000, "👑 CLAWSCore Elite")
]

badge_thresholds = {
    "Pattern Pro": 5,
    "XP Novice": 1000,
    "XP Expert": 5000,
    "Rank Master": "🧙‍♂️ Indicator Sage"
}

# === UTILS ===
def get_rank(xp):
    for i in range(len(ranks) - 1, -1, -1):
        if xp >= ranks[i][0]:
            return ranks[i][1]
    return ranks[0][1]

def get_next_rank(xp):
    for r in ranks:
        if xp < r[0]:
            return r[1], r[0]
    return None, None

def get_progress_bar(xp):
    current_rank = get_rank(xp)
    next_rank, next_xp = get_next_rank(xp)
    if not next_rank:
        return "\n\U0001F31F Max Rank Achieved"
    prev_xp = 0
    for r in ranks:
        if r[1] == current_rank:
            prev_xp = r[0]
            break
    filled = int(((xp - prev_xp) / (next_xp - prev_xp)) * 10)
    return "\n[{}{}]".format('\U0001F537' * filled, '⬜' * (10 - filled))

def check_badges(user):
    badges = set(user_data[user]["badges"])
    new_badges = []

    if len(user_data[user]["patterns"]) >= badge_thresholds["Pattern Pro"]:
        new_badges.append("Pattern Pro")
    if user_data[user]["xp"] >= badge_thresholds["XP Novice"]:
        new_badges.append("XP Novice")
    if user_data[user]["xp"] >= badge_thresholds["XP Expert"]:
        new_badges.append("XP Expert")
    if get_rank(user_data[user]["xp"]) == badge_thresholds["Rank Master"]:
        new_badges.append("Rank Master")

    for badge in new_badges:
        if badge not in badges:
            user_data[user]["badges"].append(badge)

# === COMMAND HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data.setdefault(user_id, {"xp": 0, "patterns": {}, "badges": []})
    await update.message.reply_text(
        "\U0001F44B Welcome to *CLAWSCore*\n\nUse /help to explore your tools!",
        parse_mode="MarkdownV2"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "\U0001F9F0 *CLAWSCore Help Guide*\n\n"
        "\U0001F4E5 /learn - Save a new trading pattern\n"
        "\U0001F4C2 /patterns - View saved patterns\n"
        "\U0001F4CA /xp - View XP & rank progress\n"
        "\U0001F5D1️ /delete [name] - Remove a pattern\n"
        "✏️ /edit [name] - Modify a pattern\n"
        "🎖 /badge - View unlocked badges",
        parse_mode="MarkdownV2"
    )

async def xp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    xp = user_data.get(user_id, {}).get("xp", 0)
    rank = get_rank(xp)
    next_rank, next_xp = get_next_rank(xp)
    progress = get_progress_bar(xp)
    check_badges(user_id)

    msg = f"\U0001F3C6 *Your XP Journey*\n\n"
    msg += f"\u2728 XP: `{xp}`\n"
    msg += f"🎖 Rank: *{rank}*\n"
    if next_rank:
        msg += f"\n\U0001F4C8 Next: *{next_rank}* at `{next_xp}` XP"
    msg += progress

    await update.message.reply_text(msg, parse_mode="MarkdownV2")

async def learn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /learn [pattern name] - [description]")
        return
    text = ' '.join(args)
    if '-' not in text:
        await update.message.reply_text("Please use '-' to separate the pattern name and description.")
        return
    name, desc = map(str.strip, text.split('-', 1))
    user_data[user_id]["patterns"][name] = desc
    user_data[user_id]["xp"] += 100
    check_badges(user_id)
    await update.message.reply_text(f"✅ Pattern '{name}' saved! You earned 100 XP.")

async def patterns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    patterns = user_data[user_id].get("patterns", {})
    if not patterns:
        await update.message.reply_text("No patterns saved yet.")
        return
    msg = "\U0001F4C2 *Your Patterns*\n\n"
    for name, desc in patterns.items():
        msg += f"- *{name}*: {desc}\n"
    await update.message.reply_text(msg, parse_mode="MarkdownV2")

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /delete [pattern name]")
        return
    name = ' '.join(args)
    if name in user_data[user_id]["patterns"]:
        del user_data[user_id]["patterns"][name]
        await update.message.reply_text(f"🗑️ Pattern '{name}' deleted.")
    else:
        await update.message.reply_text("Pattern not found.")

async def edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /edit [pattern name] - [new description]")
        return
    text = ' '.join(args)
    if '-' not in text:
        await update.message.reply_text("Please use '-' to separate the name and new description.")
        return
    name, desc = map(str.strip, text.split('-', 1))
    if name not in user_data[user_id]["patterns"]:
        await update.message.reply_text("Pattern not found.")
        return
    user_data[user_id]["patterns"][name] = desc
    await update.message.reply_text(f"✏️ Pattern '{name}' updated.")

async def badge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    check_badges(user_id)
    badges = user_data[user_id].get("badges", [])
    if not badges:
        await update.message.reply_text("You haven't earned any badges yet.")
        return
    msg = "🎖 *Your Badges*\n\n"
    for badge in badges:
        msg += f"🏅 {badge}\n"
    await update.message.reply_text(msg, parse_mode="MarkdownV2")

# === MAIN ===
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("xp", xp))
    app.add_handler(CommandHandler("learn", learn))
    app.add_handler(CommandHandler("patterns", patterns))
    app.add_handler(CommandHandler("delete", delete))
    app.add_handler(CommandHandler("edit", edit))
    app.add_handler(CommandHandler("badge", badge))

    await app.initialize()
    await app.bot.set_webhook(WEBHOOK_URL)
    logger.info(f"✅ Webhook set to {WEBHOOK_URL}")

    async def handle(request):
        try:
            data = await request.json()
            update = Update.de_json(data, app.bot)
            await app.process_update(update)
        except Exception as e:
            logger.error(f"❌ Failed to process update: {e}")
        return web.Response(text="OK")

    aio_app = web.Application()
    aio_app.router.add_post(WEBHOOK_PATH, handle)
    aio_app.router.add_get("/", lambda request: web.Response(text="CLAWSCore Bot is running 🐾"))

    runner = web.AppRunner(aio_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    logger.info(f"🚀 CLAWSCore running on port {PORT}")
    await site.start()

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
