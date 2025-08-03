# CLAWSCore Bot (Phase 1 - Phase 3 Part 2 Complete)

```python
import os
import json
from flask import Flask, request
import random

app = Flask(__name__)

# === Data Storage ===
XP_FILE = "xp_data.json"
PATTERN_FILE = "pattern_bank.json"

# Load XP and pattern memory
if os.path.exists(XP_FILE):
    with open(XP_FILE, "r") as f:
        xp_data = json.load(f)
else:
    xp_data = {}

if os.path.exists(PATTERN_FILE):
    with open(PATTERN_FILE, "r") as f:
        pattern_memory = json.load(f)
else:
    pattern_memory = {}

# === Rank System ===
def get_rank(xp):
    if xp >= 20000:
        return "🧟‍♂️ Profit Reaper"
    elif xp >= 15000:
        return "🌀 Void Tactician"
    elif xp >= 10000:
        return "🧠 Neural Strategist"
    elif xp >= 6000:
        return "🛰️ Orbital Operative"
    elif xp >= 3000:
        return "🎯 Market Seeker"
    elif xp >= 1000:
        return "📡 Signal Adept"
    elif xp >= 500:
        return "📈 Chart Whisperer"
    elif xp >= 100:
        return "🧪 Pattern Novice"
    else:
        return "🕹️ New Recruit"

# === XP Engine ===
def add_xp(user_id, amount):
    current_xp = xp_data.get(user_id, 0)
    new_xp = current_xp + amount
    xp_data[user_id] = new_xp
    save_xp()
    return new_xp

def save_xp():
    with open(XP_FILE, "w") as f:
        json.dump(xp_data, f)

# === Pattern Engine ===
def save_pattern(user_id, name, strategy):
    if user_id not in pattern_memory:
        pattern_memory[user_id] = {}
    pattern_memory[user_id][name] = strategy
    with open(PATTERN_FILE, "w") as f:
        json.dump(pattern_memory, f)

def delete_pattern(user_id, name):
    if user_id in pattern_memory and name in pattern_memory[user_id]:
        del pattern_memory[user_id][name]
        with open(PATTERN_FILE, "w") as f:
            json.dump(pattern_memory, f)
        return True
    return False

# === Bot Logic ===
@app.route("/bot", methods=["POST"])
def bot():
    data = request.json
    user_id = str(data["user_id"])
    message = data["message"].strip()

    # Commands
    if message.lower().startswith("/xp"):
        xp = xp_data.get(user_id, 0)
        rank = get_rank(xp)
        return {"reply": f"You have {xp} XP\nRank: {rank}"}

    elif message.lower().startswith("/train"):
        try:
            _, name, strategy = message.split("|", 2)
            save_pattern(user_id, name.strip(), strategy.strip())
            add_xp(user_id, 70)
            return {"reply": f"✅ Pattern '{name.strip()}' saved. (+70 XP)"}
        except:
            return {"reply": "❌ Usage: /train | pattern_name | strategy_description"}

    elif message.lower().startswith("/memory"):
        patterns = pattern_memory.get(user_id, {})
        if not patterns:
            return {"reply": "🧠 You have no saved patterns."}
        reply = "🧠 Your Saved Patterns:\n"
        for name, strat in patterns.items():
            reply += f"\n📌 {name} — {strat}"
        return {"reply": reply}

    elif message.lower().startswith("/forget"):
        try:
            _, name = message.split(" ", 1)
            success = delete_pattern(user_id, name.strip())
            if success:
                return {"reply": f"🗑️ Pattern '{name.strip()}' deleted."}
            else:
                return {"reply": "❌ Pattern not found."}
        except:
            return {"reply": "❌ Usage: /forget pattern_name"}

    elif message.lower().startswith("/test"):
        try:
            _, name = message.split(" ", 1)
            strat = pattern_memory.get(user_id, {}).get(name.strip())
            if strat:
                add_xp(user_id, 40)
                return {"reply": f"🧪 Testing pattern '{name.strip()}':\n{strat}\n(+40 XP)"}
            else:
                return {"reply": "❌ Pattern not found."}
        except:
            return {"reply": "❌ Usage: /test pattern_name"}

    return {"reply": "🤖 CLAWSCore is online. Use /xp, /train, /memory, /test, or /forget"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
```

---
 
