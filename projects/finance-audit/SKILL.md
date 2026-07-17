# Finance Audit — Subscription Killer

**Путь:** `projects/finance-audit/`
**Репо:** `github.com/kimicito/openclaw-workspace`

## Что делает

Анализирует личные/компанию финансы: подписки, дубликаты, аномалии, рекомендации по экономии.

- **Вход:** CSV выписки банка / email с чеками / ручной ввод
- **Выход:** Отчёт: что лишнее, сколько переплата, рекомендации

## Запуск

```bash
# Ручной анализ CSV
python scripts/analyze.py --input data/transactions.csv --output reports/audit_$(date +%F).md

# Авто через OpenClaw (cron)
# Настроено в heartbeat: проверять подписки раз в неделю
```

## Структура

```
finance-audit/
├── data/               # CSV, выписки (не в git — .gitignore)
├── reports/            # Генерируемые отчёты (не в git)
├── scripts/
│   ├── analyze.py      # Основной анализ
│   └── subscription_killer.py  # Поиск дубликатов подписок
├── config/
│   └── categories.json # Категории трат
└── SKILL.md            # Этот файл
```

## Категории анализа

1. **Подписки** — recurring payments, дубликаты (3 облака, 2 стриминга)
2. **Аномалии** — резкие скачки (AWS +40%, Uber x2)
3. **Дубликаты** — два SaaS с одной функцией
4. **Рекомендации** — downgrade, cancel, switch

## Интеграция с OpenClaw

```
Пользователь: /audit_finance
OpenClaw: Запускает analyze.py → читает CSV → шлёт Telegram отчёт
```

## Память

- Отчёты сохраняются в `reports/` для истории
- Сравнение месяц-к-месяцу: trend detection

## Безопасность

- Финансовые данные — только локально, не в git
- `.gitignore` строгий

---
_Создано: 2026-07-18_
