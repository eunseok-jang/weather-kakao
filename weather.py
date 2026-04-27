import requests
import os
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
OWM_API_KEY = os.environ.get("OWM_API_KEY")

def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q=Seoul&appid={OWM_API_KEY}&units=metric&lang=kr"
    res = requests.get(url).json()
    print("API 응답:", res)
    if "main" not in res:
        raise Exception(f"날씨 API 오류: {res}")
    temp     = res["main"]["temp"]
    feels    = res["main"]["feels_like"]
    desc     = res["weather"][0]["description"]
    humidity = res["main"]["humidity"]
    return temp, feels, desc, humidity

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    r = requests.post(url, data=data)
    print("텔레그램 응답:", r.text)

def main():
    temp, feels, desc, humidity = get_weather()
    today = datetime.now().strftime("%m월 %d일")
    msg = (
        f"🌤 {today} 서울 날씨\n"
        f"━━━━━━━━━━━━━━\n"
        f"🌡 현재 기온: {temp:.1f}°C\n"
        f"🤔 체감 온도: {feels:.1f}°C\n"
        f"☁️  날씨: {desc}\n"
        f"💧 습도: {humidity}%\n"
        f"━━━━━━━━━━━━━━\n"
        f"오늘도 좋은 하루 되세요 ☀️"
    )
    send_telegram(msg)

main()
