# CLAWSCore Bot with Full Command Set (Phase 1-3)

import logging
import os
import asyncio
from aiohttp import web
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)

# === LOGGING ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# === ENVIRONMENT VARIABLES ===
TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_HOST = os.environ.get("WEBHOOK_HOST")
PORT = int(os.environ.get("PORT", 5000))

if not TOKEN or not WEBHOOK_HOST:
    raise RuntimeError("Missing BOT_TOKEN or WEBHOOK_HOST in environment variables.")

WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# === USER DATA (IN-MEMORY) ===
user_data = {}

ranks = [
    (0, "📘 Newbie Analyst"),
    (300, "📈 Chart Reader"),
    (800, "📊 Candle Whisperer"),
    (1500, "🔍 Market Watcher"),
    (2500, "🧠 Pattern Disciple"),
    (4000, "📱 Signal Seeker"),
    (6000, "🖐 Technical Adept"),
    (9000, "🎯 Entry Strategist"),
    (13000, "🧙‍♂️ Indicator Sage"),
    (17000, "🚀 Profit Chaser"),
    (20000, "💀 Profit Reaper")
]

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
        return "\n🌟 Max Rank Achieved"
    prev_xp = 0
    for r in ranks:
        if r[1] == current_rank:
            prev_xp = r[0]
            break
    filled = int(((xp - prev_xp) / (next_xp - prev_xp)) * 10)
    return f"\n[{'\U0001f539' * filled}{'⬜' * (10 - filled)}]"

# === COMMAND HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data.setdefault(user_id, {"xp": 0, "patterns": {}, "badges": []})
    await update.message.reply_text(
        "👋 Welcome to *CLAWSCore*\n\nUse /help to explore your tools!",
        parse_mode=ParseMode.MARKDOWN_V2
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🪰 *CLAWSCore Help Guide*\n\n"
        "📅 /learn \- Save a new trading pattern\n"
        "📂 /patterns \- View saved patterns\n"
        "📊 /xp \- View XP & rank progress\n"
        "🗑️ /delete [name] \- Remove a pattern\n"
        "✏️ /edit [name] \- Modify a pattern\n"
        "🧪 /test \- Quiz yourself with saved patterns\n"
        "🎓 /train \- Run a strategy simulation\n"
        "🏅 /badge \- View unlocked badges\n\n"
        "✨ More trading magic coming soon \!",
        parse_mode=ParseMode.MARKDOWN_V2
    )

async def xp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    xp = user_data.get(user_id, {}).get("xp", 0)
    rank = get_rank(xp)
    next_rank, next_xp = get_next_rank(xp)
    progress = get_progress_bar(xp)

    msg = f"\ud83c\udfc6 *Your XP Journey*\n\n"
    msg += f"\u2728 XP: `{xp}`\n"
    msg += f"\ud83c\udf96\ufe0f Rank: *{rank}*\n"
    if next_rank:
        msg += f"\ud83d\udcc8 Next: *{next_rank}* at `{next_xp}` XP"
    msg += progress

    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN_V2)

# === Phase 2 Features ===
async def learn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    if len(args) < 2:
        return await update.message.reply_text("Usage: /learn [name] [pattern description]")

    name, pattern = args[0], ' '.join(args[1:])
    user = user_data.setdefault(user_id, {"xp": 0, "patterns": {}, "badges": []})
    user["patterns"][name] = pattern
    user["xp"] += 50
    await update.message.reply_text(f"✅ Pattern *{name}* saved and 50 XP gained!", parse_mode=ParseMode.MARKDOWN_V2)

async def patterns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    patterns = user_data.get(user_id, {}).get("patterns", {})
    if not patterns:
        return await update.message.reply_text("No patterns saved yet. Use /learn to add one!")

    msg = "📂 *Saved Patterns:*\n\n"
    for name, desc in patterns.items():
        msg += f"• *{name}*: `{desc}`\n"
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN_V2)

# === MAIN FUNCTION ===
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("xp", xp))
    app.add_handler(CommandHandler("learn", learn))
    app.add_handler(CommandHandler("patterns", patterns))

    # Placeholder for rest
    async def placeholder(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🚧 *This feature is coming soon\!*\n\nHang tight for updates 💡",
            parse_mode=ParseMode.MARKDOWN_V2
        )

    for cmd in ["delete", "edit", "test", "train", "badge"]:
        app.add_handler(CommandHandler(cmd, placeholder))

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
