import os
import random
import requests
from datetime import datetime

# -------------------------- 你的规则配置 --------------------------
DAY_MIN = 15000
DAY_MAX = 30000
BASE_MIN = 1000
BASE_MAX = 2500
ADD_MIN = 1000
ADD_MAX = 3000
RUN_START = 9
RUN_END = 23
# -------------------------------------------------------------------

def get_time_multiplier():
    hour = datetime.now().hour
    if 9 <= hour < 12:
        return 0.6
    elif 12 <= hour < 18:
        return 1.2
    elif 18 <= hour < 23:
        return 0.8
    return 0.5

def login_zepp(account, password):
    url = "https://api-cn.huami.com/v2/auth/login"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 13; MIUI 14.0)",
        "Accept-Encoding": "gzip"
    }
    data = {
        "country_code": "CN",
        "account": account,
        "password": password,
        "grant_type": "password",
        "client_id": "com.huami.mifit",
        "device_id": "robot_" + str(random.randint(100000, 999999)),
        "app_name": "com.huami.mifit",
        "password_type": "plaintext"
    }
    res = requests.post(url, headers=headers, data=data, timeout=30)
    res.raise_for_status()
    return res.json()

def sync_steps(access_token, steps):
    url = "https://api-mifit-cn.huami.com/v1/user/sync"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    today = datetime.now().strftime("%Y-%m-%d")
    data = {
        "date": today,
        "steps": steps,
        "calories": round(steps * 0.04, 1),
        "distance": round(steps * 0.0008, 2),
        "activeSeconds": steps * 1
    }
    res = requests.post(url, headers=headers, json=data, timeout=30)
    res.raise_for_status()
    return True

def main():
    account = os.getenv("ACCOUNT")
    password = os.getenv("PASSWORD")
    if not account or not password:
        print("❌ ACCOUNT 或 PASSWORD 未配置")
        return

    today_target = random.randint(DAY_MIN, DAY_MAX)
    steps_file = "/tmp/today_steps.txt"
    try:
        with open(steps_file, "r") as f:
            current_steps = int(f.read().strip())
    except:
        current_steps = 0

    if current_steps >= today_target:
        print("✅ 已达今日上限，无需继续")
        return

    multiplier = get_time_multiplier()
    increment = int((random.randint(BASE_MIN, BASE_MAX) + random.randint(ADD_MIN, ADD_MAX)) * multiplier)
    new_total = min(current_steps + increment, today_target)

    try:
        login_info = login_zepp(account, password)
        access_token = login_info["access_token"]
        sync_steps(access_token, new_total)
        with open(steps_file, "w") as f:
            f.write(str(new_total))
        print(f"✅ 同步成功！本次+{increment}步，当前累计：{new_total}/{today_target}")
    except Exception as e:
        print(f"❌ 运行失败：{e}")

if __name__ == "__main__":
    main()
