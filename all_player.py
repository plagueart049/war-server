import os
import json
import requests
from datetime import timedelta
from nbtlib import load

PLAYERDATA_PATH = "/workspaces/war-server/world/playerdata"
STATS_PATH = "/workspaces/war-server/world/stats"
WEBHOOK_URL = "https://discord.com/api/webhooks/1394645303100969002/pLlBX-ANyZrZuLthQbrztb6XvwYtPnSAKW8Bjw9swTeFf2n3lfi5zBqVgIbTqY3dzSXL"

uuid_to_name = {
    "38736c3b-f5a0-3d8d-adf2-5e7da600ee35": "Tira_gaming",
    "8f6ca4a6-5cfc-3d98-b85a-9ab2bb8a678b": "seifmonster",
    "ac316219-5b97-3dfe-8fbf-61996940f06e": "ZX12",
    "bea6243b-e6d6-3c4f-87d0-db46dc5207ba": "Plague_Wither049"
}

def format_time(ticks):
    seconds = ticks / 20
    return str(timedelta(seconds=seconds)), seconds

def read_player_inventory(uuid):
    path = os.path.join(PLAYERDATA_PATH, f"{uuid}.dat")
    if not os.path.exists(path):
        return ["⚠️ ملف غير موجود"]

    try:
        nbt_data = load(path)
        inventory = nbt_data["Inventory"]
        items = []
        for item in inventory:
            item_id = item.get("id", "minecraft:unknown")
            count = item.get("Count", 1)
            items.append(f"{item_id} x{count}")
        return items if items else ["- لا يوجد"]
    except Exception as e:
        return [f"⚠️ خطأ في قراءة الإنفنتوري: {e}"]

def read_player_stats(uuid):
    path = os.path.join(STATS_PATH, f"{uuid}.json")
    if not os.path.exists(path):
        return 0, 0, {}, {}
    try:
        with open(path, "r") as f:
            stats = json.load(f)
        playtime = stats["stats"].get("minecraft:custom", {}).get("minecraft:play_time", 0)
        deaths = stats["stats"].get("minecraft:custom", {}).get("minecraft:deaths", 0)
        blocks = stats["stats"].get("minecraft:mined", {})
        mobs = stats["stats"].get("minecraft:killed", {})
        return playtime, deaths, blocks, mobs
    except Exception as e:
        return 0, 0, {}, {}

# تجميع بيانات اللاعبين
players_data = []

if os.path.exists(PLAYERDATA_PATH):
    for filename in os.listdir(PLAYERDATA_PATH):
        if not filename.endswith(".dat"):
            continue
        uuid = filename.replace(".dat", "")
        name = uuid_to_name.get(uuid, "❓ غير معروف")

        inventory = read_player_inventory(uuid)
        playtime_ticks, playtime_sec = read_player_stats(uuid)[0:2]
        playtime_str, playtime_sec = format_time(playtime_ticks)
        deaths, blocks, mobs = read_player_stats(uuid)[1:]

        block_breaks = sum(blocks.values())
        mob_kills = sum(mobs.values())

        players_data.append({
            "uuid": uuid,
            "name": name,
            "inventory": inventory,
            "playtime_str": playtime_str,
            "playtime_sec": playtime_sec,
            "deaths": deaths,
            "blocks": blocks,
            "mobs": mobs,
            "block_breaks": block_breaks,
            "mob_kills": mob_kills
        })

# 🔢 ترتيب اللاعبين حسب وقت اللعب
players_data.sort(key=lambda p: p["playtime_sec"], reverse=True)

# 🔎 جدول ملخص
report = "**📊 ملخص اللاعبين:**\n"
report += "| 👤 اللاعب | ⏱️ وقت اللعب | 💀 الموتات | ⛏️ البلوكات | ⚔️ القتلات |\n"
report += "|-----------|---------------|------------|-------------|-------------|\n"
for p in players_data:
    report += f"| {p['name']} | {p['playtime_str']} | {p['deaths']} | {p['block_breaks']} | {p['mob_kills']} |\n"

# 🔎 تفاصيل كل لاعب
for p in players_data:
    report += f"\n--- 👤 اللاعب: {p['name']} ({p['uuid']}) ---\n"
    report += "🎒 الإنفنتوري:\n - " + "\n - ".join(p['inventory']) + "\n"
    report += f"⏱️ وقت اللعب: {p['playtime_str']}\n"
    report += f"💀 عدد مرات الموت: {p['deaths']}\n"

    if p['blocks']:
        report += "⛏️ البلوكات التي كُسرت:\n"
        for block, count in p['blocks'].items():
            report += f" - {block.split(':')[-1]}: {count}\n"
    else:
        report += "⛏️ البلوكات التي كُسرت: لا توجد بيانات.\n"

    if p['mobs']:
        report += "⚔️ الكائنات التي قُتلت:\n"
        for mob, count in p['mobs'].items():
            report += f" - {mob.split(':')[-1]}: {count}\n"
    else:
        report += "⚔️ الكائنات التي قُتلت: لا توجد بيانات.\n"

# إرسال التقرير إلى ديسكورد
MAX_DISCORD_LENGTH = 1900
if len(report) > MAX_DISCORD_LENGTH:
    with open("players_report.txt", "w", encoding="utf-8") as f:
        f.write(report)

    with open("players_report.txt", "rb") as f:
        files = {'file': ("players_report.txt", f)}
        payload = { "content": "📋 تقرير اللاعبين:" }
        response = requests.post(WEBHOOK_URL, data=payload, files=files)
else:
    payload = { "content": f"📋 تقرير اللاعبين:\n{report}" }
    response = requests.post(WEBHOOK_URL, json=payload)

try:
    response.raise_for_status()
    print("✅ تم إرسال التقرير إلى Discord.")
except Exception as e:
    print(f"❌ فشل في الإرسال: {e}")
