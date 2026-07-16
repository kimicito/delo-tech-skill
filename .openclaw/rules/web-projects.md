# Web Projects — правила

Для: logistoria-website, ai-nontechnical-course, kadena-game, ai-native

## Стек и conventions

- **HTML**: семантические теги, доступность (aria-label)
- **CSS**: кастомные свойства, mobile-first, max-width 1200px
- **JS**: vanilla, ES6+, избегать jQuery
- **Сборка**: Pagefind для поиска (если используется)

## Git

- Commit format: `[тип] описание — YYYY-MM-DD HH:MM`
- Типы: `[course]`, `[fix]`, `[memory]`, `[skill]`, `[project]`, `[task]`, `[backup]`
- Push: `git push workspace master` (основной репо)
- Для gh-pages: `cd projects/PROJECT && git push origin gh-pages`

## Файловая структура

```
project/
  index.html          # Главная
  style.css           # Общие стили
  catalog.html        # Каталог (если курс)
  glossary.html       # Глоссарий
  lessons/
    01-lesson/
      index.html      # Урок
  pagefind/           # Индекс поиска (генерируется)
```

## Pagefind

После изменений HTML-файлов:
```bash
cd projects/PROJECT && npx pagefind --source . --glob "**/*.html"
```

## Квизы

- Минимум 3 вопроса на урок
- Формат: встроенный JS, без внешних библиотек
- Правильные ответы: открытые + выбор вариантов
