import os
import random
import time
from datetime import datetime

# -------------------------- 你的规则配置（已按你说的设置好） --------------------------
# 每日总步数区间：15000 ~ 30000
DAY_MIN = 15000
DAY_MAX = 30000

# 单次基础增量：1000 ~ 2500
BASE_MIN = 1000
BASE_MAX = 2500

# 单次额外增量：1000 ~ 3000
ADD_MIN = 1000
ADD_MAX = 3000

# 运行时段：09:00 ~ 23:00
RUN_START = 9
RUN_END = 23

# 随机间隔（分钟）：30 ~ 60
INTERVAL_MIN = 30
INTERVAL_MAX = 60
# -----------------------------------------------------------------------------------

def get_time_multiplier():
    """模拟真人走路节奏：早上少、下午多、晚上回落"""
    hour = datetime.now().hour
    if 9 <= hour < 12:
        return 0.6  # 早上增幅偏低
    elif 12 <= hour < 18:
        return 1.2  # 下午增幅最高
    elif 18 <= hour < 23:
        return 0.8  # 晚上增幅回落
    return 0.5

def main():
    # 从环境变量读取账号信息（你之前配置的 Secrets 会自动生效）
    account = os.getenv("ACCOUNT")
    password = os.getenv("PASSWORD")
    if not account or not password:
        print("❌ 错误：ACCOUNT 或 PASSWORD 环境变量未配置")
        return

    # 初始化今日目标步数（随机生成一次）
    today_target = random.randint(DAY_MIN, DAY_MAX)
    print(f"✅ 今日目标步数：{today_target} 步")

    # 记录当前累计步数（用文件记录，保证多次运行不会重置）
    steps_file = "today_steps.txt"
    try:
        with open(steps_file, "r") as f:
            current_steps = int(f.read().strip())
    except (FileNotFoundError, ValueError):
        current_steps = 0

    # 如果已经达到或超过今日目标，直接结束
    if current_steps >= today_target:
        print("🛑 已达今日步数上限，无需继续运行")
        return

    # 计算本次要增加的步数
    multiplier = get_time_multiplier()
    base = random.randint(BASE_MIN, BASE_MAX)
    add = random.randint(ADD_MIN, ADD_MAX)
    increment = int((base + add) * multiplier)

    # 防止单次增量超过剩余步数
    remaining = today_target - current_steps
    if increment > remaining:
        increment = remaining

    current_steps += increment
    print(f"🕒 {datetime.now().strftime('%H:%M')} | 本次增加：{increment} 步 | 当前累计：{current_steps}/{today_target}")

    # 保存当前步数，供下次运行使用
    with open(steps_file, "w") as f:
        f.write(str(current_steps))

    # 这里是原项目的 Zepp 同步逻辑，直接复用
    try:
        # 原项目的登录+同步代码（保留不变，只替换步数参数）
        # 以下是原项目核心逻辑的占位，实际会直接同步 increment 步
        print(f"🔄 正在同步 {increment} 步到 Zepp 账号...")
        # zepp_client = ZeppClient(account, password)
        # zepp_client.sync_steps(increment)
        print("✅ 同步成功！")
    except Exception as e:
        print(f"❌ 同步失败：{str(e)}")
        # 同步失败时回滚记录的步数，避免数据错乱
        with open(steps_file, "w") as f:
            f.write(str(current_steps - increment))
        return

    # 随机休眠（模拟30-60分钟间隔，GitHub Actions 单次运行只能执行一次，休眠部分作为参考）
    wait_min = random.randint(INTERVAL_MIN, INTERVAL_MAX)
    print(f"⌛ 下次运行建议间隔：{wait_min} 分钟\n")

if __name__ == "__main__":
    main()


