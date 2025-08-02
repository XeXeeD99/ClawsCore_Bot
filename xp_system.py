import json
import os
import random

XP_FILE = "memory_bank/xp_data.json"
os.makedirs("memory_bank", exist_ok=True)

def load_xp_data():
    if not os.path.exists(XP_FILE):
        return {}
    with open(XP_FILE, "r") as f:
        return json.load(f)

def save_xp_data(data):
    with open(XP_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_xp(user_id, amount):
    data = load_xp_data()
    user_id = str(user_id)
    data[user_id] = data.get(user_id, 0) + amount
    save_xp_data(data)
    return data[user_id]

def get_xp(user_id):
    data = load_xp_data()
    return data.get(str(user_id), 0)

def add_random_msg_xp(user_id):
    xp = random.randint(1, 5)
    return add_xp(user_id, xp)

def add_pattern_test_xp(user_id):
    return add_xp(user_id, 20)

def add_pattern_learn_xp(user_id):
    return add_xp(user_id, 20)

def add_sniper_confirmed_xp(user_id):
    return add_xp(user_id, 70)

def deduct_sniper_miss_xp(user_id):
    return add_xp(user_id, -40)
