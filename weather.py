import requests
import os
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
OWM_API_KEY = os.environ.get("OWM_API_KEY")

def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/forecast?q=Seoul&appid={OWM_API_KEY}&units=metric&lang=kr&cnt=8"
    res = requests.get(url).json()
    print("API 응답:", res)

    temps = [item["main"]["temp"] for item in res["list"]]
    descs = [item["weather"][0]["description"] for item in res["list"]]
    rain  = any("비" in d or "rain" in d.lower() for d in descs)
    snow  = any("눈" in d or "snow" in d.lower() for d in descs)

    temp_min = min(temps)
    temp_max = max(temps)

    if snow:
        characteristic = "❄️ 눈 소식이 있어요! 우산 챙기세요"
    elif rain:
        characteristic = "☂️ 비 소식이 있어요! 우산 챙기세요"
    else:
        characteristic = "☀️ 맑은 하루가 예상돼요"

    current_temp = res["list"][0]["main"]["temp"]
    current_desc = res["list"][0]["weather"][0]["description"]
    humidity     = res["list"][0]["main"]["humidity"]
    feels        = res["list"][0]["main"]["feels_like"]

    return current_temp, feels, current_desc, humidity, temp_min, temp_max, characteristic

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    r = requests.post(url, data=data)
    print("텔레그램 응답:", r.text)

def main():
    current_temp, feels, current_desc, humidity, temp_min, temp_max, characteristic = get_weather()
    today = datetime.now().strftime("%m월 %d일")
    msg = (
        f"🌤 {today} 서울 날씨\n"
        f"━━━━━━━━━━━━━━\n"
        f"🌡 현재 기온: {current_temp:.1f}°C\n"
        f"🤔 체감 온도: {feels:.1f}°C\n"
        f"☁️  날씨: {current_desc}\n"
        f"💧 습도: {humidity}%\n"
        f"━━━━━━━━━━━━━━\n"
        f"📉 오늘 최저: {temp_min:.1f}°C\n"
        f"📈 오늘 최고: {temp_max:.1f}°C\n"
        f"━━━━━━━━━━━━━━\n"
        f"{characteristic}\n"
        f"━━━━━━━━━━━━━━\n"
        f"오늘도 좋은 하루 되세요 ☀️"
    )
    send_telegram(msg)

main()
