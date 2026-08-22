# ДЕЛО ТЕХ — Архитектура Skill'а

## 🎯 Структура (рекомендуемая)

```
delo-tech/
│
├── 📄 SKILL.md                          # Документация (триггеры, примеры)
│
├── 🧠 delo_tech.py                      # ЯДРО (единая точка входа)
│   ├── CDPClient                        # Подключение к Chrome
│   ├── SessionManager                   # Проверка авторизации
│   ├── ReportManager                    # Работа с отчётами
│   └── DeloTechCore                     # Главный класс-роутер
│
├── 📊 reports/                           # Модули отчётов
│   ├── report_13_import.py              # Отчёт 13 — Движение по импорту
│   ├── report_7_export.py               # Отчёт 7 — Движение по экспорту
│   └── report_custom.py                 # Пользовательские отчёты
│
├── ⚙️ operations/                        # Операции
│   ├── container_status.py              # Статус контейнера
│   ├── release_orders.py                # Релиз-ордера
│   ├── customs_docs.py                  # Таможенные документы
│   └── balance.py                       # Баланс
│
├── 🛠 utils/                             # Утилиты
│   ├── cdp_client.py                    # CDP-клиент
│   ├── csv_excel.py                     # Конвертация
│   └── session.py                       # Управление сессией
│
├── 📥 report_13_import.xlsx             # Последний отчёт (Excel)
├── 📄 report_13_import.csv              # Последний отчёт (CSV)
│
├── 📦 requirements.txt                  # Зависимости
└── ⚙️ .env.example                      # Шаблон настроек
```

---

## 🔄 Как добавить новую операцию

### Шаг 1: Создать модуль

```python
# operations/container_status.py
from ..delo_tech import CDPClient

async def get_status(cdp: CDPClient, container_number: str) -> dict:
    """Получает статус контейнера."""
    script = f"""
        // Ищем контейнер в таблице
        const frame = document.querySelectorAll('iframe')[1];
        const doc = frame.contentDocument || frame.contentWindow.document;
        
        // Логика поиска...
        return JSON.stringify({{container: '{container_number}', status: 'found'}});
    """
    
    result = await cdp.execute(script)
    return json.loads(result)
```

### Шаг 2: Добавить в ядро

```python
# delo_tech.py → class DeloTechCore

def get_container_status(self, container_number: str) -> dict:
    """Получает статус контейнера."""
    from .operations.container_status import get_status
    return asyncio.run(get_status(self.cdp, container_number))
```

### Шаг 3: Обновить SKILL.md

```markdown
## Операции

| Операция | Метод | Статус |
|----------|-------|--------|
| Отчёт 13 | `run_report("13", ...)` | ✅ Готово |
| Статус контейнера | `get_container_status("TKRU...")` | ✅ Готово |
```

---

## 🎭 Сценарии использования

### Сценарий 1: Ежедневный отчёт

```python
from skills.delo-tech.delo_tech import DeloTechCore

core = DeloTechCore()

# Каждый день — отчёт за вчера
from datetime import datetime, timedelta

yesterday = (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y")
result = core.run_report("13", yesterday, yesterday)

if result.success:
    send_email(result.files['xlsx'])  # Отправить бухгалтеру
```

### Сценарий 2: Проверка контейнера

```python
core = DeloTechCore()
status = core.get_container_status("TKRU3055043")

if status['location'] == 'Терминал':
    print("Контейнер на терминале, можно забирать")
```

### Сценарий 3: Мониторинг релиз-ордеров

```python
core = DeloTechCore()
orders = core.get_release_orders()

for order in orders:
    if order['status'] == 'новый':
        send_telegram(f"🆕 Новый релиз-ордер: {order['number']}")
```

---

## ❓ Когда использовать оркестратор?

### Сейчас: Один skill (до 10 операций)

```
✅ Просто
✅ Общая сессия
✅ Не нужен оркестратор
```

### Будущее: Оркестратор (если > 15 операций)

```
delo-tech-orchestrator/     # Роутинг
├── Определяет тип задачи
└── Вызывает нужный skill

delo-tech-auth/            # Авторизация (разделяемая)
delo-tech-reports/         # Все отчёты
delo-tech-monitoring/      # Мониторинг контейнеров
delo-tech-docs/            # Документы
```

**Но:** Сессия (cookies, iframe) — проблема. Каждый skill будет логиниться заново.

**Решение:** Общий `delo-tech-session` skill, который хранит сессию и передаёт другим.

---

## 📋 Правила разработки

1. **Всегда через ядро** — не вызывать CDP напрямую, использовать `DeloTechCore`
2. **Проверка авторизации** — каждая операция начинается с `session.ensure_auth()`
3. **Единый формат результата** — использовать `OperationResult`
4. **Сохранение файлов** — CSV + Excel, имена с timestamp
5. **Документация** — обновлять SKILL.md при добавлении операции

---

## 🚀 Быстрый старт для нового разработчика

```bash
# 1. Установка
pip install -r requirements.txt

# 2. Проверка подключения
python -c "from delo_tech import DeloTechCore; c = DeloTechCore(); print('OK')"

# 3. Первый отчёт
python delo_tech.py --action report --report-type 13 \
    --start-date 01.08.2026 --end-date 21.08.2026
```
