# Metrika Skill — Yandex Analytics for OpenClaw

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Полный цикл аналитики Яндекс.Метрики: от OAuth до бизнес-гипотез.

## 🚀 Быстрый старт

```bash
# 1. Клонируй
 git clone https://github.com/kimicito/metrika-skill.git

# 2. Установи зависимости
 pip install requests python-dotenv

# 3. Получи токен (см. SKILL.md)
# 4. Запусти
 python3 scripts/metrika_dashboard.py
```

## 📊 Пример вывода

```
============================================================
📊 SITE.COM — АНАЛИТИЧЕСКИЙ ДАШБОРД
============================================================

📅 Период: 2026-07-06 — 2026-08-05
📈 Визитов: 205
👥 Пользователей: 172
📄 Просмотров: 653
📊 Страниц/визит: 3.2
🚪 Отказов: 46.3%

=== 🌐 ИСТОЧНИКИ ТРАФИКА ===
Direct traffic: 119 визитов
Search engine traffic: 17 визитов
Social network traffic: 1 визит

=== 🧠 БИЗНЕС-ГИПОТЕЗЫ ===

1. 🔴 HIGH | SEO
   🎯 Низкий органический трафик (8%)
   🚀 Оптимизировать мета-теги, запустить блог
```

## 📁 Структура

```
skills/metrika/
├── SKILL.md              # OpenClaw skill manifest
├── README.md             # Этот файл
├── scripts/
│   ├── metrika_dashboard.py   # Дашборд + гипотезы
│   ├── oauth_helper.py        # Помощник авторизации
│   └── check_access.py        # Проверка токена
└── .env.example          # Шаблон конфигурации
```

## 🔑 Получение токена

1. Создай приложение: https://oauth.yandex.ru/client/new
2. Выбери платформу «Веб-сервисы»
3. Укажи Redirect URI
4. Скопируй Client ID
5. Открой: `https://oauth.yandex.ru/authorize?response_type=token&client_id=YOUR_ID`
6. Авторизуйся → скопируй токен из URL

## ⚙️ Конфигурация

```bash
# .env
YANDEX_METRIKA_TOKEN=your_token_here
YANDEX_METRIKA_COUNTER_ID=12345678
```

## 🛠️ Команды

| Команда | Описание |
|---------|----------|
| `python3 scripts/metrika_dashboard.py` | Полный отчёт |
| `python3 scripts/oauth_helper.py` | Генерация ссылки OAuth |
| `python3 scripts/check_access.py` | Проверка токена |

## 📄 Лицензия

MIT © Logistoria
