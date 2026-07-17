# Multi-Agent Research System

**Путь:** `projects/multi-agent-research/`
**Репо:** `github.com/kimicito/openclaw-workspace`

## Что делает

Параллельно запускает 3-6 суб-агентов, каждый исследует свою область. Координатор собирает результаты в единый брифинг.

**Пример для закупок:**
- Агент 1: Мониторинг цен (ЦИАН, fgiscs, Авито)
- Агент 2: Регуляторные изменения (pravo.gov.ru, Минстрой)
- Агент 3: Новые поставщики и тендеры

## Архитектура

```
┌─────────────┐
│ Coordinator │ ← запускает, ждёт, собирает
└──────┬──────┘
       │ sessions_spawn (параллельно)
   ┌───┴───┬───────┐
   ▼       ▼       ▼
Agent1 Agent2 Agent3
   │       │       │
   └───────┴───────┘
          │
          ▼
    Briefing (Telegram)
```

## Запуск

### Через Telegram
```
/research тема: "цемент М400 цены поставщики"
```

### Через CLI (ручной)
```bash
python scripts/coordinator.py --topic "цемент М400" --agents config/agents.json
```

### Через OpenClaw (авто)
```
# В cron: каждый день 9:00
0 9 * * * openclaw run projects/multi-agent-research --topic "daily_procurement"
```

## Структура

```
multi-agent-research/
├── agents/
│   ├── price_monitor.py      # Мониторинг цен
│   ├── regulation_watcher.py # Регуляторка
│   └── supplier_finder.py    # Поиск поставщиков
├── scripts/
│   └── coordinator.py        # Оркестратор
├── config/
│   └── agents.json           # Конфиг агентов
├── reports/                  # Выход (не в git)
└── SKILL.md                  # Этот файл
```

## Конфигурация агентов (agents.json)

```json
{
  "coordinator": {
    "model": "kimi-k2p6",
    "timeout_seconds": 300,
    "max_agents": 4
  },
  "agents": [
    {
      "id": "price",
      "name": "Price Monitor",
      "task": "Найди актуальные цены на {topic}. Источники: fgiscs.minstroyrf.ru, Авито, Пульс цен. Формат: таблица (поставщик, цена, дата)",
      "tools": ["browser", "kimi_search"]
    },
    {
      "id": "regulation",
      "name": "Regulation Watcher",
      "task": "Проверь изменения в ГОСТ, СП, приказах Минстроя по теме {topic}. Источники: pravo.gov.ru, docs.cntd.ru",
      "tools": ["browser", "web_fetch"]
    },
    {
      "id": "suppliers",
      "name": "Supplier Finder",
      "task": "Найди новых поставщиков {topic} в Москве и МО. Источники: Авито, 2ГИС, Яндекс.Карты",
      "tools": ["kimi_search", "browser"]
    }
  ]
}
```

## Как работает coordinator

1. **Parse** — читает agents.json, подставляет `{topic}`
2. **Spawn** — `sessions_spawn` для каждого агента (runtime="subagent")
3. **Wait** — `sessions_yield` пока все не вернут результат
4. **Synthesize** — LLM объединяет результаты в briefing
5. **Deliver** — Telegram / сохранение в reports/

## Требования

- **RAM:** 1.5-2G при параллельном запуске 3-4 агентов
- **Время:** 2-5 минут на полный цикл
- **API:** зависит от агентов (browser, search, etc.)

## Пример выхода (briefing)

```markdown
# Research Briefing: Цемент М400
**Date:** 2026-07-18

## Prices (Agent: price)
| Поставщик | Цена | Дата |
|-----------|------|------|
| ООО СтройМат | 4,200 ₽ | 2026-07-17 |
| ООО ЦементСнаб | 4,350 ₽ | 2026-07-16 |

## Regulations (Agent: regulation)
- ⚠️ ГОСТ 2026-3 вступает в силу 2026-08-01. Изменения в прочности.

## Suppliers (Agent: suppliers)
- Новый поставщик в Раменском: ООО БетонЦентр, тел. +7...

## Summary
Рекомендация: закупить до 1 августа по старому ГОСТ. Мониторить цену у ООО СтройМат.
```

## Безопасность

- Каждый агент — изолированная сессия (subagent)
- Ошибка одного агента не ломает остальных
- Timeout на каждом агенте (не ждём вечно)

---
_Создано: 2026-07-18_
