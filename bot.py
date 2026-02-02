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

message = ""

# --- ゴミ出しの自動判別ライン ---

# 【月曜日】
if weekday == 0: 
    message = "明日は **【燃えるゴミ・プラスチック】** の日やでな"

# 【火曜日】交互（缶 or 瓶）
elif weekday == 1: 
    # 今週（6週目・偶数）は「缶」
    if week_number % 2 == 0:
        message = "明日は **【缶】** の日かも"
    else:
        message = "明日は **【瓶】** の日らしいで"

# 【水曜日】隔週（ダンボール）
elif weekday == 2:
    # 来週（7週目・奇数）から通知するために「!= 0」にしています
    if week_number % 2 != 0:
        message = "明日は **【ダンボール】** の日っぽい"

# 【木曜日】毎週：燃えるゴミ ＋ 隔週：ペットボトル
elif weekday == 3:
    # ペットボトルも来週（7週目・奇数）なので「!= 0」にしました
    if week_number % 2 != 0:
        message = "明日は **【燃えるゴミ】** の日やで\nあ、**【ペットボトル】** も忘れんといてな"
    else:
        message = "明日は **【燃えるゴミ】** の日やでな"

# メッセージがあれば送信実行
if message and WEBHOOK_URL:
    requests.post(WEBHOOK_URL, json={"content": message})
