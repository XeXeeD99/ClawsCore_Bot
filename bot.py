import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Logging
logging.basicConfig(level=logging.INFO)

# In-memory database
users = {}
strategies = {}

# Ranks
ranks = [
    (0, "Recruit 🟢"),
    (500, "Tactician ⚔️"),
    (1500, "Sniper 🎯"),
    (3000, "Shadow Broker 🕵️"),
    (5000, "Assassin 🗡️"),
    (10000, "Profit Reaper 💰"),
    (15000, "Core Master 1 🧠"),
    (20000, "Core Master 2 🔥")
]

# Get rank from XP
def get_rank(xp):
    for required, name in reversed(ranks):
        if xp >= required:
            return name
    return "Recruit 🟢"

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in users:
        users[user_id] = {"xp": 0}
    xp = users[user_id]["xp"]
    rank = get_rank(xp)
    await update.message.reply_text(f"👋 Welcome to ClawsCore_Bot!\n\nXP: {xp}\nRank: {rank}")

# Learn a strategy
async def learn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /learn <strategy_name>")
        return
    strategy_name = context.args[0]
    await update.message.reply_text(f"🧠 Type out the full strategy for '{strategy_name}' now:")

    # Wait for next message
    message = await context.bot.wait_for_message(chat_id=update.effective_chat.id, from_user=update.effective_user)
    if not message:
        return
    strategy_text = message.text
    strategies[strategy_name] = strategy_text
    await update.message.reply_text(f"✅ Strategy '{strategy_name}' saved!")

# Simulate a trade
async def simulate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /simulate <strategy_name>")
        return
    strategy_name = context.args[0]
    if strategy_name not in strategies:
        await update.message.reply_text(f"❌ Strategy '{strategy_name}' not found.")
        return
    text = strategies[strategy_name]
    await update.message.reply_text(f"📊 Simulating trade with '{strategy_name}'...\n\n{text}\n\n🧪 Trade simulated (demo mode).")

# Train a strategy (gain XP)
async def train(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in users:
        users[user_id] = {"xp": 0}
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /train <strategy_name>")
        return
    strategy_name = context.args[0]
    if strategy_name not in strategies:
        await update.message.reply_text("❌ Strategy not found.")
        return
    users[user_id]["xp"] += 70
    xp = users[user_id]["xp"]
    rank = get_rank(xp)
    await update.message.reply_text(f"💪 Trained with '{strategy_name}'\n+70 XP\nTotal XP: {xp}\nNew Rank: {rank}")

# Run the bot
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("learn", learn))
    app.add_handler(CommandHandler("simulate", simulate))
    app.add_handler(CommandHandler("train", train))

    print("🤖 ClawsCore_Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
