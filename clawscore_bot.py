import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from aiohttp import web

# === LOGGING ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# === ENVIRONMENT VARIABLES ===
TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_HOST = os.environ.get("WEBHOOK_HOST")  # e.g. https://your-app-name.onrender.com
PORT = int(os.environ.get("PORT", 5000))

if not TOKEN or not WEBHOOK_HOST:
    logger.error("❌ Missing BOT_TOKEN or WEBHOOK_HOST in environment variables.")
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
    (4000, "📡 Signal Seeker"),
    (6000, "📐 Technical Adept"),
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
    return f"\n[{ '🟦' * filled }{ '⬜' * (10 - filled) }]"

# === COMMAND HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data.setdefault(user_id, {"xp": 0, "patterns": {}, "badges": []})
    await update.message.reply_text(
        "👋 Welcome to CLAWSCore\n\nUse /help to explore your tools!",
        parse_mode="MarkdownV2"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧰 *CLAWSCore Help Guide*\n\n"
        "📥 /learn - Save a new trading pattern\n"
        "📂 /patterns - View saved patterns\n"
        "📊 /xp - View XP & rank progress\n"
        "🗑️ /delete [name] - Remove a pattern\n"
        "✏️ /edit [name] - Modify a pattern\n"
        "🧪 /test - Quiz yourself with saved patterns\n"
        "🎓 /train - Run a strategy simulation\n"
        "🏅 /badge - View unlocked badges\n\n"
        "More trading magic coming soon ✨",
        parse_mode="MarkdownV2"
    )

async def xp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    xp = user_data.get(user_id, {}).get("xp", 0)
    rank = get_rank(xp)
    next_rank, next_xp = get_next_rank(xp)
    progress = get_progress_bar(xp)

    msg = f"🏆 *Your XP Journey*\n\n"
    msg += f"✨ XP: `{xp}`\n"
    msg += f"🎖️ Rank: *{rank}*\n"
    if next_rank:
        msg += f"📈 Next: *{next_rank}* at `{next_xp}` XP"
    msg += progress

    await update.message.reply_text(msg, parse_mode="MarkdownV2")

async def placeholder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚧 This feature is coming soon!")

# === MAIN ===
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # === Register Handlers ===
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("xp", xp))
    for cmd in ["learn", "patterns", "delete", "edit", "test", "train", "badge"]:
        app.add_handler(CommandHandler(cmd, placeholder))

    # === Web Server ===
    async def index(request):
        return web.Response(text="CLAWSCore Bot is running 🐾")

    app.web_app.add_routes([web.get("/", index)])

    # === Set Webhook on startup ===
    async def on_startup(application):
        await application.bot.set_webhook(WEBHOOK_URL)
        logger.info(f"✅ Webhook set to: {WEBHOOK_URL}")

    app.post_init = on_startup

    logger.info("🚀 Launching CLAWSCore with webhook...")
    await app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_path=WEBHOOK_PATH,
    )

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
