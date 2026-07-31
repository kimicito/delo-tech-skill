# HARNESS Registry — Master Index

## Структура

```
HARNESS/
├── _master.md              # Общие правила для всех проектов
├── _registry.md            # Этот файл — реестр
├── ai-nontechnical-course.md
├── drawings-to-vor.md
├── instagram-automation.md
├── logistoria-website.md
├── ozon-tax-calculator.md
├── supplychains-bot.md
└── wb-tax-calculator.md
```

## Проекты

| Проект | Статус | Описание |
|--------|--------|----------|
| ai-nontechnical-course | ✅ Активен | AI-курс для не-IT |
| drawings-to-vor | ✅ Активен | OCR чертежей → ВОР |
| instagram-automation | 🔄 Настройка | Автопостинг @logistoria_edu |
| logistoria-website | ✅ Активен | Основной сайт компании |
| ozon-tax-calculator | ✅ Активен | Налоги Ozon (АУСН) |
| supplychains-bot | ✅ Активен | Telegram-бот @supplychains |
| wb-tax-calculator | ✅ Активен | Налоги Wildberries (АУСН) |

## Принцип работы

1. **Оригинал** — в проекте (`projects/<name>/HARNESS.md`)
2. **Копия** — здесь (`HARNESS/<name>.md`)
3. **Мастер-правила** — общие конвенции (`_master.md`)

## Синхронизация

При изменении оригинала:
```bash
cp projects/<name>/HARNESS.md HARNESS/<name>.md
git add HARNESS/
git commit -m "[harness] Sync <name>"
```

## Приоритет

Если конфликт:
1. Проектный HARNESS.md — специфика
2. HARNESS/<name>.md — копия специфики
3. HARNESS/_master.md — общие правила
