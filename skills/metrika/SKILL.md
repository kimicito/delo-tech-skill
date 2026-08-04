# metrika — Yandex Metrika Analytics Skill

Полный цикл: от OAuth-авторизации до бизнес-гипотез на основе данных Яндекс.Метрики.

## Что делает

1. **OAuth-авторизация** — проходит весь flow получения токена
2. **Сбор данных** — посещаемость, источники, страницы, страны
3. **Аналитика** — автоматический дашборд с метриками
4. **Гипотезы** — генерирует приоритизированные рекомендации по продвижению

## Установка

```bash
# Клонируй в skills/
git clone https://github.com/kimicito/metrika-skill.git skills/metrika
```

## Требования

- Python 3.9+
- `requests`
- `python-dotenv` (опционально)

```bash
pip install requests python-dotenv
```

## Быстрый старт

### Шаг 1: Создать приложение в Yandex OAuth

1. Открой: https://oauth.yandex.ru/client/new
2. **Название:** `Metrika Analytics`
3. **Платформы:** Веб-сервисы
4. **Redirect URI:** `https://your-site.com/callback` (или `http://localhost:8000/callback`)
5. Скопируй **Client ID**

### Шаг 2: Получить токен

```bash
# Способ 1: Через redirect (если есть веб-сайт)
open "https://oauth.yandex.ru/authorize?response_type=token&client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT"

# Способ 2: Без redirect (ручной)
open "https://oauth.yandex.ru/authorize?response_type=token&client_id=YOUR_CLIENT_ID"
# Скопируй токен из адресной строки после #access_token=
```

### Шаг 3: Настроить

```bash
export YANDEX_METRIKA_TOKEN="your_token_here"
export YANDEX_METRIKA_COUNTER_ID="92824982"
```

Или создай `.env`:
```
YANDEX_METRIKA_TOKEN=your_token_here
YANDEX_METRIKA_COUNTER_ID=92824982
```

### Шаг 4: Запустить анализ

```bash
python3 skills/metrika/scripts/metrika_dashboard.py
```

## Команды

### Полный дашборд

```bash
python3 skills/metrika/scripts/metrika_dashboard.py
```

Выводит:
- Общую сводку (визиты, пользователи, просмотры)
- Источники трафика
- Географию
- Бизнес-гипотезы с приоритетами

### Проверка доступа

```bash
python3 skills/metrika/scripts/check_access.py
```

### Помощник авторизации

```bash
python3 skills/metrika/scripts/oauth_helper.py
```

Генерирует ссылку для авторизации и инструкции.

## Архитектура

```
skills/metrika/
├── SKILL.md                 # Этот файл
├── README.md                # Документация
├── scripts/
│   ├── metrika_dashboard.py # Основной дашборд
│   ├── oauth_helper.py      # Помощник OAuth
│   ├── check_access.py      # Проверка токена
│   └── report_generator.py  # Генератор отчётов
├── examples/
│   └── sample_report.txt    # Пример вывода
└── .env.example             # Шаблон конфига
```

## API Endpoints

Используется **Yandex Metrika API v1**:

| Endpoint | Описание |
|----------|----------|
| `stat/v1/data` | Агрегированные данные |
| `stat/v1/data/bytime` | Данные по времени |
| `management/v1/counters` | Список счётчиков |

## Метрики

| Название | Описание |
|----------|----------|
| `ym:s:visits` | Визиты |
| `ym:s:pageviews` | Просмотры страниц |
| `ym:s:users` | Уникальные пользователи |
| `ym:s:bounceRate` | Показатель отказов |
| `ym:s:trafficSource` | Источник трафика |
| `ym:s:regionCountry` | Страна |

## Бизнес-гипотезы

Система автоматически генерирует гипотезы по направлениям:

- **🔴 HIGH** — SEO, трафик, конверсия
- **🟡 MEDIUM** — SMM, вовлечённость, продукт
- **🟢 LOW** — GEO-расширение, бренд

## Интеграция с OpenClaw

```yaml
# openclaw.yaml
skills:
  - path: skills/metrika
    triggers:
      - "метрика"
      - "аналитика"
      - "yandex"
      - "продвижение"
```

## Лицензия

MIT
