**Мантра:** Если не в git — его не существует.

---

## Skill Design — проектирование skills

**Методичка:** `docs/references/skill-design-guide-utov.pdf`
**Автор:** Илья Утов (Gorilla Under the Hood)
**Что даёт:**
- Когда создавать skill, а когда хватит prompt / проектной инструкции / subagent
- 4 критерия оценки кандидата (частота, цена разброса, стабильность, проверяемость)
- Контракт поведения (активация, вход, границы, режимы, выход, человеческое подтверждение)
- Eval-кейсы и диагностика сбоев
- Перенос между агентными средами (Claude Code, Codex, etc.)

**Когда использовать:** Перед созданием нового skill — чтобы убедиться, что задача стоит оформления, и спроектировать контракт.

**Техническая сборка skill:** см. `skill-creator` (OpenClaw) — init_skill.py, package_skill.py, структура папок.

---

## Project Templates

**Plan.md** — шаблон планирования сложных задач  
`templates/Plan.md`

**State Machine** — фазы выполнения скиллов  
`docs/state-machine.md`

**HARNESS.md** — структура проекта для агентов  
Пример: `projects/drawings-to-vor/HARNESS.md`

---

## Skill Repositories on GitHub

**Правило:** Каждый skill пушится в отдельный GitHub-репозиторий. При любом улучшении здесь — сразу `git commit && git push`.

| Skill | Repo | Описание | Синхронизация |
|-------|------|----------|---------------|
| delo-tech | `github.com/kimicito/delo-tech-skill` | Автоматизация ДЕЛО ТЕХ (rlisystems.ru/conterra/) | `scripts/sync-delo-tech.sh` |

**Workflow для обновления (subtree):**
```bash
# Автоматическая синхронизация
bash scripts/sync-delo-tech.sh

# Или вручную:
cd /root/.openclaw/workspace
git subtree push --prefix=skills/delo-tech delo-tech-skill master
```

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



## Connected Integrations (Активные интеграции)

### 📧 Yandex Email — artem.avyan@yandex.com
- **Тип:** IMAP/SMTP через skill `imap-smtp-email`
- **Статус:** ✅ Подключено и работает
- **Настройки:** `~/.openclaw/kimi-skills/imap-smtp-email/.env`
- **App Password:** `fnjqyitphxxielho` (mail/imap/smtp)
- **Что умеет:**
  - Читать входящие (`check`, `fetch`)
  - Искать по ящику (`search`)
  - Отправлять письма (`send`)
  - Скачивать вложения (`download`)
- **Важно:** IMAP должен быть включён в настройках Yandex → Почтовые программы

### 📂 Yandex Disk — artem.avyan@yandex.com
- **Тип:** WebDAV + OAuth
- **Статус:** ✅ Подключено и работает
- **Настройки:** `~/.openclaw/kimi-skills/yandex-disk-webdav.env`
- **App Password:** `scygsyeseepfchkv` (files/webdav)
- **URL:** `https://webdav.yandex.ru`
- **Что умеет:**
  - Список файлов и папок (`PROPFIND`)
  - Скачивание (`GET`)
  - Загрузка (`PUT`)
  - Создание папок (`MKCOL`)

### 🧠 Dashscope / Alibaba Qwen (OCR)
- **Тип:** REST API для AI-распознавания изображений
- **Статус:** ✅ Подключено и работает
- **API Key:** в `~/.openclaw/workspace/.env`
- **Базовый URL:** `https://ws-tgqwfcamlhhgyuu2.ap-southeast-1.maas.aliyuncs.com`
- **Что умеет:**
  - OCR (распознавание текста с изображений)
  - Распознавание чертежей и схем
  - Извлечение структурированных данных из документов
- **Используется в:** `projects/drawings-to-vor/` — извлечение ВОР (ведомость объёмов работ)

### 🐙 GitHub (PAT)
- **Тип:** GitHub API через Personal Access Token
- **Статус:** ✅ Подключено и работает
- **Токен:** в `~/.openclaw/workspace/.env`
- **Репозитории:**
  - `github.com/kimicito/openclaw-workspace.git` (branch: `master`, remote: `workspace`)
  - `github.com/kimicito/drawings-to-vor.git` (branch: `master`, remote: `origin`)
- **Что умеет:**
  - Push/pull репозиториев
  - Создание issues/PR
  - Actions (CI/CD)
  - Хранение кода и бэкапов

### 📊 Yandex Metrika
- **Тип:** REST API аналитики
- **Статус:** ✅ Подключено и работает
- **Токен + Client ID/Secret:** в `~/.openclaw/workspace/.env`
- **Счётчики:**
  - `92824982` — logistoria
  - `30201489` — supplychains
  - `45030274` — crossdoc
- **Что умеет:**
  - Получать статистику посещаемости
  - Источники трафика
  - Популярные страницы
  - Данные в реальном времени

### 🖥️ SafeMind Server (Timeweb Cloud)
- **Хостинг:** timeweb.cloud
- **IP:** `200.165.227.84` (IPv6: `2a03:6f00:a::2:1bf7`)
- **SSH:** `ssh root@200.165.227.84`
- **Root-пароль:** `gN8J__WG#P88wf`
- **Нода:** `kmnvm-737`
- **Закрытые порты:** 2525, 3389, 465, 25, 389, 587, 53413
- **Сайт:** https://safemind.pro
- **Статус:** требует перезапуска сервиса при сбоях

### 📱 Instagram API + Facebook Page
- **Тип:** Meta Graph API
- **Статус:** ✅ Токен есть (проверить актуальность при использовании)
- **Настройки:** `projects/ai-nontechnical-course/.env`
  - `INSTAGRAM_ACCESS_TOKEN`
  - `INSTAGRAM_BUSINESS_ID=17841439161166578`
  - `FACEBOOK_PAGE_ID=1201091379758387`
- **Что умеет:**
  - Публикация постов/сторис
  - Ответы на комментарии
  - Получение статистики взаимодействий

### 🤖 Telegram Bot (@supplychains)
- **Тип:** Bot API
- **Статус:** ✅ Подключено и работает
- **Настройки:** `projects/supplychains-bot/.env`
  - `TELEGRAM_BOT_TOKEN`
  - `ADMIN_CHAT_ID=143946238`
  - `CHANNEL_ID=@supplychains`
- **Что умеет:**
  - Рассылка уведомлений подписчикам канала
  - Интерактивные квизы и опросы
  - Приём заявок/обратной связи
  - Автоответы на частые вопросы

### 📋 Правило использования
При задачах, связанных с:
- **Почта** → использовать Yandex Email
- **Файлы/хранилище** → использовать Яндекс.Диск
- **Распознавание документов** → использовать Dashscope/Qwen
- **Код/бэкапы** → использовать GitHub
- **Аналитика сайтов** → использовать Yandex Metrika
- **Соцсети** → использовать Instagram/Facebook
- **Telegram** → использовать Telegram Bot

**Всегда спрашивать пользователя** перед использованием интеграций — данные чувствительные.

**Skill:** `skills/ai-job-search/SKILL.md`
