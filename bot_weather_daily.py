import os
import requests
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup

# 日本時間設定
JST = timezone(timedelta(hours=+9))
now = datetime.now(JST)
today_date = now.strftime('%Y-%m-%d')
tomorrow_date = (now + timedelta(days=1)).strftime('%Y-%m-%d')

WEBHOOK_URL = os.getenv("WEATHER_WEBHOOK_URL")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
LAT, LON = "35.6663", "139.3158" # 八王子

if WEATHER_API_KEY and WEBHOOK_URL:
    try:
        # --- 1. 天気予報の取得 ---
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&appid={WEATHER_API_KEY}&units=metric&lang=ja"
        data = requests.get(url).json()
        
        # 今日と明日のデータを抽出
        today_forecasts = [f for f in data['list'] if today_date in f['dt_txt']]
        tomorrow_forecasts = [f for f in data['list'] if tomorrow_date in f['dt_txt']]
        
        # 今日の最高気温（データがない場合は現在の気温を使用）
        today_max = max([f['main']['temp'] for f in today_forecasts]) if today_forecasts else data['list'][0]['main']['temp']
        
        # 明日のデータ解析
        weather_list = [f['weather'][0]['description'] for f in tomorrow_forecasts]
        temps = [f['main']['temp'] for f in tomorrow_forecasts]
        pops = [f.get('pop', 0) * 100 for f in tomorrow_forecasts]
        
        main_weather = tomorrow_forecasts[4]['weather'][0]['description'] if len(tomorrow_forecasts) > 4 else weather_list[0]
        max_temp = max(temps)
        min_temp = min(temps)
        max_pop = max(pops)
        
        # --- 2. 今日との気温差メッセージ ---
        diff = max_temp - today_max
        if diff <= -3:
            diff_msg = f"今日より {abs(diff):.1f}度も下がるらしい"
        elif diff < 0:
            diff_msg = f"今日より {abs(diff):.1f}度低いらしい"
        elif diff >= 3:
            diff_msg = f"今日より {diff:.1f}度も上がるらしい"
        else:
            diff_msg = "今日と同じくらいの気温やで"

        # --- 3. 花粉情報の取得（ある時だけ） ---
        pollen_info = ""
        try:
            pollen_url = "https://tenki.jp/pollen/3/16/4410/13201/"
            res = requests.get(pollen_url, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.find_all(class_='pollen-forecast__item')
            if len(items) >= 2:
                rank = items[1].find(class_='pollen-forecast__level').text.strip()
                pollen_advices = {
                    "少ない": "ちょっと飛んでるかも？油断は禁物",
                    "やや多い": "マスクしといたほうが安心かも",
                    "多い": "結構飛んでる！対策しっかりした方が身の為",
                    "非常に多い": "ありえへんくらい飛んでる！！！！\n目も鼻もやられちゃうから気をつけて😭"
                }
                pollen_info = f"\n花粉：{rank}（{pollen_advices.get(rank, 'しっかり対策してね')}）"
        except:
            pass
        
        # --- 4. 傘アドバイス ---
        if max_pop >= 50:
            rain_msg = f"降水確率 {max_pop:.0f}% やから傘なかったら濡れる可能性はかなりあるね"
        elif max_pop >= 20:
            rain_msg = f"降水確率 {max_pop:.0f}% やから、折りたたみ傘とかあったら安心かも"
        else:
            rain_msg = f"降水確率 {max_pop:.0f}% やし、傘は一切必要なし！"

        # --- 5. メッセージ作成 ---
        message = (
            f"【明日の八王子の予報】\n"
            f"天気：**{main_weather}**\n"
            f"気温：最高 **{max_temp:.1f}度** / 最低 **{min_temp:.1f}度**\n"
            f"前日比：{diff_msg}\n"
            f"雨：{rain_msg}"
        )
        
        if pollen_info:
            message += pollen_info
        
        requests.post(WEBHOOK_URL, json={"content": message})
    except Exception as e:
        pass
