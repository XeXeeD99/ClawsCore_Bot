# claws_bot.py

import os
import asyncio
from aiohttp import web
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# In-memory user data
users = {}

# XP rank tiers
ranks = [
    (0, "🧠 Beginner Mind"),
    (500, "🎯 Focused Learner"),
    (1000, "🖠 Strategy Sculptor"),
    (2000, "📈 Signal Seeker"),
    (4000, "🧬 Logic Alchemist"),
    (6000, "🚀 Market Specialist"),
    (10000, "🧠 Neural Analyst"),
    (15000, "🔮 Visionary Trader"),
    (20000, "💀 Profit Reaper"),
    (30000, "🌌 CLAWSCore Elite"),
]

badges = {
    5: "🎓 First 5 Patterns",
    10: "📘 Tactical Archivist",
    20: "🧠 Memory Hoarder",
}

# --------- UTILITIES --------- #

def get_user_data(user_id):
    if user_id not in users:
        users[user_id] = {
            "xp": 0,
            "patterns": {},
            "badges": [],
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
    filled = int((xp / total) * 10)
    bar = "🟩" * filled + "⬛" * (10 - filled)
    return f"{bar} {xp}/{total} XP"

def check_badges(user_id):
    user = get_user_data(user_id)
    unlocked = []
    count = len(user["patterns"])
    for num, badge in badges.items():
        if count >= num and badge not in user["badges"]:
            user["badges"].append(badge)
            unlocked.append(badge)
    return unlocked

# --------- COMMANDS --------- #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to <b>CLAWSCore 🧠</b> — Your Trading Pattern Memory System.\nUse /help to see commands.",
        parse_mode="HTML"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
<b>📘 CLAWSCore Commands</b>
/learn [name] | [strategy] — Learn & save a pattern (+100 XP)
/edit [name] | [new strategy] — Edit a saved pattern
/delete [name] — Delete a saved pattern
/patterns — List all your patterns
/xp — View XP, rank & progress
/badge — See unlocked badges
/help — Show this help message
""", parse_mode="HTML")

async def learn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        content = update.message.text.split(" ", 1)[1]
        name, strategy = map(str.strip, content.split("|", 1))
        user = get_user_data(update.effective_user.id)
        user["patterns"][name] = strategy
        user["xp"] += 100
        new_badges = check_badges(update.effective_user.id)
        badge_text = f"<br><br>🎖 <b>New Badges:</b> {', '.join(new_badges)}" if new_badges else ""
        await update.message.reply_text(
            f"📌 <b>Learned pattern:</b> {name}<br>➕ +100 XP!<br>{generate_progress_bar(user['xp'])}<br>🏅 <b>Rank:</b> {get_rank(user['xp'])}{badge_text}",
            parse_mode="HTML"
        )
    except:
        await update.message.reply_text("Usage: /learn name | strategy")

async def patterns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user_data(update.effective_user.id)
    if not user["patterns"]:
        await update.message.reply_text("You haven't saved any patterns yet.")
        return
    msg = "<br>".join([f"• <b>{k}</b>: {v}" for k, v in user["patterns"].items()])
    await update.message.reply_text(f"🧠 <b>Your Patterns:</b><br>{msg}", parse_mode="HTML")

async def edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        content = update.message.text.split(" ", 1)[1]
        name, new_strategy = map(str.strip, content.split("|", 1))
        user = get_user_data(update.effective_user.id)
        if name in user["patterns"]:
            user["patterns"][name] = new_strategy
            await update.message.reply_text(f"✅ <b>Updated pattern:</b> {name}", parse_mode="HTML")
        else:
            await update.message.reply_text("Pattern not found.")
    except:
        await update.message.reply_text("Usage: /edit name | new strategy")

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        name = update.message.text.split(" ", 1)[1].strip()
        user = get_user_data(update.effective_user.id)
        if name in user["patterns"]:
            del user["patterns"][name]
            await update.message.reply_text(f"🗑 <b>Deleted pattern:</b> {name}", parse_mode="HTML")
        else:
            await update.message.reply_text("Pattern not found.")
    except:
        await update.message.reply_text("Usage: /delete name")

async def xp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user_data(update.effective_user.id)
    rank = get_rank(user["xp"])
    progress = generate_progress_bar(user["xp"])
    await update.message.reply_text(
        f"🏅 <b>Your Rank:</b> {rank}<br>{progress}",
        parse_mode="HTML"
    )

async def badge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user_data(update.effective_user.id)
    if not user["badges"]:
        await update.message.reply_text("You haven't unlocked any badges yet.")
    else:
        await update.message.reply_text(
            f"🎖 <b>Badges:</b> {', '.join(user['badges'])}",
            parse_mode="HTML"
        )

# --------- MAIN APP --------- #

async def main():
    token = os.environ["BOT_TOKEN"]
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("learn", learn))
    app.add_handler(CommandHandler("patterns", patterns))
    app.add_handler(CommandHandler("edit", edit))
    app.add_handler(CommandHandler("delete", delete))
    app.add_handler(CommandHandler("xp", xp))
    app.add_handler(CommandHandler("badge", badge))

    async def handler(request):
        data = await request.json()
        await app.update_queue.put(Update.de_json(data, app.bot))
        return web.Response(text="ok")

    webhook_app = web.Application()
    webhook_app.add_routes([web.post("/", handler)])
    await app.initialize()
    await app.start()
    await app.bot.set_webhook(os.environ["WEBHOOK_URL"])
    runner = web.AppRunner(webhook_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 8080)))
    await site.start()
    print("CLAWSCore is live.")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
