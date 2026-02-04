import os
import requests

WEBHOOK_URL = os.getenv("WEATHER_WEBHOOK_URL")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
LAT, LON = "35.6663", "139.3158"

if WEATHER_API_KEY and WEBHOOK_URL:
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&appid={WEATHER_API_KEY}&units=metric"
    data = requests.get(url).json()
    p_now = data['list'][0]['main']['pressure']
    p_next = data['list'][1]['main']['pressure']
    diff = p_now - p_next

    msg = ""
    if diff >= 4:
        msg = "⚠️**【気圧警報：一気に低下】**\nこれから気圧がガクッと急降下するらしい。頭痛くなるかもしれんから気をつけて。"
    elif diff >= 2:
        msg = "💡**【気圧注意：徐々に低下】**\nこれから気圧が少しずつ下がるっぽい。危ないかも。"

    if msg:
        requests.post(WEBHOOK_URL, json={"content": msg})
