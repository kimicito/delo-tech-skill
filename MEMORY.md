# MEMORY.md — Долгосрочная память

_Курированные знания. Дистиллированная мудрость из дневных заметок._

> 📁 **Новая структура памяти:** см. `memory/brain/`, `memory/people/`, `memory/projects/`, `memory/templates/`

## Политики памяти

### Temporal Decay (увядание)

- Записи в **memory/YYYY-MM-DD.md** старше 7 дней помечаются как «устаревшие»
- Session-логи старше 30 дней архивируются в `memory/archive/`
- Global MEMORY.md (этот файл) — **не увядает**, это курированная память

### Auto-Dream (авто-консолидация)

Каждые 3–5 дней или после 3+ сессий:
1. Прочитать все `memory/2026-*.md`
2. Извлечь решения, уроки, паттерны
3. Дедуплицировать и структурировать
4. Добавить в этот MEMORY.md под соответствующие заголовки
5. Очистить дневные заметки от дублирующей информации

### Staleness Notes

При поиске памяти старше 7 дней — добавлять пометку:
> ⚠️ Эта информация из [дата]. Проверьте актуальность перед использованием.

## Структура

### Preferences (предпочтения пользователя)
_(Заполняется по мере изучения)_

### Project Context (контекст проектов)
_(Ключевые архитектурные решения, conventions)_

### Debugging Patterns (паттерны отладки)
_(Что работало, что — нет)_

### Lessons Learned (уроки)
_(Ошибки и как их избежать)_

### API Discoveries (открытия)
_(Новые инструменты, endpoint'ы, библиотеки)_

- **CLI-Anything** (HKUDS): Фреймворк для создания CLI-обёрток (harnesses) вокруг любого ПО, чтобы AI-агенты управляли им через текстовые команды. Форк: `github.com/kimicito/CLI-Anything`. Реестр: CLI-Hub (`pip install cli-anything-hub`). Уже готовы harnesses для FreeCAD, Blender, QGIS, ArcGIS, Kdenlive, Shotcut, Obsidian, Zotero, n8n, ChromaDB, LibreOffice и 200+ других. **Использовать при задачах, требующих управления desktop-software или CAD/медиа/документами.**

## Текущие проекты

### Skills on GitHub (2026-08-21)

**Правило:** Каждый skill, созданный или улучшенный в этом workspace, должен быть запушен на GitHub в отдельный репозиторий.

| Skill | Repo | Status |
|-------|------|--------|
| delo-tech | `github.com/kimicito/delo-tech` | ✅ pushed |

**Команда для нового skill:**
```bash
cd skills/<skill-name>
git init
git add .
git commit -m "Initial commit"
gh repo create <skill-name> --public --description "..." --source=. --remote=origin --push
```

**Команда для обновления:**
```bash
cd skills/<skill-name>
git add .
git commit -m "[fix/feature] description"
git push origin master
```
- **Yandex Email** (artem.avyan@yandex.com) — IMAP/SMTP через `imap-smtp-email` skill, статус: ✅ активно
- **Yandex Disk** (artem.avyan@yandex.com) — WebDAV, статус: ✅ активно
- Конфиги: `~/.openclaw/kimi-skills/imap-smtp-email/.env` и `yandex-disk-webdav.env`

### safemind.pro (2026-08-16)
- **Status:** ✅ Recovered and operational
- **Server:** Nimble Cepheus (Timeweb Cloud), IP: 200.165.227.84
- **DNS:** REG.RU (updated A-record from old IP 85.239.59.8 to current 200.165.227.84)
- **Nginx:** SSL via Let's Encrypt, proxies to backends on ports 3001, 3002, 8002
- **Full recovery log:** `memory/projects/safemind-pro.md`
- **Key lesson:** If server shows "В сети" but SSH timeout → hard reboot (power off/on) fixes boot hang
- **Quick access:** `ssh root@200.165.227.84` (password in TOOLS.md / project file)


- **MarketPlays**: денежные значения ×10, старт 40 000 ₽, 20 товаров, 15/30 раундов
- **AI-курс**: 10 уровней, русский язык, Pagefind search

### ai-nontechnical-course
- Уровень 7 переделан на «ИИ для закупщика» (3 урока: on-prem / cloud / hybrid)
- Каждый урок: практические промпты + квиз
- **Правило:** при добавлении нового уровня, урока или вкладки — обязательно добавлять запись на страницу «Что нового» (updates.html) на всех языках (RU, EN, FR, ZH). Иначе пользователи не узнают об обновлениях.

## История изменений

| Дата | Что изменилось |
|------|----------------|
| 2026-07-16 | Создан MEMORY.md с политиками temporal decay и auto-dream |

---

## System Rules (системные правила)

### 🚨 Дисковое пространство
- **Критический порог:** 98%+
- **Действие:** Немедленно сообщить пользователю и начать очистку
- **Автоочистка:** Скрипт `scripts/cleanup-checkpoints.sh`
  - Оставляет последние 3 чекпоинта на сессию
  - Не влияет на: skills, проекты, .env, конфиги, MEMORY.md
  - Удаляет только историю чатов (session checkpoints)
  - Запуск: `bash scripts/cleanup-checkpoints.sh`
  - Симуляция: `bash scripts/cleanup-checkpoints.sh --dry-run`
- **Что очищать вручную при необходимости:**
  1. Reset-файлы старше 30 дней
  2. Медиа inbound старше 30 дней
  3. Логи старше 7 дней
- **История:** 
  - 2026-08-03 — диск был на 100%, очищено ~14Гб старых чекпоинтов
  - 2026-08-15 — диск снова 100%, очищено ~14Гб (80 чекпоинтов одной сессии)

### 🔔 Heartbeat Checks
- При каждом heartbeat проверять `df -h`
- Если >90% — предупредить пользователя
- Если >98% — критическое уведомление + автоочистка
