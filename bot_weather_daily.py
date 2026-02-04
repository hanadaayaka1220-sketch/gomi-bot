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
        
        # 明日のデータだけを抽出
        tomorrow_forecasts = [f for f in data['list'] if tomorrow_date in f['dt_txt']]
        
        # 天気、最高・最低気温、雨の判定
        weather_list = [f['weather'][0]['description'] for f in tomorrow_forecasts]
        temps = [f['main']['temp'] for f in tomorrow_forecasts]
        
        # 代表的な天気（お昼頃）
        main_weather = tomorrow_forecasts[4]['weather'][0]['description'] if len(tomorrow_forecasts) > 4 else weather_list[0]
        max_temp = max(temps)
        min_temp = min(temps)
        
        # 雨が降るかチェック（予報に「雨」という文字があるか）
        rain_info = "傘持っていったほうがいいで ☂️" if any("雨" in w for w in weather_list) else "傘はいらんみたいやで ☀️"

        message = (
            f"【明日の八王子の予報】\n"
            f"天気：**{main_weather}**\n"
            f"気温：最高 **{max_temp:.1f}度** / 最低 **{min_temp:.1f}度**\n"
            f"{rain_info}"
        )
        
        requests.post(WEBHOOK_URL, json={"content": message})
    except Exception as e:
        # エラーが起きた場合は通知（デバッグ用）
        # requests.post(WEBHOOK_URL, json={"content": f"エラー出たわ：{e}"})
        pass
