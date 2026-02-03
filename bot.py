import os
import requests
from datetime import datetime, timedelta, timezone

# 日本時間 (JST) を設定
JST = timezone(timedelta(hours=+9))
now = datetime.now(JST)
tomorrow = now + timedelta(days=1)
weekday = tomorrow.weekday() # 0:月, 1:火, 2:水, 3:木, 4:金, 5:土, 6:日
week_number = tomorrow.isocalendar()[1]

# GitHubの「隠し金庫」からURLを取り出す
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# 【追加】ゴミの日じゃない時のデフォルトメッセージ
message = "明日はごみの日じゃないよ/n安心してね、ちゅ"

# --- ゴミ出しの自動判別ライン ---

# 【月曜日】
if weekday == 0: 
    message = "明日は **【燃えるゴミ・プラスチック】** の日やでな"

# 【火曜日】
elif weekday == 1: 
    if week_number % 2 == 0:
        message = "明日は **【缶】** の日かも"
    else:
        message = "明日は **【瓶】** の日らしいで"

# 【水曜日】（ダンボールは来週・奇数週）
elif weekday == 2:
    if week_number % 2 != 0:
        message = "明日は **【ダンボール】** の日っぽい"

# 【木曜日】（ペットボトルは来週・奇数週）
elif weekday == 3:
    if week_number % 2 != 0:
        message = "明日は **【燃えるゴミ】** の日やでなあ、**【ペットボトル】** も忘れんといてな"
    else:
        message = "明日は **【燃えるゴミ】** の日やでな"

# URLがあれば毎日必ず送信します
if WEBHOOK_URL:
    requests.post(WEBHOOK_URL, json={"content": message})
