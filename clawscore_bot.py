import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# In-memory user data
users = {}

# XP rank tiers
ranks = [
    (0, "🧠 Beginner Mind"),
    (500, "🎯 Focused Learner"),
    (1000, "𔙠 Strategy Sculptor"),
    (2000, "📈 Signal Seeker"),
    (4000, "🧬 Logic Alchemist"),
    (6000, "🚀 Market Specialist"),
    (10000, "🧠 Neural Analyst"),
    (15000, "🔮 Visionary Trader"),
    (20000, "💀 Profit Reaper"),
    (30000, "🌌 CLAWSCore Elite"),
]

# Badge milestones
badges = {
    500: "📚 Apprentice Analyst",
    3000: "⚔️ Strategy Wielder",
    7000: "🔮 Chart Whisperer",
    10000: "🧪 Tactical Alchemist",
    15000: "🧠 Memory Hoarder",
    20000: "💸 Profit Reaper",
    50000: "🧠 Pattern Sage",
    100000: "👑 CLAWS Mastermind",
}

# ---------- UTILITIES ----------

def get_user_data(user_id):
    if user_id not in users:
        users[user_id] = {
            "xp": 0,
            "patterns": {},
            "badges": [],
            "brain_on": False
        }
    return users[user_id]

def get_rank(xp):
    current_rank = ranks[0][1]
    for threshold, rank in ranks:
        if xp >= threshold:
            current_rank = rank
    return current_rank

def get_next_xp_target(xp):
    for threshold, _ in ranks:
        if xp < threshold:
            return threshold
    return ranks[-1][0]

def generate_progress_bar(xp):
    total = get_next_xp_target(xp)
    filled = min(int((xp / total) * 10), 10)
    bar = "🟩" * filled + "⬛" * (10 - filled)
    return f"{bar} {xp}/{total} XP"

def check_badges(user_id):
    user = get_user_data(user_id)
    unlocked = []
    current_xp = user["xp"]
    for xp_req, badge_name in sorted(badges.items()):
        if current_xp >= xp_req and badge_name not in user["badges"]:
            user["badges"].append(badge_name)
            unlocked.append(badge_name)
    return unlocked

# ---------- MIXTRAL PLACEHOLDER ----------

async def ask_mixtral(prompt: str):
    return f"🤖 [Mixtral AI Brain Responds]:\n{prompt}"

# ---------- COMMANDS ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 <b>Welcome to CLAWSCore 🧠</b>\n\n"
        "Your Tactical Memory Bank for Trading Patterns!\n\n"
        "Use /help to open your toolbox 🧰",
        parse_mode="HTML"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "<b>🧰 CLAWSCore Command Menu</b>\n\n"
        "📚 /learn <i>name | strategy</i> — Save a new pattern (+100 XP)\n"
        "✏️ /edit <i>name | new strategy</i> — Update an existing pattern\n"
        "🗑️ /delete <i>name</i> — Delete a pattern\n\n"
        "📖 /patterns — Show all your saved patterns\n"
        "📊 /xp — View rank & XP progress\n"
        "🧪 /profile — View full stats: XP, rank, patterns & badges\n"
        "🎖️ /badge — View unlocked badges\n"
        "🌟 /achievements — All possible ranks & badges\n\n"
        "🧠 /brainon — Enable AI Brain\n"
        "🧠 /brainoff — Disable AI Brain\n"
        "🤐 /help — This magical menu again",
        parse_mode="HTML"
    )

async def brainon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user_data(update.effective_user.id)
    user["brain_on"] = True
    await update.message.reply_text("🧠 CLAWSCore Brain is now ON. Mixtral AI is thinking with you.")

async def brainoff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user_data(update.effective_user.id)
    user["brain_on"] = False
    await update.message.reply_text("🧠 Brain is OFF. Back to default core logic.")

async def learn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        content = update.message.text.split(" ", 1)[1]
        name, strategy = map(str.strip, content.split("|", 1))
        user = get_user_data(update.effective_user.id)
        user["patterns"][name] = strategy
        user["xp"] += 100
        new_badges = check_badges(update.effective_user.id)
        badge_text = f"\n🎖 <b>New Badge Unlocked:</b> {', '.join(new_badges)}" if new_badges else ""
        await update.message.reply_text(
            f"✅ <b>Pattern Saved:</b> {name}\n"
            f"➕ +100 XP!\n"
            f"{generate_progress_bar(user['xp'])}\n\n"
            f"🏅 <b>Rank:</b> {get_rank(user['xp'])}{badge_text}",
            parse_mode="HTML"
        )
    except:
        await update.message.reply_text("❌ Usage: /learn name | strategy")

async def patterns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user_data(update.effective_user.id)
    if not user["patterns"]:
        await update.message.reply_text("🛌 You haven't saved any patterns yet. Use /learn to get started!")
    else:
        msg = "\n\n".join([f"🔹 <b>{k}</b>: {v}" for k, v in user["patterns"].items()])
        await update.message.reply_text(f"📖 <b>Your Pattern Vault:</b>\n\n{msg}", parse_mode="HTML")

async def edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        content = update.message.text.split(" ", 1)[1]
        name, new_strategy = map(str.strip, content.split("|", 1))
        user = get_user_data(update.effective_user.id)
        if name in user["patterns"]:
            user["patterns"][name] = new_strategy
            await update.message.reply_text(f"✏️ <b>Updated pattern:</b> {name}", parse_mode="HTML")
        else:
            await update.message.reply_text("❌ Pattern not found.")
    except:
        await update.message.reply_text("❌ Usage: /edit name | new strategy")

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        name = update.message.text.split(" ", 1)[1].strip()
        user = get_user_data(update.effective_user.id)
        if name in user["patterns"]:
            del user["patterns"][name]
            await update.message.reply_text(f"🗑️ <b>Deleted pattern:</b> {name}", parse_mode="HTML")
        else:
            await update.message.reply_text("❌ Pattern not found.")
    except:
        await update.message.reply_text("❌ Usage: /delete name")

async def xp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user_data(update.effective_user.id)
    rank = get_rank(user["xp"])
    progress = generate_progress_bar(user["xp"])
    await update.message.reply_text(
        f"📊 <b>Progress Overview</b>\n\n"
        f"🏅 <b>Rank:</b> {rank}\n"
        f"{progress}",
        parse_mode="HTML"
    )

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user_data(update.effective_user.id)
    xp = user["xp"]
    rank = get_rank(xp)
    progress = generate_progress_bar(xp)
    badge_count = len(user["badges"])
    pattern_count = len(user["patterns"])
    badge_list = ", ".join(user["badges"]) if user["badges"] else "None yet 😅"

    await update.message.reply_text(
        f"🧪 <b>Your CLAWSCore Profile</b>\n\n"
        f"🧠 <b>XP:</b> {xp}\n"
        f"🏅 <b>Rank:</b> {rank}\n"
        f"{progress}\n\n"
        f"📚 <b>Patterns Learned:</b> {pattern_count}\n"
        f"🎖 <b>Badges:</b> {badge_count} ({badge_list})",
        parse_mode="HTML"
    )

async def badge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user_data(update.effective_user.id)
    if not user["badges"]:
        await update.message.reply_text("😅 You haven't unlocked any badges yet.")
    else:
        await update.message.reply_text(
            f"🎖 <b>Your Badges:</b> {', '.join(user['badges'])}",
            parse_mode="HTML"
        )

async def achievements(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rank_list = "\n".join([f"{emoji} — <i>{xp} XP+</i>" for xp, emoji in ranks])
    badge_list = "\n".join([f"{v} — <i>{k} XP+</i>" for k, v in sorted(badges.items())])
    await update.message.reply_text(
        f"<b>🌟 All Ranks & Badges</b>\n\n"
        f"<b>🏅 Ranks:</b>\n{rank_list}\n\n"
        f"<b>🎖 Badges:</b>\n{badge_list}",
        parse_mode="HTML"
    )

# ---------- MESSAGE HANDLER ----------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user_data(update.effective_user.id)
    text = update.message.text

    if user.get("brain_on"):
        response = await ask_mixtral(text)
    else:
        response = "🧠 Brain is OFF. Use /brainon to enable AI."

    await update.message.reply_text(response)

# ---------- MAIN ----------

def main():
    token = os.environ["BOT_TOKEN"]
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("learn", learn))
    app.add_handler(CommandHandler("edit", edit))
    app.add_handler(CommandHandler("delete", delete))
    app.add_handler(CommandHandler("patterns", patterns))
    app.add_handler(CommandHandler("xp", xp))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("badge", badge))
    app.add_handler(CommandHandler("achievements", achievements))
    app.add_handler(CommandHandler("brainon", brainon))
    app.add_handler(CommandHandler("brainoff", brainoff))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ CLAWSCore is running (polling mode)")
    app.run_polling()

if __name__ == "__main__":
    main()
