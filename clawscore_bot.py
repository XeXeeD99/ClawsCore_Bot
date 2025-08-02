import os
import json
import logging
from flask import Flask, request
import telegram
from telegram.ext import Dispatcher, CommandHandler

TOKEN = os.environ.get("BOT_TOKEN")
XP_FILE = "xp_data.json"
PORT = int(os.environ.get("PORT", 5000))

bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)

# 📊 Rank system
RANKS = [
    (0, "📄 Trainee"),
    (100, "🧠 Novice Strategist"),
    (300, "🔎 Chart Analyst"),
    (700, "📈 Technical Reader"),
    (1300, "🎯 Signal Seeker"),
    (2500, "⚔️ Tactical Trader"),
    (5000, "💼 Position Planner"),
    (8000, "👁️‍🗨️ Market Phantom"),
    (13000, "🧬 Risk Architect"),
    (20000, "💀 Profit Reaper"),
]

def load_xp():
    if not os.path.exists(XP_FILE):
        return {}
    with open(XP_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_xp(data):
    with open(XP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_rank(xp):
    current_rank = RANKS[0][1]
    for threshold, rank in RANKS:
        if xp >= threshold:
            current_rank = rank
        else:
            break
    return current_rank

# 🧠 /xp command
def xp_command(update, context):
    user_id = str(update.effective_user.id)
    xp_data = load_xp()
    xp = xp_data.get(user_id, 0)
    rank = get_rank(xp)
    update.message.reply_text(f"🧠 Your XP: {xp}\n🏅 Rank: {rank}")

# 🚫 Remove XP from regular messages for now
# def handle_message(update, context):
#     ...

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

@app.route("/", methods=["GET"])
def home():
    return "🤖 ClawsCore Bot Running!"

# 🧰 Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# 🧠 Command setup
dispatcher = Dispatcher(bot, None, use_context=True)
dispatcher.add_handler(CommandHandler("xp", xp_command))
# dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
