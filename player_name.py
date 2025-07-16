import json
import os

# المسارات (تم تعديلها لتتوافق مع مجلد المشروع الجديد)
USERCACHE_PATH = "/workspaces/war-server/usercache.json"
PLAYERDATA_PATH = "/workspaces/war-server/world/playerdata"

# تحميل usercache.json
with open(USERCACHE_PATH, "r") as f:
    usercache = json.load(f)

# جلب كل ملفات .dat
playerdata_files = set(f.replace(".dat", "") for f in os.listdir(PLAYERDATA_PATH) if f.endswith(".dat"))

# تحليل البيانات
print("📋 تقرير اللاعبين:\n")

for entry in usercache:
    name = entry["name"]
    uuid = entry["uuid"]

    if uuid in playerdata_files:
        print(f"✅ {name:<15} ↔️ {uuid} ← 🟢 لديه ملف بيانات")
    else:
        print(f"❌ {name:<15} ↔️ {uuid} ← 🔴 لا يملك ملف بيانات (ربما حُذف أو لم يدخل العالم)")

# لاعبين لديهم ملفات .dat لكن غير مذكورين في usercache
print("\n🕵️‍♂️ UUIDات بدون أسماء في usercache:")

unknown_uuids = playerdata_files - {entry["uuid"] for entry in usercache}
for uuid in unknown_uuids:
    print(f"🔘 {uuid} ← ❓ الاسم غير معروف (قد يكون قديم أو مكرك)")
