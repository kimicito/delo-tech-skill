**Мантра:** Если не в git — его не существует.

---

## Project Templates

**Plan.md** — шаблон планирования сложных задач  
`templates/Plan.md`

**State Machine** — фазы выполнения скиллов  
`docs/state-machine.md`

**HARNESS.md** — структура проекта для агентов  
Пример: `projects/drawings-to-vor/HARNESS.md`

---

## Browser Scraping (геоблок, JS-рендеринг)

**Repo:** `github.com/kimicito/browser-scraping`
**Когда:** curl 403/5xx, SPA без контента, геоблок (gge.ru)
**Команды:** `browser navigate` → `snapshot` → клики по дереву → скриншот

**Проверенные сайты:**
- `fgiscs.minstroyrf.ru` — ФГИС ЦС, индексы, расценки
- `pravo.gov.ru` — приказы Минстроя, экспорт RTF

---

## Price Comparison Skill

**Repo:** `github.com/kimicito/price-comparison-skill`
**Когда:** закупки, сравнение аналогов, категорийные шаблоны
**Что делает:** inline eval, dual analogs, категорийные матрицы

---

## Drawing OCR / VOR Extraction

**Repo:** `github.com/kimicito/drawings-to-vor` (separate project)
**Local:** `projects/drawings-to-vor/`

**Workflow:**
1. `python3 preprocess.py input.tiff` — tile into 1000×1000
2. `python3 tile_ocr.py --tiles-dir tiles/ --output ocr_result.json` — OCR via Qwen-VL
3. `python3 extract_vor.py --ocr-json ocr_result.json --type piles` — extract VOR (ВОР)

**API:** Alibaba Qwen-VL-OCR (key in `~/.openclaw/workspace/.env`)

---

## CLI-Anything (Desktop Software Harnesses)

**Repo:** `github.com/kimicito/CLI-Anything` (fork от HKUDS)
**Hub:** `pip install cli-anything-hub`
**Docs:** https://hkuds.github.io/CLI-Anything/

**Что это:** Фреймворк для создания CLI-обёрток (harnesses) вокруг любого ПО, чтобы AI-агенты управляли им через текстовые команды. Не замена скриптам — стандартный разъём для AI-агентов.

**Готовые harnesses, релевантные проектам:**
- **CAD/3D:** FreeCAD, Blender, SolidWorks, 3MF
- **GIS:** QGIS, ArcGIS Pro
- **Медиа:** Kdenlive, Shotcut, Openscreen, MiniMax (TTS)
- **Документы:** LibreOffice, Obsidian, Zotero, Joplin
- **Автоматизация:** n8n, Dify Workflow, ChromaDB (векторный поиск)

**Когда использовать:**
- Задача требует управления desktop-software из AI-агента
- Нужна интеграция CAD/медиа/документов в пайплайн OpenClaw
- Хочешь избежать ручного API-программирования для каждого инструмента

**Когда НЕ использовать:**
- Простые REST API — проще напрямую
- Задачи, где уже есть готовый скилл

**Ключевые фичи:**
- **OpenClaw — нативная поддержка.** Harnesses работают как скиллы без адаптеров.
- **CLI-Hub = пакетный менеджер.** `cli-hub install freecad` как `apt install`. Не клонировать, не собирать — просто ставить и запускать.
- **Авто-SKILL.md.** Каждый harness генерирует документацию автоматически — OpenClaw сразу понимает команды.
- **7-фазовый генератор.** Нужно обернуть своё ПО? Шаблон HARNESS.md → готовый CLI + тесты + SKILL.md.
- **Реестр растёт ежедневно.** 200+ harnesses, новые через PR. Не ждём официальной интеграции — берём готовое.

---

## WB Tax Calculator (РВБ / Wildberries)

**Skill:** `skills/wb-tax-calculator/`
**Docs:** `skills/wb-tax-calculator/SKILL.md`
**Script:** `skills/wb-tax-calculator/calculator.py`
**Tests:** `skills/wb-tax-calculator/tests/`

**Input files:**
1. Реестр еженедельных операций (Excel/CSV)
2. Детализация отчётов (Excel/CSV)
3. Уведомления о выкупе (Excel/CSV, optional)
4. Доп. расходы из Аналитики (optional)

**Run:**
```bash
python skills/wb-tax-calculator/calculator.py --registry реестр.xlsx --details детализация.xlsx
```

**Tests:**
```bash
cd skills/wb-tax-calculator && python3 tests/test_calculator.py
```

---

## Ozon Tax Calculator (ООО Интернет Решения)

**Skill:** `skills/ozon-tax-calculator/`
**Docs:** `skills/ozon-tax-calculator/SKILL.md`
**Script:** `skills/ozon-tax-calculator/calculator.py`

**Input files:**
1. Отчёт о реализации (Excel/CSV)
2. Отчёт о взаиморасчётах (Excel/CSV)

**Run:**
```bash
python skills/ozon-tax-calculator/calculator.py --realization отчёт_реализации.xlsx --mutual_settlement отчёт_взаиморасчётов.xlsx
```

---

## Git Notes

- **Main repo:** `github.com/kimicito/openclaw-workspace.git` (branch: `master`, remote: `workspace`)
- **Drawing repo:** `github.com/kimicito/drawings-to-vor.git` (branch: `master`, remote: `origin`)
- **Push main:** `git push workspace master`
- **Push drawing:** `cd projects/drawings-to-vor && git push origin master`

---

## Ozon Tax Calculator (ООО «Интернет Решения»)

**Skill:** `workspace/skills/ozon-tax-calculator/`
**Запуск:** Пользователь говорит «Рассчитай налог Ozon»

**Что нужно запросить:**
1. Отчёт о реализации (Excel/CSV) — столбцы: «Возвращено на сумму, руб.», «Выплаты по механикам лояльности партнёров, руб.»
2. Отчёт о взаиморасчётах (Excel/CSV) — столбец: «Суммы дебиторской задолженности»

**Алгоритм:**
- Возвраты = Σ(«Возвращено на сумму») + Σ(«Выплаты по механикам лояльности»)
- Услуги = Σ строк «Отчёт о реализации», «Акт выполненных работ», «Отчёт о перевыставлении услуг», «Акт об оказанных услугах» из взаиморасчётов
- В ЛКН АУСН: Приход = Услуги + Возвраты, Возврат прихода = Возвраты, Расход = Услуги

**Команда:**
```bash
python skills/ozon-tax-calculator/calculator.py --realization отчет.xlsx --mutual взаиморасчеты.xlsx
```

---

## WB Tax Calculator (РВБ / Wildberries)

**Skill:** `workspace/skills/wb-tax-calculator/`
**Запуск:** Пользователь говорит «Рассчитай налог РВБ»

**Что нужно запросить:**
1. Реестр еженедельных операций (Excel/CSV) — столбцы: Тип отчета, Продажа, Итого к оплате
2. Детализация отчётов (Excel/CSV) — столбцы: Тип документа, Вайлдберриз реализовал Товар (Пр)
3. Уведомления о выкупе (Excel/CSV, опционально) — столбец: Сумма
4. Доп. расходы (потери/подмены/дефекты) из Аналитики → Доходы и расходы

**Алгоритм:**
- Комиссия (Основной) = Σ(Продажа) − Σ(Итого к оплате)
- Комиссия (Выкупы) = Сумма Уведомления − Сумма в реестре
- Итого комиссия = Основной + Выкупы + Доп. расходы
- Возвраты = Σ из детализации (фильтр по «возврат»)
- ЛКН АУСН: взаимозачёт на сумму комиссии, возвраты отдельно

**Команда:**
```bash
python skills/wb-tax-calculator/calculator.py --registry реестр.xlsx --details детализация.xlsx [--purchases уведомления.xlsx --losses 9104.28]
```

---

## Agent Safety Rules (from Claudecourse research)

### 1. Plan Mode — «Сначала план, потом действие»
Для задач, затрагивающих **более 3 файлов** или **более 5 шагов**:
1. Составь план из 3–5 пунктов
2. Покажи пользователю на одобрение
3. Только после «да» или правок — выполняй

Исключение: пользователь явно сказал «сделай без вопросов».

### 2. Опасные команды — запрет автоматического выполнения
Никогда не выполняй без подтверждения пользователя:
- `rm -rf *`, `rm -rf /`, `rm -rf ~`
- `mkfs*`, `dd`, `fdisk`
- `git push --force`, `git push -f`
- `git reset --hard`
- Любая команда с `> /dev/null` или pipe в `/dev/null` с подозрительным источником
- Любая команда, удаляющая `.git`, `SOUL.md`, `AGENTS.md`, `USER.md`

### 3. Таймауты на exec
Все `exec` с потенциально долгими операциями — с таймаутом **60 секунд**.
Если команда зависла — возвращай ошибку, а не жди вечно.

### 4. Read-only суб-агенты для анализа
При анализе больших объёмов данных (PDF, логи, отчёты) используй `sessions_spawn` в режиме **read-only**:
- Суб-агент читает и анализирует
- Возвращает сводку
- Главный агент принимает решения

Это защищает от случайных изменений при анализе.

### 5. Git Safety
Перед `git push`:
1. Проверь `git remote -v` — правильный remote?
2. Проверь `git branch` — правильная ветка?
3. Для `--force` — всегда спрашивай подтверждение

Правило: **никогда `git push --force` без явного разрешения пользователя**.

### 6. Output Truncation
Если вывод `exec` превышает 500 строк — обрезай до `tail -100` или `head -50` + пояснение «вывод обрезан, полный лог при необходимости».
Это экономит токены и предотвращает переполнение контекста.

### 7. Файлы-запреты (Never modify without explicit user request)
- `SOUL.md` — личность агента
- `AGENTS.md` — правила поведения
- `USER.md` — профиль пользователя
- `IDENTITY.md` — идентичность
- `MEMORY.md` — долгосрочная память

Эти файлы можно **читать**, но редактировать **только если пользователь явно попросил**.

---
*Добавлено: 2026-07-16. Источник: адаптация паттернов Claude Code (https://github.com/justxor/Claudecourse/).*


**Skill:** `skills/ai-job-search/`
**Docs:** `skills/ai-job-search/SKILL.md`
**Profile:** `memory/candidate-profile.md`
**Scraper:** `skills/ai-job-search/scripts/hh_scraper.py`

**Workflow:**
1. `/setup` — заполнить профиль (через Telegram)
2. `/scrape` — поиск вакансий на hh.ru через kimi_search/browser
3. `/apply <url>` — оценка + CV + сопроводительное письмо

**Job search:**
```
kimi_search: "site:hh.ru [query] вакансия"
# или
browser: open https://hh.ru/search/vacancy?text=[query]
```

**Адаптация:**
- Заменён Claude Code → OpenClaw subagents
- LaTeX → Markdown (проще для OpenClaw)
- Датские порталы → hh.ru (русский рынок)
- Slash commands → Telegram команды
