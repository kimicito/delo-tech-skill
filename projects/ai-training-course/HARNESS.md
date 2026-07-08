---
project: ai-training-course
version: 1.0
goal: "Обучение сотрудников 4 направлений работе с on-premise Generative AI"
---

# HARNESS.md — AI Training Course

## Структура проекта

```
ai-training-course/
├── README.md              # Общее описание, архитектура
├── Plan.md                # План фаз, чек-листы
├── HARNESS.md             # Этот файл
│
├── 00-common/             # Модуль 0: Общий вводный
│   ├── README.md          # 3 урока, теория, демо, практика
│   ├── assets/
│   └── templates/
│
├── 01-pr-crisis/          # Модуль 1: PR / Дирекция по СО
│   ├── README.md          # 3 урока (пресс-релизы, тональность, соцсети)
│   ├── assets/
│   └── templates/
│       ├── pr-prompts.md
│       └── pr-checklist.md
│
├── 02-construction/       # Модуль 2: Строители
│   ├── README.md          # 3 урока (сметы, ВОР, планирование)
│   ├── assets/
│   └── templates/
│       ├── construction-prompts.md
│       └── construction-checklists.md
│
├── 03-security/           # Модуль 3: Служба безопасности
│   ├── README.md          # 3 урока (видео, отчеты, аналитика)
│   ├── assets/
│   └── templates/
│       ├── security-templates.md
│       └── incident-classifier.md
│
├── 04-procurement/        # Модуль 4: Закупки и логистика
│   ├── README.md          # 3 урока (цены, логистика, тендеры)
│   ├── assets/
│   └── templates/
│       ├── procurement-templates.md
│       └── procurement-checklists.md
│
└── scripts/               # Скрипты автоматизации
    ├── generate-slides.py
    └── build-course.py
```

## Формат урока (единый шаблон)

Каждый урок = 45-60 минут:
1. **Теория** (15 мин) — презентация 10-15 слайдов
2. **Live Demo** (15 мин) — hands-on в OpenWebUI
3. **Практика** (20 мин) — задание с чек-листом
4. **Проверка** — самопроверка или peer review

## Технический стек on-premise

```
┌──────────────────────────────────────────────┐
│  OpenWebUI (Web Interface)                   │
│  ├── Chat with models                        │
│  ├── RAG (Documents)                         │
│  ├── Custom Models (System Prompts)          │
│  └── Functions/Tools (Agents)              │
├──────────────────────────────────────────────┤
│  Ollama / vLLM (Inference Engine)            │
│  ├── Qwen-VL (Vision + Text)                 │
│  ├── Llama 3 (General Purpose)               │
│  ├── Mistral (Code/Analysis)                 │
│  └── DeepSeek (Reasoning)                    │
├──────────────────────────────────────────────┤
│  AI Agents (OpenClaw / LangChain)            │
│  ├── PR-Agent (мониторинг, генерация)        │
│  ├── Construction-Agent (ВОР, сметы)         │
│  ├── Security-Agent (видео, отчеты)         │
│  └── Procurement-Agent (цены, тендеры)       │
└──────────────────────────────────────────────┘
```

## Skills использованные

| Skill | Назначение | Модуль |
|-------|-----------|--------|
| openclaw-slides | Генерация презентаций | Все |
| process-doc | Документирование процессов | Все |
| content-research-writer | Создание образовательного контента | Все |
| copywriting | Тексты для PR | 01 |
| drawings-to-vor | OCR чертежей, ВОР | 02 |
| smeta | Сметы по ФЕР-2020/БИМ | 02 |
| price-comparison-skill | Сравнение цен, аналоги | 04 |
| context-router | Роутинг контекста | Все |

## Ключевые агенты

### PR-Агент
- Мониторинг СМИ (тональность, аспекты)
- Генерация пресс-релизов, постов
- Анализ кризисных коммуникаций

### Construction-Агент
- OCR чертежей → ВОР (drawings-to-vor)
- Проверка смет (БИМ, ФЕР-2020)
- Планирование графиков (Gantt)

### Security-Агент
- Анализ видео (Qwen-VL)
- Генерация протоколов, рапортов
- Предиктивная аналитика (паттерны, heatmap)

### Procurement-Агент
- Сравнение цен (price-comparison)
- Оптимизация маршрутов
- Тендерная документация

## Статус
- Структура: ✅ Готово
- Контент: 🚧 Ожидает драфт презентации
- Инфраструктура: 🚧 Ожидает уточнение стека
- Пилот: 🚧 Не начат

## Git
Репозиторий: workspace/projects/ai-training-course/
Commit: [в процессе]
