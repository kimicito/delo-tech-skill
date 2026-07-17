# Corporate Reports Analyzer

**Путь:** `projects/corporate-reports/`
**Репо:** `github.com/kimicito/openclaw-workspace`

## Что делает

Анализирует квартальные и годовые отчёты компании: P&L, Balance Sheet, Cash Flow.

- **Вход:** PDF, Excel (.xlsx), CSV с отчётами
- **Выход:** Markdown отчёт с динамикой, маржами, аномалиями
- **Автозагрузка:** Может сам скачать отчёт с сайта и проанализировать

## Возможности

| Анализ | Описание |
|--------|----------|
| **QoQ** | Квартал к кварталу (Q2 vs Q1) |
| **YoY** | Год к году (Q2 2026 vs Q2 2025) |
| **Маржинальность** | Gross, Operating, Net margin |
| **Динамика расходов** | Какие статьи растут/падают |
| **Аномалии** | Скачки >30% без объяснений |
| **Тренды** | 4-8 кварталов истории |

## Структура

```
corporate-reports/
├── data/               # Excel/CSV/PDF отчёты (не в git)
├── reports/            # Генерация (не в git)
├── scripts/
│   ├── quarterly_analyzer.py   # Основной анализ
│   └── fetch_and_analyze.py    # Скачать с сайта → проанализировать
├── config/
│   └── report_templates.json
└── SKILL.md
```

## Запуск

### Локальный файл
```bash
# Анализ квартального отчёта (Excel/CSV/PDF)
python scripts/quarterly_analyzer.py --input data/q2_2026.xlsx --output reports/analysis.md

# Анализ PDF отчёта
python scripts/quarterly_analyzer.py --input data/annual_report_2025.pdf --output reports/analysis.md
```

### Скачать с сайта и проанализировать
```bash
# Прямая ссылка на файл
python scripts/fetch_and_analyze.py --url https://company.com/reports/q2_2026.pdf --direct

# Искать отчёты на странице
python scripts/fetch_and_analyze.py --url https://company.com/investors/reports
```

## Формат входных данных

### P&L (Excel/CSV)
| Статья | Q1 2025 | Q2 2025 | Q3 2025 | Q4 2025 |
|--------|---------|---------|---------|---------|
| Выручка | 1000000 | 1200000 | ... | ... |
| Себестоимость | 600000 | 700000 | ... | ... |
| Расходы на персонал | 200000 | 220000 | ... | ... |
| ... | ... | ... | ... | ... |

### Balance Sheet
| Статья | Q1 | Q2 | Q3 | Q4 |
|--------|----|----|----|----|
| Оборотные активы | ... | ... | ... | ... |
| Внеоборотные активы | ... | ... | ... | ... |
| Краткосрочные обязательства | ... | ... | ... | ... |

## Требования

- **RAM:** 300-800 MB (только во время анализа)
- **Время:** 10-30 секунд на отчёт
- **Disk:** <10 MB (скрипт + конфиг)

---
_Создано: 2026-07-18_
