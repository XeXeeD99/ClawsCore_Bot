from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging

# 🚨 Bot Token (Keep this private in production!)
TOKEN = "8329675796:AAHEGO7MokUPI1FmqevdCl56tuceVMawxyY"

# ✅ Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# 🧠 Command handler: /start
def start(update, context):
    update.message.reply_text("🤖 CLAWSCore activated. I'm ready to learn and trade, Commander!")

# 📥 Message handler: learns text
def handle_message(update, context):
    user_message = update.message.text
    update.message.reply_text(f"🧠 Learned: \"{user_message}\" (but my memory isn't saved yet 😉)")

# 🔁 Error handler
def error(update, context):
    logger.warning(f'Update {update} caused error {context.error}')

# 🔄 Main bot loop
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()            return name
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
