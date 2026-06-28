# Kimi Wiki — Schema

Паттерн: LLM-управляемая база знаний (Obsidian vault).
Wiki = persistent, compounding artifact. Не RAG.

---

## Архитектура (3 слоя)

```
┌─────────────────────────────────────────┐
│  RAW SOURCES (источники)                │
│  Неизменяемые. Статьи, отчёты, PDF.     │
│  Путь: raw/                             │
├─────────────────────────────────────────┤
│  WIKI (Markdown-заметки)                │
│  LLM создаёт и поддерживает.            │
│  Путь: wiki/                            │
│  ├─ 00-Inbox/    — входящие (сырые)     │
│  ├─ 01-Projects/ — проекты и задачи     │
│  ├─ 02-Areas/    — области              │
│  ├─ 03-Resources/— ресурсы, справочники │
│  ├─ 04-Archive/  — архив                │
│  ├─ index.md     — каталог всего        │
│  └─ log.md       — хронология           │
├─────────────────────────────────────────┤
│  SCHEMA (этот файл)                     │
│  Правила структуры, ingest, query, lint │
│  Путь: wiki/.obsidian/KIMI.md           │
└─────────────────────────────────────────┘
```

---

## Конвенции

### Формат заметок
- **YAML frontmatter** обязателен:
  ```yaml
  ---
  title: Название
  source: "URL или файл"
  date: 2026-06-28
  tags: [tag1, tag2]
  status: draft | review | done
  ---
  ```
- **Wikilinks:** `[[Note name]]` для связей
- **Tags:** `#tag` в конце заметки
- **MOC (Map of Content):** индексные заметки для навигации

### Структура папок
| Папка | Назначение |
|-------|-----------|
| `00-Inbox/` | Входящие — сырые заметки, ещё не обработанные |
| `01-Projects/` | Активные проекты (смета, презентации, исследования) |
| `02-Areas/` | Постоянные области (skills, health, finance) |
| `03-Resources/` | Справочники, заметки по источникам, Entity-страницы |
| `04-Archive/` | Завершённые проекты, устаревшее |

---

## Операции

### 1. INGEST (добавление источника)

**Триггер:** Пользователь даёт источник (ссылка, PDF, текст).

**Шаги:**
1. Сохранить источник в `raw/`
2. Прочитать и обсудить ключевые моменты с пользователем
3. Создать summary-заметку в `03-Resources/`
4. Обновить entity-страницы (если новые сущности)
5. Обновить `index.md`
6. Добавить запись в `log.md`

**Формат log-записи:**
```markdown
## [2026-06-28] ingest | WEF AI Playbook for Financial Services
- Source: https://www.weforum.org/...
- Summary: [[WEF AI Playbook 2026]]
- Entities updated: [[Agentic AI]], [[Risk Management]]
- Questions: Как применить к нашему бизнесу?
```

### 2. QUERY (запрос к базе знаний)

**Триггер:** Пользователь задаёт вопрос.

**Шаги:**
1. Прочитать `index.md` для поиска релевантных страниц
2. Прочитать найденные страницы
3. Синтезировать ответ с цитатами (`[[Page]]`)
4. **Если ответ ценный — сохранить в wiki как новую страницу**

**Форматы ответа:**
- Markdown-страница (по умолчанию)
- Сравнительная таблица
- Презентация (Marp / PPTX)
- Canvas (Obsidian canvas)

### 3. LINT (проверка здоровья wiki)

**Триггер:** По запросу пользователя или периодически.

**Что проверять:**
- [ ] Контрадикции между страницами
- [ ] Устаревшие claims (новые источники опровергли старые)
- [ ] Orphan pages (нет inbound links)
- [ ] Важные concepts без собственной страницы
- [ ] Пропущенные cross-references
- [ ] Данные, которые можно дополнить web search

**Формат lint-отчёта:**
```markdown
## [2026-06-28] lint
### Contradictions
- [[Page A]] говорит X, [[Page B]] говорит not-X

### Missing pages
- Concept "Agentic AI" mentioned in 5 pages but has no own page

### Orphans
- [[Old note]] — нет ссылок на неё
```

---

## Entity-страницы

Для каждой важной сущности — отдельная страница:
- **People** — люди (авторы, эксперты)
- **Organizations** — компании, институты
- **Concepts** — идеи, фреймворки, технологии
- **Sources** — конкретные документы, книги, отчёты

**Формат entity-страницы:**
```markdown
---
title: Agentic AI
source: "WEF AI Playbook 2026"
date: 2026-06-28
tags: [ai, concept]
status: done
---

# Agentic AI

## Definition
...

## Levels of autonomy
...

## Sources
- [[WEF AI Playbook 2026]]
- [[KBTG Case Study]]

## Related
- [[AI Governance]]
- [[Human-in-the-Loop]]
```

---

## Obsidian-плагины (рекомендуемые)

| Плагин | Назначение |
|--------|-----------|
| **Dataview** | Запросы к frontmatter (динамические таблицы) |
| **Graph View** | Визуализация связей между заметками |
| **Templater** | Шаблоны для новых заметок |
| **Marp** | Презентации из markdown |
| **Web Clipper** | Конвертация web-статей в markdown |

---

## Git backup

```bash
# Автобэкап в 3:00 AM (уже настроен)
cd /root/.openclaw/workspace && ./backup.sh "[wiki] daily backup"
```

Все заметки — plain markdown. Git отслеживает версии, ветки, коллаборацию.

---

## Правила для LLM

1. **Никогда не редактируй raw sources** — только читай
2. **Всегда обновляй index.md** после ingest
3. **Всегда пиши в log.md** — chronological, append-only
4. **Сохраняй ценные ответы** в wiki, не оставляй в чате
5. **Используй wikilinks** — `[[Page]]` вместо plain text
6. **Добавляй YAML frontmatter** — title, source, date, tags, status
7. **Периодически запускай lint** — по запросу пользователя

---

*Schema version: 1.0*
*Created: 2026-06-28*
*Pattern: https://gist.github.com/kimicito/6f33a4457b8c2c9767e960c692e6d7a3*
*LLM: Kimi (Moonshot AI)*
