import json
import os

# 📂 Path to the XP data file
XP_FILE = "memory_bank/xp_data.json"

# ✅ Ensure the memory_bank folder exists
os.makedirs("memory_bank", exist_ok=True)

# 🧠 Load XP data from file
def load_xp_data():
    if not os.path.exists(XP_FILE):
        return {}
    with open(XP_FILE, "r") as f:
        return json.load(f)

# 💾 Save XP data to file
def save_xp_data(data):
    with open(XP_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ➕ Add XP to a user
def add_xp(user_id, amount):
    data = load_xp_data()
    user_id = str(user_id)
    data[user_id] = data.get(user_id, 0) + amount
    save_xp_data(data)
    return data[user_id]

# 📊 Get user's current XP
def get_xp(user_id):
    data = load_xp_data()
    return data.get(str(user_id), 0)