---
name: supplychains-article-scraper
description: >
  Сбор статей с supplychains.ru/blog для Telegram-бота @supplychains.
  Используется browser automation (Cloudflare защита, Tilda JS-рендеринг).
  Ротация: 19+ статей, не повторяться ~3 месяца.
---

# SupplyChains Article Scraper

## Назначение
Автоматический сбор реальных статей с блога supplychains.ru для публикации в Telegram-канале @supplychains.

## Проблема доступа
- Сайт на Tilda — JS-рендеринг, динамический контент
- Cloudflare — curl/kimi_fetch не работает (403/блокировка)
- Только browser automation (Chromium через OpenClaw)

---

## Методология: 5 шагов

### Шаг 1: Открыть /blog через browser

```python
browser action="navigate" url="https://supplychains.ru/blog"
```

### Шаг 2: Догрузить ленту

Кнопка «ЗАГРУЗИТЬ ЕЩЁ» — кликать пока не исчезнет:
```python
browser action="snapshot"  # найти ref кнопки
browser action="click" ref="eN"  # клик
# Повторить 2-3 раза для получения 25+ статей
```

### Шаг 3: Собрать URL статей

Из snapshot извлечь все ссылки `/blog/*`:
- Каждая статья: `https://supplychains.ru/blog/<slug>`
- Собрать 19-25 уникальных URL
- Убрать дубли (например, kak-oformit-gruz может повторяться)

### Шаг 4: Прочитать каждую статью

Для каждого URL:
```python
browser action="navigate" url="https://supplychains.ru/blog/<slug>"
browser action="snapshot"  # извлечь заголовок + текст
```

**Что извлекать:**
- Заголовок H1
- Основной текст статьи
- Ключевые тезисы (3-5 пунктов)

### Шаг 5: Обновить config.py бота

Структура данных в `projects/supplychains-bot/config.py`:

```python
ARTICLES_DATABASE = [
    {
        "title": "...",
        "url": "https://supplychains.ru/blog/...",
        "summary": "...",
        "key_points": ["...", "...", "..."]
    },
    # ... 19-25 статей
]
```

---

## Ротация контента

- **19 уникальных статей** = ~9.5 недель ротации (2 статьи в неделю)
- **Индекс текущей статьи** хранится в `bot_state.json`
- Берём `articles[index % len(articles)]` для вторника
- Берём `articles[(index+1) % len(articles)]` для четверга
- После публикации — инкремент индекса

```python
# bot_state.json
{
    "article_index": 0,  # текущая позиция в ротации
    "last_updated": "2026-07-21"
}
```

---

## Технические детали

| Параметр | Значение |
|----------|----------|
| Браузер | Chromium через OpenClaw |
| Таргет | DE29C9B00AB22E0041686C06E12DACC4 |
| Защита | Cloudflare |
| Платформа | Tilda (JS-рендеринг) |
| Метод | Browser automation only |

---

## Файлы проекта

```
projects/supplychains-bot/
├── bot.py              # Основной бот
├── config.py           # Конфиг + ARTICLES_DATABASE
├── .env                # Токен (не в git)
├── requirements.txt    # Зависимости
└── bot_state.json      # Индекс ротации
```

---

## История обновлений

| Дата | Что изменилось |
|------|----------------|
| 2026-07-21 | Первый сбор: 19 уникальных статей через browser |

---

## Проверенные статьи (URL)

1. https://supplychains.ru/blog/logistika-domashnih-hozyaistv
2. https://supplychains.ru/blog/logistika-obshestvennogo-pitaniya
3. https://supplychains.ru/blog/upravlenie-zapasami
4. https://supplychains.ru/blog/logistika-tovarnogo-sklada
5. https://supplychains.ru/blog/logistika-optovoy-torgovli
6. https://supplychains.ru/blog/logistika-transportnoy-kompanii
7. https://supplychains.ru/blog/model-pyati-sil-portera
8. https://supplychains.ru/blog/supplychains-kak-vybirat-postavschikov
9. https://supplychains.ru/blog/kak-otsenit-riski-postavschika
10. https://supplychains.ru/blog/tendernye-zakupki
11. https://supplychains.ru/blog/supply-chain-strategy
12. https://supplychains.ru/blog/5-prichin-pochemu-postavschik-mozhet-sorvat-sroki
13. https://supplychains.ru/blog/kak-vybrat-transportnuyu-kompaniyu
14. https://supplychains.ru/blog/sklog-otzyv
15. https://supplychains.ru/blog/kak-oformit-gruz
16. https://supplychains.ru/blog/chto-takoe-in-kot
17. https://supplychains.ru/blog/logistika-i-sklad
18. https://supplychains.ru/blog/strategiya-zakupok
19. https://supplychains.ru/blog/5-veschey-kotorye-nuzhno-znat

---

*Version: 1.0*
*Created: 2026-07-21*
*Bot: @Lgistbot | Channel: @supplychains*
