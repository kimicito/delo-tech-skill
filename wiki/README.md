# Wiki / Knowledge Base

База знаний в формате Obsidian vault (Markdown + wikilinks).

## Структура

```
wiki/
├── 📁 00-Inbox/          # Входящие заметки (необработанные)
├── 📁 01-Projects/       # Проекты и задачи
├── 📁 02-Areas/          # Области ответственности
├── 📁 03-Resources/      # Ресурсы и справочники
├── 📁 04-Archive/        # Архив
└── 📄 README.md          # Этот файл
```

## Принципы

1. **Всё в Markdown** — читаемо без Obsidian
2. **Wikilinks** — `[[Note name]]` для связей
3. **Tags** — `#tag` для категоризации
4. **MOC (Map of Content)** — индексные заметки для навигации

## Добавление заметки

```bash
obsidian-cli create "Resources/AI in Finance" --content "..."
```

## Поиск

```bash
obsidian-cli search "AI"
obsidian-cli search-content "financial services"
```

## Git backup

Все заметки автоматически бэкапятся в GitHub (3:00 AM).
