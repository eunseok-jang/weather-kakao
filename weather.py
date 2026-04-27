import requests
import os
from datetime import datetime, timezone, timedelta

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
OWM_API_KEY = os.environ.get("OWM_API_KEY")

KST = timezone(timedelta(hours=9))

# 미세먼지 등급
def get_dust_grade(pm25, pm10):
    if pm25 <= 15 and pm10 <= 30:
        return "💚 좋음"
    elif pm25 <= 35 and pm10 <= 80:
        return "💛 보통"
    elif pm25 <= 75 and pm10 <= 150:
        return "🟠 나쁨 😷 마스크 챙기세요!"
    else:
        return "🔴 매우나쁨 😷 외출 자제 권고!"

def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/forecast?q=Seoul&appid={OWM_API_KEY}&units=metric&lang=kr&cnt=8"
    res = requests.get(url).json()

    temps = [item["main"]["temp"] for item in res["list"]]
    temp_min = min(temps)
    temp_max = max(temps)

    current = res["list"][0]
    current_temp = current["main"]["temp"]
    current_desc = current["weather"][0]["description"]
    humidity     = current["main"]["humidity"]
    feels        = current["main"]["feels_like"]
    wind_speed   = current["wind"]["speed"]

    # 비/눈 시간대 분석
    rain_times = []
    snow_times = []

    for item in res["list"]:
        dt_kst = datetime.fromtimestamp(item["dt"], tz=KST)
        desc = item["weather"][0]["description"].lower()
        time_str = dt_kst.strftime("%H시")
        if "비" in desc or "rain" in desc or "drizzle" in desc:
            rain_times.append(time_str)
        if "눈" in desc or "snow" in desc:
            snow_times.append(time_str)

    return current_temp, feels, current_desc, humidity, temp_min, temp_max, rain_times, snow_times, wind_speed

def get_air_quality():
    # 서울 위도/경도
    lat, lon = 37.5683, 126.9778
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={OWM_API_KEY}"
    res = requests.get(url).json()
    print("대기질 응답:", res)

    components = res["list"][0]["components"]
    pm25 = components["pm2_5"]
    pm10 = components["pm10"]
    return pm25, pm10

def build_special_alerts(rain_times, snow_times, pm25, pm10, wind_speed):
    alerts = []

    # 비
    if snow_times:
        alerts.append(f"❄️ 눈 예보: {snow_times[0]} ~ {snow_times[-1]}")
    if rain_times:
        alerts.append(f"☂️ 비 예보: {rain_times[0]} ~ {rain_times[-1]}")

    # 미세먼지
    dust_grade = get_dust_grade(pm25, pm10)
    alerts.append(f"🌫 미세먼지: {dust_grade} (PM2.5 {pm25:.0f} / PM10 {pm10:.0f})")

    # 황사 (PM10이 매우 높으면)
    if pm10 >= 300:
        alerts.append("🟤 황사 경보! 외출 시 마스크 필수!")
    elif pm10 >= 150:
        alerts.append("🟤 황사 주의! 마스크 챙기세요")

    # 강풍
    if wind_speed >= 14:
        alerts.append(f"💨 강풍 주의! 풍속 {wind_speed:.1f}m/s")
    elif wind_speed >= 9:
        alerts.append(f"💨 바람 강함 풍속 {wind_speed:.1f}m/s")

    if not alerts:
        alerts.append("☀️ 특이사항 없음! 맑은 하루 되세요")

    return "\n".join(alerts)

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    r = requests.post(url, data=data)
    print("텔레그램 응답:", r.text)

def main():
    current_temp, feels, current_desc, humidity, temp_min, temp_max, rain_times, snow_times, wind_speed = get_weather()
    pm25, pm10 = get_air_quality()
    alerts = build_special_alerts(rain_times, snow_times, pm25, pm10, wind_speed)

    today = datetime.now(KST).strftime("%m월 %d일")
    msg = (
        f"🌤 {today} 서울 날씨\n"
        f"━━━━━━━━━━━━━━\n"
        f"🌡 현재 기온: {current_temp:.1f}°C\n"
        f"🤔 체감 온도: {feels:.1f}°C\n"
        f"☁️  날씨: {current_desc}\n"
        f"💧 습도: {humidity}%\n"
        f"💨 풍속: {wind_speed:.1f}m/s\n"
        f"━━━━━━━━━━━━━━\n"
        f"📉 오늘 최저: {temp_min:.1f}°C\n"
        f"📈 오늘 최고: {temp_max:.1f}°C\n"
        f"━━━━━━━━━━━━━━\n"
        f"⚠️ 오늘의 특이사항\n"
        f"{alerts}\n"
        f"━━━━━━━━━━━━━━\n"
        f"오늘도 좋은 하루 되세요 ☀️"
    )
    send_telegram(msg)

main()
