import os
import requests
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=+9))
tomorrow = datetime.now(JST) + timedelta(days=1)

WEBHOOK_URL = os.getenv("WEATHER_WEBHOOK_URL")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
LAT, LON = "35.6663", "139.3158" # 八王子

if WEATHER_API_KEY and WEBHOOK_URL:
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&appid={WEATHER_API_KEY}&units=metric&lang=ja"
    data = requests.get(url).json()
    target = data['list'][8] # 明日の昼頃
    weather = target['weather'][0]['description']
    temp = target['main']['temp']
    msg = f"明日の八王子の天気は\n**【{weather}】**、気温は {temp}度 くらいやで"
    requests.post(WEBHOOK_URL, json={"content": msg})
