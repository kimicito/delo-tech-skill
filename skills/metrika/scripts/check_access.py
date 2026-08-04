#!/usr/bin/env python3
"""Check Yandex Metrika API access."""
import os
import requests

TOKEN = os.getenv("YANDEX_METRIKA_TOKEN", "")
COUNTER_ID = os.getenv("YANDEX_METRIKA_COUNTER_ID", "92824982")

def check():
    if not TOKEN:
        print("❌ YANDEX_METRIKA_TOKEN не задан")
        print("   Получи токен: https://oauth.yandex.ru/authorize")
        return False
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    url = f"https://api-metrika.yandex.net/stat/v1/data?ids={COUNTER_ID}&metrics=ym:s:visits&date1=today&date2=today"
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        visits = data.get("data", [{}])[0].get("metrics", [0])[0]
        print(f"✅ Доступ есть! Счётчик: {COUNTER_ID}")
        print(f"📊 Визитов сегодня: {int(visits)}")
        return True
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            print("❌ Доступ запрещён. Проверь токен.")
        elif e.response.status_code == 400:
            print("❌ Неверный запрос. Проверь ID счётчика.")
        else:
            print(f"❌ Ошибка: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка сети: {e}")
        return False

if __name__ == "__main__":
    check()
