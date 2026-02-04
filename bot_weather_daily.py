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
        
        # データの解析
        weather_list = [f['weather'][0]['description'] for f in tomorrow_forecasts]
        temps = [f['main']['temp'] for f in tomorrow_forecasts]
        # 降水確率は0〜1の間で入っているので%に直す（pop: 0.5 → 50%）
        pops = [f.get('pop', 0) * 100 for f in tomorrow_forecasts]
        
        main_weather = tomorrow_forecasts[4]['weather'][0]['description'] if len(tomorrow_forecasts) > 4 else weather_list[0]
        max_temp = max(temps)
        min_temp = min(temps)
        max_pop = max(pops) # 明日の最大降水確率
        
        # 降水確率によって傘メッセージを変える
        if max_pop >= 50:
            rain_msg = f"降水確率 {max_pop:.0f}% やから、傘なかったらめっちゃ濡れるで☔"
        elif max_pop >= 20:
            rain_msg = f"降水確率 {max_pop:.0f}% やから、折りたたみ傘とかあったら安心できそう☂️"
        else:
            rain_msg = f"降水確率 {max_pop:.0f}% やし傘はいらんな☀️"

        message = (
            f"【明日の八王子の予報】\n"
            f"天気：**{main_weather}**\n"
            f"気温：最高 **{max_temp:.1f}度** / 最低 **{min_temp:.1f}度**\n"
            f"{rain_msg}"
        )
        
        requests.post(WEBHOOK_URL, json={"content": message})
    except Exception as e:
        pass
