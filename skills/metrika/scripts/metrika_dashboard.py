#!/usr/bin/env python3
"""
Logistoria Yandex Metrika Analytics Dashboard
Collects metrics, builds reports, generates business hypotheses.
"""
import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

TOKEN = os.getenv("YANDEX_METRIKA_TOKEN", "y0__wgBEPDX5P8IGP3jRiDfu6zGGDD30vn4CGQUGVHHBZzqktnb-LUH2rVvm9ag")
COUNTER_ID = "92824982"
API_BASE = "https://api-metrika.yandex.net/stat/v1"

def fetch_data(endpoint, params):
    """Fetch data from Yandex Metrika API."""
    headers = {"Authorization": f"Bearer {TOKEN}"}
    url = f"{API_BASE}/{endpoint}"
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()

def get_summary(days=30):
    """Get traffic summary for last N days."""
    end = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    data = fetch_data("data", {
        "ids": COUNTER_ID,
        "metrics": "ym:s:visits,ym:s:pageviews,ym:s:users,ym:s:bounceRate",
        "date1": start,
        "date2": end
    })
    
    metrics = data.get("data", [{}])[0].get("metrics", [])
    if not metrics:
        return None
    
    visits = metrics[0]
    pageviews = metrics[1]
    users = metrics[2]
    bounce = metrics[3]
    
    return {
        "period": f"{start} — {end}",
        "total_visits": int(visits),
        "total_pageviews": int(pageviews),
        "total_users": int(users),
        "avg_bounce_rate": round(bounce, 1),
        "pages_per_visit": round(pageviews / visits, 1) if visits else 0,
    }

def get_sources(days=30):
    """Get traffic sources."""
    end = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    data = fetch_data("data", {
        "ids": COUNTER_ID,
        "dimensions": "ym:s:trafficSource",
        "metrics": "ym:s:visits,ym:s:users",
        "date1": start,
        "date2": end,
        "limit": 20,
        "sort": "-ym:s:visits"
    })
    
    sources = []
    for row in data.get("data", []):
        sources.append({
            "source": row["dimensions"][0]["name"],
            "visits": int(row["metrics"][0]),
            "users": int(row["metrics"][1])
        })
    return sources

def get_pages(days=30):
    """Get top pages."""
    end = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    data = fetch_data("data", {
        "ids": COUNTER_ID,
        "dimensions": "ym:s:URLPath",
        "metrics": "ym:s:pageviews,ym:s:users,ym:s:bounceRate",
        "date1": start,
        "date2": end,
        "limit": 20,
        "sort": "-ym:s:pageviews"
    })
    
    pages = []
    for row in data.get("data", []):
        pages.append({
            "path": row["dimensions"][0]["name"],
            "pageviews": int(row["metrics"][0]),
            "users": int(row["metrics"][1]),
            "bounce_rate": round(row["metrics"][2], 1)
        })
    return pages

def get_countries(days=30):
    """Get countries."""
    end = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    data = fetch_data("data", {
        "ids": COUNTER_ID,
        "dimensions": "ym:s:regionCountry",
        "metrics": "ym:s:visits,ym:s:users",
        "date1": start,
        "date2": end,
        "limit": 20,
        "sort": "-ym:s:visits"
    })
    
    countries = []
    for row in data.get("data", []):
        countries.append({
            "country": row["dimensions"][0]["name"],
            "visits": int(row["metrics"][0]),
            "users": int(row["metrics"][1])
        })
    return countries

def generate_hypotheses(summary, sources, pages, countries):
    """Generate business hypotheses based on data."""
    hypotheses = []
    
    # Traffic volume hypothesis
    if summary["total_visits"] < 500:
        hypotheses.append({
            "priority": "🔴 HIGH",
            "area": "Трафик",
            "hypothesis": "Низкий органический трафик. Запустить SEO-оптимизацию и контент-маркетинг.",
            "action": "Создать блог с кейсами, оптимизировать страницы под ключевые слова 'логистические игры', 'обучение supply chain'"
        })
    
    # Bounce rate hypothesis
    if summary["avg_bounce_rate"] > 50:
        hypotheses.append({
            "priority": "🔴 HIGH",
            "area": "Конверсия",
            "hypothesis": f"Высокий показатель отказов ({summary['avg_bounce_rate']}%). Пользователи не находят нужную информацию.",
            "action": "Улучшить CTA-кнопки, добавить видео-превью игр, упростить навигацию"
        })
    
    # Pages per visit
    if summary["pages_per_visit"] < 2:
        hypotheses.append({
            "priority": "🟡 MEDIUM",
            "area": "Вовлечённость",
            "hypothesis": "Пользователи смотрят мало страниц. Нет перекрёстных ссылок между играми.",
            "action": "Добавить блок 'Похожие игры' на каждой странице, улучшить внутреннюю перелинковку"
        })
    
    # Sources hypothesis
    organic = sum(s["visits"] for s in sources if s["source"].lower() in ["organic", "search", "seo"])
    direct = sum(s["visits"] for s in sources if s["source"].lower() in ["direct", "direct traffic", "direct / none"])
    social = sum(s["visits"] for s in sources if any(x in s["source"].lower() for x in ["social", "instagram", "telegram"]))
    
    if organic < summary["total_visits"] * 0.3:
        hypotheses.append({
            "priority": "🔴 HIGH",
            "area": "SEO",
            "hypothesis": "Мало органического трафика. Основной трафик — прямой или реферальный.",
            "action": "Оптимизировать мета-теги, добавить schema.org разметку, создать лендинги под ключевые запросы"
        })
    
    if social < 10:
        hypotheses.append({
            "priority": "🟡 MEDIUM",
            "area": "SMM",
            "hypothesis": "Минимальный трафик из соцсетей. Instagram/Telegram не работают как каналы.",
            "action": "Запустить регулярный контент в Instagram, добавить кнопки шеринга на сайте"
        })
    
    # Page-specific hypotheses
    top_pages = [p for p in pages if p["pageviews"] > 10]
    if top_pages:
        game_pages = [p for p in top_pages if any(x in p["path"] for x in ["kadena", "storewars", "beergame", "heroes", "market", "auction"])]
        if len(game_pages) < 3:
            hypotheses.append({
                "priority": "🟡 MEDIUM",
                "area": "Продукт",
                "hypothesis": "Не все игры получают трафик. Некоторые страницы неинтересны аудитории.",
                "action": "Проанализировать, какие игры популярны — сделать их более заметными на главной"
            })
    
    # Country hypothesis
    if countries:
        ru_visits = sum(c["visits"] for c in countries if c["country"] in ["Россия", "Russia"])
        if ru_visits > summary["total_visits"] * 0.8:
            hypotheses.append({
                "priority": "🟢 LOW",
                "area": "GEO",
                "hypothesis": "Аудитория 80%+ из России. Международное продвижение (EN, ES, FR) пока не даёт результата.",
                "action": "Запустить рекламу на LinkedIn для B2B аудитории в Европе, добавить кейсы на EN/ES/FR"
            })
    
    return hypotheses

def print_report():
    """Generate and print full report."""
    print("=" * 60)
    print("📊 LOGISTORIA.COM — АНАЛИТИЧЕСКИЙ ДАШБОРД")
    print("=" * 60)
    print()
    
    # Summary
    summary = get_summary(30)
    if not summary:
        print("❌ Нет данных за указанный период")
        return
    
    print(f"📅 Период: {summary['period']}")
    print(f"📈 Визитов: {summary['total_visits']}")
    print(f"👥 Пользователей: {summary['total_users']}")
    print(f"📄 Просмотров: {summary['total_pageviews']}")
    print(f"📊 Страниц/визит: {summary['pages_per_visit']}")
    print(f"🚪 Отказов: {summary['avg_bounce_rate']}%")
    print()
    
    # Sources
    sources = get_sources(30)
    if sources:
        print("=== 🌐 ИСТОЧНИКИ ТРАФИКА ===")
        for s in sources[:7]:
            print(f"{s['source']}: {s['visits']} визитов | {s['users']} юзеров")
        print()
    
    # Pages
    # pages = get_pages(30)
    # if pages:
    #     print("=== 📄 ТОП СТРАНИЦЫ ===")
    #     for p in pages[:7]:
    #         print(f"{p['path']}: {p['pageviews']} просмотров | {p['users']} юзеров | отказ {p['bounce_rate']}%")
    #     print()
    
    # Countries
    countries = get_countries(30)
    if countries:
        print("=== 🌍 СТРАНЫ ===")
        for c in countries[:7]:
            print(f"{c['country']}: {c['visits']} визитов | {c['users']} юзеров")
        print()
    
    # Hypotheses
    hypotheses = generate_hypotheses(summary, sources, [], countries)
    print("=" * 60)
    print("🧠 БИЗНЕС-ГИПОТЕЗЫ")
    print("=" * 60)
    for i, h in enumerate(hypotheses, 1):
        print()
        print(f"{i}. {h['priority']} | {h['area']}")
        print(f"   🎯 Гипотеза: {h['hypothesis']}")
        print(f"   🚀 Действие: {h['action']}")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    print_report()
