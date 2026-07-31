# HARNESS Registry — Master Index

## Структура

```
HARNESS/
├── _master.md              # Общие правила для всех проектов
├── ai-nontechnical-course.md
├── drawings-to-vor.md
├── instagram-automation.md
├── logistoria-website.md
├── wb-tax-calculator.md
├── ozon-tax-calculator.md
└── supplychains-bot.md
```

## Принцип работы

1. **Оригинал** — в проекте (`projects/<name>/HARNESS.md`)
2. **Копия** — здесь (`HARNESS/<name>.md`)
3. **Мастер-правила** — общие конвенции (`_master.md`)

## Синхронизация

При изменении оригинала:
```bash
# Ручная синхронизация
cp projects/<name>/HARNESS.md HARNESS/<name>.md
git add HARNESS/
git commit -m "[harness] Sync <name>"
```

## Приоритет

Если конфликт:
1. Проектный HARNESS.md — специфика
2. HARNESS/<name>.md — копия специфики
3. HARNESS/_master.md — общие правила
