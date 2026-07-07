# HH.ru Scraper Reference

## Проблема

Публичное API hh.ru (`https://api.hh.ru/vacancies`) часто возвращает 403 Forbidden для облачных IP. Ниже — рабочие альтернативы.

## Метод 1: kimi_search (быстрый)

Ищем вакансии через поисковый индекс:

```
kimi_search: "site:hh.ru Python разработчик Москва 150000"
```

Результат: список URL вакансий. Затем для каждого URL:
```
web_fetch: <url>
```

## Метод 2: browser (надёжный)

Открываем hh.ru и ищем через UI:

```
browser: open https://hh.ru
browser: type "Поиск по вакансиям" "Python разработчик"
browser: click "Найти"
browser: snapshot
```

Для фильтрации по зарплате:
```
browser: type "от" "150000"
browser: click "Показать результаты"
```

## Метод 3: web_fetch (прямой)

Пробуем получить страницу поиска напрямую:

```
web_fetch: https://hh.ru/search/vacancy?text=Python+разработчик&area=1&salary=150000
```

Если blocked — fallback на browser.

## Парсинг результата

Из любого метода извлекаем:
- `title` — название вакансии
- `company` — компания
- `salary` — зарплата (или "Не указана")
- `url` — ссылка на вакансию
- `snippet` — требования/описание
- `experience` — опыт
- `location` — город

Формат вывода: JSON массив объектов.

## Сохранение результатов

```json
[
  {
    "title": "Python разработчик",
    "company": "ООО Технологии",
    "salary": "От 150 000 до 250 000 RUR",
    "url": "https://hh.ru/vacancy/12345678",
    "snippet": "Требования: Python, Django, PostgreSQL...",
    "experience": "От 3 до 6 лет",
    "location": "Москва"
  }
]
```

## Скрипт fallback

`scripts/hh_scraper.py` — попробовать если API доступен. Параметры:
- `--query` — поисковый запрос
- `--area` — город (1 = Москва, 2 = СПб, 113 = Россия)
- `--salary` — минимальная зарплата
- `--limit` — количество результатов (default: 20)
- `--output` — файл для сохранения JSON

```bash
python scripts/hh_scraper.py --query "Python разработчик" --area 1 --limit 20 --output jobs.json
```
