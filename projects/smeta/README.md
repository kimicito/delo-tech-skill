# Smeta Project — Infrastructure

## Структура

```
projects/smeta/
├── src/                    # Скрипты (Python)
│   ├── eval_smeta.py      # Проверка сметы
│   ├── create_bim_template.py  # Генератор шаблона БИМ
│   └── check_updates.py   # Проверка обновлений ФГИС/Минстроя
├── templates/             # Шаблоны Excel
│   ├── ШАБЛОН_ЛСР_БИМ_Методика2.xlsx
│   └── bim_template_base.xlsx
├── data/                  # Сметы и ВОР (по объектам)
│   ├── иркутск_вентиляция_2026/
│   │   ├── ВОР.xlsx
│   │   ├── смета_v1.xlsx
│   │   └── смета_итог.xlsx
│   └── README.md          # Как добавлять новые объекты
├── docs/                  # Документация
│   ├── README.md          # Главный readme (этот файл)
│   ├── ПРАВИЛО_ВОР.md     # Правило: ВОР = основной документ
│   ├── ОШИБКИ_АНАЛИЗ.md   # Анализ ошибок (исторический)
│   ├── СРАВНЕНИЕ_моя_смета_vs_профи.md  # Уроки
│   └── ARCHITECTURE.md    # Архитектура проекта
├── raw/                   # PDF сборники, нормативы (immutable)
│   └── ФЕР-20_Вентиляция.pdf
├── config/                # Конфигурация (индексы, нормативы)
│   ├── indexes.json       # Текущие индексы по регионам
│   ├── norms.json         # Нормативы НР/СП по шифрам
│   └── fer_codes.json     # Коды ФЕР (кэш)
├── scripts/               # Bash-скрипты для cron
│   └── check_updates.sh   # Проверка обновлений (cron monthly)
├── requirements.txt       # Зависимости Python
├── Makefile              # Команды проекта
└── manifest.json          # Метаданные проекта
```

## Быстрый старт

```bash
# Установка зависимостей
make install

# Проверить смету
make eval SMETA=path/to/смета.xlsx VOR=path/to/ВОР.xlsx

# Создать шаблон БИМ
make template OUTPUT=path/to/смета.xlsx REGION="Иркутск" YEAR=2026 Q=2

# Проверить обновления (вручную)
make check-updates
```

## Архитектура

### Поток данных

```
ВОР (Excel) → src/eval_smeta.py → Отчёт (FAIL/WARN/OK)
                     ↓
              src/create_bim_template.py → Шаблон БИМ (Excel)
                     ↓
              config/indexes.json → Актуальные индексы
                     ↓
              scripts/check_updates.sh → Cron (monthly)
```

### Правила

1. **ВОР в `data/`** — каждый объект в отдельной папке
2. **Сметы версионируются** — v1, v2, v3... итоговая
3. **Индексы в `config/indexes.json`** — единый источник правды
4. **PDF в `raw/`** — immutable, только для чтения
5. **Git commit после каждого изменения**

## Cron

```bash
# Проверка обновлений — 1-го числа каждого месяца в 9:00
0 9 1 * * /root/.openclaw/workspace/projects/smeta/scripts/check_updates.sh >> /var/log/smeta_updates.log 2>&1
```

## Статус

- Version: 3.0
- Created: 2026-06-28
- Updated: 2026-06-29
- Schema: BIM + FER-2020 + Methodology 2
