# .openclaw/rules/

Per-directory правила для проектов. Загружаются автоматически при работе в соответствующей директории.

## Иерархия

```
~/.openclaw/workspace/
  AGENTS.md                    # Глобальные правила (все проекты)
  .openclaw/
    rules/
      web-projects.md          # Правила для веб-проектов
      python-projects.md       # Правила для Python-скриптов
      skills.md                # Правила для skills
  projects/
    logistoria-website/
      AGENTS.md                # Проект-специфичные правила
    ai-nontechnical-course/
      AGENTS.md                # Проект-специфичные правила
    drawings-to-vor/
      AGENTS.md                # Проект-специфичные правила
```

## Приоритет

Директория глубже = приоритет выше. Конфликт разрешается в пользу более глубокого файла.

## Как добавить правила для нового проекта

1. Создать `AGENTS.md` в корне проекта
2. Или создать `.md` файл в `.openclaw/rules/` и добавить ссылку

## Текущие правила

- `web-projects.md` — для logistoria-website, ai-nontechnical-course, kadena-game
- `python-projects.md` — для drawings-to-vor, skills
- `skills.md` — conventions для skills (SKILL.md, structure, etc.)
