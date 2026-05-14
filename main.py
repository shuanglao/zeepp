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
    print(f"🕐 当前时间: {datetime.now().strftime('%H:%M')}, 小时数: {hour}")
    if 9 <= hour < 12:
        print("☀️ 时段: 早上，增幅系数: 0.6")
        return 0.6
    elif 12 <= hour < 18:
        print("🌞 时段: 下午，增幅系数: 1.2")
        return 1.2
    elif 18 <= hour < 23:
        print("🌙 时段: 晚上，增幅系数: 0.8")
        return 0.8
    print("🌃 时段: 非运行时段，增幅系数: 0.5")
    return 0.5

def login_zepp(account, password):
    print("🔐 正在登录 Zepp...")
    # 最新可用的登录接口
    url = "https://account.zepp.com/v2/client/login"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Zepp/7.0.0 (Android 14; Scale/3.00)",
        "Accept": "*/*"
    }
    data = {
        "country_code": "CN",
        "account": account,
        "password": password,
        "grant_type": "password",
        "client_id": "com.huami.mifit",
        "device_id": "zepp_robot_" + str(random.randint(100000, 999999)),
        "app_name": "com.huami.mifit"
    }
    try:
        res = requests.post(url, headers=headers, data=data, timeout=30)
        res.raise_for_status()
        print("✅ 登录成功！")
        return res.json()
    except Exception as e:
        print(f"❌ 登录失败: {str(e)}")
        raise

def sync_steps(access_token, steps):
    print(f"📤 正在同步 {steps} 步...")
    url = "https://api-mifit.zepp.com/v1/user/sync"
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
    try:
        res = requests.post(url, headers=headers, json=data, timeout=30)
        res.raise_for_status()
        print("✅ 步数同步成功！")
        return True
    except Exception as e:
        print(f"❌ 同步失败: {str(e)}")
        raise

def main():
    print("=" * 50)
    print("🚀 云端全自动刷步脚本启动")
    print("=" * 50)

    # 从 Secrets 读取账号密码
    account = os.getenv("ACCOUNT")
    password = os.getenv("PASSWORD")
    print(f"🔍 读取账号配置: ACCOUNT={account[:3]}***, PASSWORD={len(password)*'*'}")
    if not account or not password:
        print("❌ 错误：ACCOUNT 或 PASSWORD 未配置！")
        return

    # 今日目标步数（随机生成）
    today_target = random.randint(DAY_MIN, DAY_MAX)
    print(f"🎯 今日目标步数: {today_target}")

    # 读取/初始化累计步数
    steps_file = "/tmp/today_steps.txt"
    print(f"📂 读取步数记录文件: {steps_file}")
    try:
        with open(steps_file, "r") as f:
            current_steps = int(f.read().strip())
            print(f"📊 已读取累计步数: {current_steps}")
    except (FileNotFoundError, ValueError):
        current_steps = 0
        print("📝 未找到记录文件，初始化为 0")

    if current_steps >= today_target:
        print("🛑 已达今日步数上限，无需继续运行")
        return

    # 计算本次增量
    multiplier = get_time_multiplier()
    base = random.randint(BASE_MIN, BASE_MAX)
    add = random.randint(ADD_MIN, ADD_MAX)
    increment = int((base + add) * multiplier)
    print(f"📈 本次增量计算: base={base}, add={add}, multiplier={multiplier}, increment={increment}")

    remaining = today_target - current_steps
    if increment > remaining:
        increment = remaining
        print(f"⚠️ 增量超过剩余步数，调整为剩余步数: {increment}")

    new_total = current_steps + increment
    print(f"🕒 {datetime.now().strftime('%H:%M')} | 本次增加: {increment} 步 | 当前累计: {new_total}/{today_target}")

    try:
        # 登录并同步
        login_info = login_zepp(account, password)
        access_token = login_info["access_token"]
        sync_steps(access_token, new_total)

        # 保存本次累计步数
        with open(steps_file, "w") as f:
            f.write(str(new_total))
        print(f"💾 已保存新的累计步数: {new_total}")

    except Exception as e:
        print(f"❌ 运行失败: {str(e)}")
        return

    print("=" * 50)
    print("✅ 脚本运行完成！")
    print("=" * 50)

if __name__ == "__main__":
    main()
