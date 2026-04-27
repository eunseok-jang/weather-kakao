import requests
import os
from datetime import datetime

KAKAO_TOKEN = os.environ.get("KAKAO_TOKEN")
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

def send_kakao(message):
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {KAKAO_TOKEN}"}
    data = {
        "template_object": '{"object_type":"text","text":"' + message + '","link":{"web_url":"https://weather.naver.com"}}'
    }
    r = requests.post(url, headers=headers, data=data)
    print("카카오 응답:", r.text)

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
    send_kakao(msg)

main()
