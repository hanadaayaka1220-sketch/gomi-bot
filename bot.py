import os
import requests
from datetime import datetime, timedelta, timezone

# 日本時間 (JST) を設定
JST = timezone(timedelta(hours=+9))
now = datetime.now(JST)
tomorrow = now + timedelta(days=1)
weekday = tomorrow.weekday() # 0:月, 1:火, 2:水, 3:木, 4:金, 5:土, 6:日

# 「隠し金庫」からURLを取り出す
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

message = ""

# --- ゴミ出しの自動判別ライン ---
# 【月曜】毎週：燃えるゴミ、プラスチック
if weekday == 0: 
    message = "明日は **【燃えるゴミ・プラスチック】** の日やでな"

# 【火曜】隔週：缶 or 瓶
elif weekday == 1: 
    week_number = tomorrow.isocalendar()[1]
    if week_number % 2 == 0:
        message = "明日は **【缶】** の日かも"
    else:
        message = "明日は **【瓶】** の日らしいで"

# 【水曜】隔週：ダンボール
elif weekday == 2:
    week_number = tomorrow.isocalendar()[1]
    if week_number % 2 == 0:
        message = "明日は **【ダンボール】** の日っぽい"

# 【木曜】毎週：燃えるゴミ ＋ 隔週：ペットボトル
elif weekday == 3:
    week_number = tomorrow.isocalendar()[1]
    if week_number % 2 == 0:
        message = "明日は **【燃えるゴミ】** の日やでな\nあ、**【ペットボトル】** も忘れんといてな"
    else:
        message = "明日は **【燃えるゴミ】** の日やでな"

# メッセージがあれば送信実行
if message and WEBHOOK_URL:
    requests.post(WEBHOOK_URL, json={"content": message})
