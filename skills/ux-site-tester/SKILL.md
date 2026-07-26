---
name: ux-site-tester
description: |
  UX/UI тестировщик сайтов с проверкой форм, email-рассылок, адаптивности, скорости и автоматическим loop-улучшением.
  Использовать когда пользователь просит протестировать сайт, проверить UX/UI, найти баги,
  или запустить цикл тестирование-исправление-тестирование (loop).
  Триггеры: "протестируй сайт", "проверь формы", "ux тестирование", "проверь email",
  "проверь адаптивность", "тест скорости", "найди баги", "улучши сайт", "loop тестирование".
---

# UX Site Tester

## Описание

Автоматизированное тестирование веб-сайтов с **циклом улучшения**:
1. **Тестирование** — находит проблемы
2. **Анализ** — генерирует actionable отчёт
3. **Исправление** — предлагает или применяет фиксы
4. **Ретест** — проверяет исправления

## Требования

- Python 3.8+
- Playwright
- Доступ к IMAP (Mail.ru)

## Workflow: Loop улучшения

```bash
# 1. Запустить тест
python scripts/site_tester.py --url https://safemind.pro/ru/

# 2. Проанализировать результаты
python scripts/fix_applier.py --report reports/2026-01-01_12-00-00/actionable.json

# 3. Применить исправления (вручную или автоматически)
# Редактируем файлы по fix_plan.json

# 4. Перетестировать
python scripts/site_tester.py --url https://safemind.pro/ru/
```

## Выходные файлы

После теста создаётся папка `reports/YYYY-MM-DD_HH-MM-SS/`:

| Файл | Назначение |
|------|------------|
| `report.md` | Читаемый отчёт для человека |
| `actionable.json` | Структурированные проблемы для AI-обработки |
| `fix_plan.json` | План автоматических исправлений |
| `screenshots/*.png` | Скриншоты адаптивности |

## Структура actionable.json

```json
{
  "url": "https://example.com",
  "total_issues": 5,
  "critical": 1,
  "major": 3,
  "minor": 1,
  "auto_fixable": 2,
  "issues": [
    {
      "id": 1,
      "severity": "critical",
      "category": "forms",
      "title": "Форма без кнопки отправки",
      "location": "order.html — форма #0",
      "fix_suggestion": "Добавить <button type=\"submit\">",
      "auto_fixable": true
    }
  ]
}
```

## Использование

### Полный тест
```bash
python scripts/site_tester.py --url https://safemind.pro/ru/ --email Art_east@internet.ru
```

### Проверка почты
```bash
python scripts/email_checker.py --check-safemind
```

### Применение исправлений
```bash
python scripts/fix_applier.py --report reports/.../actionable.json --dry-run
```

### Генерация PDF
```bash
python scripts/report_generator.py --input report.md --output report.pdf
```

## Переменные окружения

```bash
export TESTER_EMAIL="Art_east@internet.ru"
export TESTER_EMAIL_PASSWORD="your_app_password"
export TESTER_IMAP_SERVER="imap.mail.ru"
```

## Категории проблем

| Категория | Что проверяет |
|-----------|---------------|
| `navigation` | Битые ссылки, меню |
| `forms` | Поля, валидация, кнопки |
| `email` | Доставка, формат, вложения |
| `responsive` | Адаптивность, скролл |
| `performance` | Скорость, TTFB |
| `content` | JS ошибки, консоль |
| `seo` | Мета-теги, заголовки |
| `security` | HTTPS, cookie |

## Severity levels

- 🔴 **critical** — Блокирует использование
- 🟡 **major** — Ухудшает UX
- 🟢 **minor** — Косметические проблемы

## Auto-fixable проблемы

Скрипт `fix_applier.py` может автоматически предложить исправления для:
- Отсутствующих label в формах
- Отсутствующих кнопок submit
- Битых ссылок
- Отсутствующих meta-тегов
- CSS media queries

## Цикл улучшения (Loop)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Тест      │────▶│   Анализ    │────▶│  Исправление│
│  (site_tester)│    │(fix_applier)│    │  (редакция) │
└─────────────┘     └─────────────┘     └──────┬──────┘
       ▲                                        │
       └────────────────────────────────────────┘
                    (ретест)
```

Каждый цикл генерирует новый отчёт для сравнения прогресса.
