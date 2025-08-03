import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Memory Bank to store trading patterns
trading_patterns = {}

# XP system
user_data = {}

# Rank thresholds
ranks = [
    (0, "Rookie 🐣"),
    (300, "Observer 👀"),
    (700, "Trainee Trader 💼"),
    (1200, "Analyst 📊"),
    (1800, "Pattern Scout 🧠"),
    (2500, "Strategist ♟️"),
    (3500, "Risk Handler ⚖️"),
    (4800, "Sniper 🎯"),
    (6000, "Momentum Rider 🚀"),
    (7500, "Signal Master 📡"),
    (9000, "Shadow Trader 👤"),
    (11000, "Chart Phantom 👻"),
    (13000, "Volatility Viper 🐍"),
    (15000, "Risk Taker ⚠️"),
    (17500, "Execution Ace 🧨"),
    (20000, "Profit Reaper ☠️")
]

def get_rank(xp):
    for i in range(len(ranks) - 1, -1, -1):
        if xp >= ranks[i][0]:
            return ranks[i][1]
    return ranks[0][1]

def progress_bar(xp):
    current_rank = None
    next_rank = None
    for i in range(len(ranks) - 1):
        if ranks[i][0] <= xp < ranks[i + 1][0]:
            current_rank = ranks[i]
            next_rank = ranks[i + 1]
            break
    if xp >= ranks[-1][0]:
        return "🟩" * 20 + f"  (MAX)"
    if current_rank and next_rank:
        progress = int(20 * (xp - current_rank[0]) / (next_rank[0] - current_rank[0]))
        return "🟩" * progress + "⬜" * (20 - progress) + f"  ({xp}/{next_rank[0]} XP)"
    return "⬜" * 20 + f"  ({xp} XP)"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to CLAWSCore Bot — your AI trading apprentice.\n\nUse /help to see what I can do."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📘 *CLAWSCore Commands*\n\n"
        "/learn [pattern] - Teach a trading pattern\n"
        "/patterns - List saved patterns\n"
        "/delete [pattern name] - Delete a pattern\n"
        "/edit [old] [new] - Edit a pattern\n"
        "/xp - View your XP, rank, and progress\n"
        "/profile - See your CLAWSCore status\n"
        "/rank - Show your current rank\n"
        "\nMore coming soon. Type smart, rank up faster."
    )

async def learn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("❌ Please provide a pattern to learn.")
        return
    user_data.setdefault(user_id, {"xp": 0, "patterns": {}})
    user_data[user_id]["patterns"][text] = True
    user_data[user_id]["xp"] += 70  # +70 XP per learning
    rank = get_rank(user_data[user_id]["xp"])
    await update.message.reply_text(
        f"✅ Pattern learned!\n+70 XP gained.\n\nCurrent Rank: *{rank}*\n{progress_bar(user_data[user_id]['xp'])}"
    )

async def patterns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    patterns = user_data.get(user_id, {}).get("patterns", {})
    if not patterns:
        await update.message.reply_text("📭 No patterns learned yet.")
    else:
        await update.message.reply_text("📚 *Your Trading Patterns:*\n\n" + "\n".join(patterns.keys()))

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    name = " ".join(context.args)
    if name in user_data.get(user_id, {}).get("patterns", {}):
        del user_data[user_id]["patterns"][name]
        await update.message.reply_text(f"🗑️ Deleted pattern: {name}")
    else:
        await update.message.reply_text("❌ Pattern not found.")

async def edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("❌ Usage: /edit [old name] [new name]")
        return
    old = args[0]
    new = " ".join(args[1:])
    if old in user_data.get(user_id, {}).get("patterns", {}):
        del user_data[user_id]["patterns"][old]
        user_data[user_id]["patterns"][new] = True
        await update.message.reply_text(f"✏️ Renamed pattern '{old}' to '{new}'")
    else:
        await update.message.reply_text("❌ Pattern not found.")

async def xp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    xp = user_data.get(user_id, {}).get("xp", 0)
    rank = get_rank(xp)
    await update.message.reply_text(
        f"🏅 *XP:* {xp}\n*Rank:* {rank}\n{progress_bar(xp)}"
    )

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    xp = user_data.get(user_id, {}).get("xp", 0)
    rank = get_rank(xp)
    count = len(user_data.get(user_id, {}).get("patterns", {}))
    await update.message.reply_text(
        f"👤 *CLAWSCore Profile*\n\n"
        f"*XP:* {xp}\n"
        f"*Rank:* {rank}\n"
        f"*Patterns Learned:* {count}\n"
        f"{progress_bar(xp)}"
    )

async def rank_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    xp = user_data.get(user_id, {}).get("xp", 0)
    current_rank = get_rank(xp)
    await update.message.reply_text(f"🔰 Your current rank is: *{current_rank}*\n{progress_bar(xp)}")

def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token("8329675796:AAHEGO7MokUPI1FmqevdCl56tuceVMawxyY").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("learn", learn))
    app.add_handler(CommandHandler("patterns", patterns))
    app.add_handler(CommandHandler("delete", delete))
    app.add_handler(CommandHandler("edit", edit))
    app.add_handler(CommandHandler("xp", xp))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("rank", rank_command))

    app.run_polling()

if __name__ == '__main__':
    main()

