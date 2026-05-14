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
    """原项目可用的 Zepp 登录接口"""
    url = "https://api.huami.com/v2/auth/login"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36"
    }
    data = {
        "country_code": "CN",
        "account": account,
        "password": password,
        "grant_type": "password",
        "client_id": "Amazfit",
        "device_id": "zepp_robot_" + str(random.randint(100000, 999999))
    }
    res = requests.post(url, headers=headers, data=data)
    res.raise_for_status()
    return res.json()

def sync_steps(access_token, steps):
    """原项目可用的 Zepp 步数同步接口"""
    url = "https://api-mifit.huami.com/v1/user/sync"
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
    res = requests.post(url, headers=headers, json=data)
    res.raise_for_status()
    return True

def main():
    # 从 Secrets 读取账号密码
    account = os.getenv("ACCOUNT")
    password = os.getenv("PASSWORD")
    if not account or not password:
        print("❌ 错误：ACCOUNT 或 PASSWORD 未配置")
        return

    # 今日目标步数（随机生成）
    today_target = random.randint(DAY_MIN, DAY_MAX)
    print(f"✅ 今日目标步数：{today_target}")

    # 读取/初始化累计步数
    steps_file = "/tmp/today_steps.txt"
    try:
        with open(steps_file, "r") as f:
            current_steps = int(f.read().strip())
    except (FileNotFoundError, ValueError):
        current_steps = 0

    if current_steps >= today_target:
        print("🛑 已达今日上限，无需继续")
        return

    # 计算本次增量
    multiplier = get_time_multiplier()
    base = random.randint(BASE_MIN, BASE_MAX)
    add = random.randint(ADD_MIN, ADD_MAX)
    increment = int((base + add) * multiplier)

    remaining = today_target - current_steps
    if increment > remaining:
        increment = remaining

    new_total = current_steps + increment
    print(f"🕒 {datetime.now().strftime('%H:%M')} | 本次增加：{increment} 步 | 当前累计：{new_total}/{today_target}")

    try:
        # 登录并同步
        login_info = login_zepp(account, password)
        access_token = login_info["access_token"]
        sync_steps(access_token, new_total)
        print("✅ 步数同步成功！")

        # 保存本次累计步数
        with open(steps_file, "w") as f:
            f.write(str(new_total))

    except Exception as e:
        print(f"❌ 同步失败：{str(e)}")
        return

if __name__ == "__main__":
    main()
