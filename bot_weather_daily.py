import os
import requests
from datetime import datetime, timedelta, timezone

# 日本時間設定
JST = timezone(timedelta(hours=+9))
now = datetime.now(JST)
tomorrow_date = (now + timedelta(days=1)).strftime('%Y-%m-%d')

WEBHOOK_URL = os.getenv("WEATHER_WEBHOOK_URL")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
LAT, LON = "35.6663", "139.3158" # 八王子

if WEATHER_API_KEY and WEBHOOK_URL:
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&appid={WEATHER_API_KEY}&units=metric&lang=ja"
        data = requests.get(url).json()
        
        tomorrow_forecasts = [f for f in data['list'] if tomorrow_date in f['dt_txt']]
        
        weather_list = [f['weather'][0]['description'] for f in tomorrow_forecasts]
        temps = [f['main']['temp'] for f in tomorrow_forecasts]
        pops = [f.get('pop', 0) * 100 for f in tomorrow_forecasts]
        
        main_weather = tomorrow_forecasts[4]['weather'][0]['description'] if len(tomorrow_forecasts) > 4 else weather_list[0]
        max_temp = max(temps)
        min_temp = min(temps)
        temp_diff = max_temp - min_temp # 寒暖差
        max_pop = max(pops)
        
        # --- 服装アドバイスのロジック ---
        if max_temp >= 25:
            wear = "半袖で十分！暑さ対策せなしんじゃうかも"
        elif max_temp >= 20:
            wear = "長袖のシャツとかちょうどいいかも"
        elif max_temp >= 15:
            wear = "カーディガンとかジャケットがあったほうが安心かも"
        elif max_temp >= 10:
            wear = "セーターとか厚手のコート着た方がいいかも"
        else:
            wear = "めちゃ寒い、マフラーとか巻いた方がいいでな"
        
        # 寒暖差が激しい場合（8度以上）の追記
        if temp_diff >= 8:
            wear += "\n（寒暖差かなり激しくなりそうやで）"

        # --- 傘アドバイス ---
        if max_pop >= 50:
            rain_msg = f"降水確率 {max_pop:.0f}% やから、傘なかったらめっちゃ濡れるで"
        elif max_pop >= 20:
            rain_msg = f"降水確率 {max_pop:.0f}% やから、折りたたみ傘とかあったら安心かも"
        else:
            rain_msg = f"降水確率 {max_pop:.0f}% やし、傘は一切必要なし！"

        message = (
            f"【明日の八王子の予報】\n"
            f"天気：**{main_weather}**\n"
            f"気温：最高 **{max_temp:.1f}度** / 最低 **{min_temp:.1f}度**\n"
            f"服装：{wear}\n"
            f"雨：{rain_msg}"
        )
        
        requests.post(WEBHOOK_URL, json={"content": message})
    except Exception as e:
        pass
