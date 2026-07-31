# _master.md — Общие правила для всех проектов

## Git-дискиплина (обязательно!)

- **ВСЕ изменения в git сразу**
- Формат коммита: `[тип] описание`
  - `[course]` — курс
  - `[fix]` — исправление
  - `[skill]` — новый/обновлённый скилл
  - `[memory]` — память
  - `[project]` — проект
- Push в `workspace master` после каждого коммита

## Структура памяти

```
memory/
├── brain/           # Курированные знания
│   ├── api-discoveries.md
│   ├── decisions.md
│   ├── gotchas.md
│   ├── patterns.md
│   ├── policies.md
│   └── rules.md
├── people/          # Люди
├── projects/        # Проекты (контекст)
├── templates/       # Шаблоны
│   ├── decision.md
│   ├── incident.md
│   ├── meeting.md
│   ├── person.md
│   └── project.md
└── YYYY-MM-DD.md   # Ежедневные заметки (append!)
```

## Языки

- **RU** — основной (контент, документация)
- **EN** — международный (курс, сайт)
- **FR, ZH, ES** — по запросу

## Безопасность

- Credentials → `secrets/` (не в git!)
- Личные проекты → не упоминать в публичных файлах
- API ключи → `.env`, никогда в коде

## Работа с проектами

1. **Читать HARNESS.md первым делом**
2. **Проверять чеклист** перед коммитом
3. **Обновлять updates/changelog** при изменениях
4. **Не ломать URL** — старая структура = навсегда

## Контакты

- **Владелец:** Artur A. (tagartur)
- **Репозиторий:** github.com/kimicito/openclaw-workspace
