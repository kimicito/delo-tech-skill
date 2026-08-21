# delo-tech

**Skill для автоматизации работы с личным кабинетом ДЕЛО ТЕХ (rlisystems.ru/conterra/)**

## Описание

Автоматизирует вход, навигацию и извлечение отчётов из системы «ДЕЛО ТЕХ» (RLISystems / Контейнерный терминал). Используется для логистики и таможенного документооборота.

## Триггеры

- Пользователь упоминает: "delo tech", "дело тех", "rlisystems", "conterra", "контейнерный терминал"
- Запрос на проверку статуса контейнера, релиз-ордеров, баланса
- Запрос на выгрузку отчёта (особенно отчёт 13 — «Движение по импорту»)

---

## Общая последовательность разработки агента (Универсальный шаблон)

Этот skill демонстрирует **полный цикл разработки агента** для сложных enterprise-систем. Используйте как шаблон для подобных задач.

### Этап 1: Разведка и диагностика

**Цель:** Понять архитектуру целевой системы.

```bash
# 1.1. Анализ структуры страницы
- Открыть сайт в браузере
- Определить: SPA или классический сайт
- Проверить наличие iframe
- Проверить систему аутентификации (SSO, форма, токены)

# 1.2. Проверка простых методов
curl -I https://target-site.com/api/endpoint  # Проверка API
# Если 403/5xx — переходим к browser automation

# 1.3. Анализ защиты
- Cloudflare? → Использовать browser tool
- Geo-block? → Проверить из нужной локации
- CORS? → Проксирование через iframe/CDP
```

### Этап 2: Выбор стратегии доступа

| Сценарий | Инструмент | Пример |
|----------|-----------|--------|
| Простой REST API | `curl` / `requests` | 90% сайтов |
| Форма + cookies | `curl -c -b` | Legacy системы |
| SPA (React/Vue) | Playwright/CDP | Modern dashboards |
| Vaadin/GWT iframe | **CDP + iframe** | ДЕЛО ТЕХ |
| SSO (Keycloak/AD) | Browser automation | Enterprise |

**Для ДЕЛО ТЕХ:**
- Основная страница: `iframe` с Vaadin-приложением
- SSO: `https://rlisystems.ru/webiom/sso/`
- Отчёты: загружаются в отдельный `iframe`
- **Решение:** CDP (Chrome DevTools Protocol) для доступа к iframe

### Этап 3: Реализация доступа

#### 3.1. Playwright (headless) — Пробуем первым

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://rlisystems.ru/conterra/")
    
    # Проверяем, видим ли элементы
    if page.locator("text='Войти'").count() == 0:
        print("iframe или SSO — нужен CDP")
```

**Результат для ДЕЛО ТЕХ:** ❌ Не работает (iframe + SSO)

#### 3.2. CDP (Chrome DevTools Protocol) — Основное решение

```python
import asyncio
import websockets
import json

async def extract_via_cdp():
    # Подключаемся к запущенному Chrome
    ws_url = "ws://127.0.0.1:18800/devtools/page/<PAGE_ID>"
    
    async with websockets.connect(ws_url) as ws:
        # Включаем Runtime
        await ws.send(json.dumps({
            "id": 1, "method": "Runtime.enable"
        }))
        
        # Выполняем скрипт в контексте страницы
        script = """
        (function() {
            const frame = document.querySelectorAll('iframe')[1];
            const doc = frame.contentDocument || frame.contentWindow.document;
            // Извлекаем данные...
            return extractedData;
        })()
        """
        
        await ws.send(json.dumps({
            "id": 2,
            "method": "Runtime.evaluate",
            "params": {
                "expression": script,
                "returnByValue": True
            }
        }))
        
        response = await ws.recv()
        data = json.loads(response)
```

**Результат для ДЕЛО ТЕХ:** ✅ Работает!

### Этап 4: Извлечение данных из iframe

**Проблема:** iframe изолирован от основной страницы (same-origin policy).

**Решение:**
1. Получаем доступ к iframe через `contentDocument`
2. Ищем таблицы (`table` → `tr` → `td/th`)
3. Конвертируем в CSV

```javascript
// Выполняем в CDP
const frame = document.querySelectorAll('iframe')[1];
const doc = frame.contentDocument || frame.contentWindow.document;

let csv = '';
const tables = doc.querySelectorAll('table');
for (let t of tables) {
    const rows = t.querySelectorAll('tr');
    for (let r of rows) {
        const cells = r.querySelectorAll('td, th');
        if (cells.length > 3) {
            let row = [];
            for (let c of cells) {
                row.push(c.textContent.trim().replace(/\s+/g, ' '));
            }
            csv += row.join(';') + '\n';
        }
    }
}
```

### Этап 5: Обработка и сохранение

```python
# CSV → Excel
from openpyxl import Workbook
import csv

def csv_to_excel(csv_path, xlsx_path):
    wb = Workbook()
    ws = wb.active
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            ws.append(row)
    
    wb.save(xlsx_path)
    return xlsx_path
```

### Этап 6: Проверка и доставка

```bash
# Проверка количества строк
wc -l report.csv

# Проверка структуры
head -5 report.csv

# Отправка пользователю (Telegram)
# Использовать message tool с filePath
```

---

## Архитектура ДЕЛО ТЕХ

### Компоненты системы

| Компонент | URL | Назначение |
|-----------|-----|------------|
| Основной сайт | `https://rlisystems.ru/conterra/` | iframe-контейнер |
| SSO | `https://rlisystems.ru/webiom/sso/` | Аутентификация |
| Отчёты | `https://rlisystems.ru/conterra/reports/~<ID>.html` | Vaadin-отчёты |
| Чат | `https://web.redhelper.ru/chat/` | Виджет поддержки |

### Структура iframe

```
rlisystems.ru/conterra/
├── iframe[0]: web.redhelper.ru/chat/ (виджет чата)
├── iframe[1]: conterra/reports/~<ID>.html (Vaadin-отчёт) ← ДАННЫЕ
└── iframe[2]: javascript:"" (пустой)
```

### Типы отчётов

| № | Название | Описание |
|---|----------|----------|
| 13 | Движение по импорту | Контейнеры, импорт |
| ... | ... | ... |

---

## Файлы

| Файл | Назначение |
|------|------------|
| `SKILL.md` | Эта документация |
| `delo_tech.py` | Модуль Python для автоматизации |
| `extract_report.py` | Извлечение отчёта через CDP |
| `extract_ws.py` | Подключение к CDP WebSocket |
| `csv_to_excel.py` | Конвертация CSV → Excel |
| `download_report.py` | Полный pipeline: извлечение + конвертация |
| `.env.example` | Шаблон переменных окружения |
| `requirements.txt` | Зависимости Python |

---

## Установка

```bash
# 1. Копируем env
cp .env.example .env

# 2. Устанавливаем зависимости
pip install -r requirements.txt

# 3. Для Playwright (опционально)
playwright install chromium
```

---

## Использование

### Полный pipeline (рекомендуется)

```bash
python download_report.py --contract <ID> --start-date DD.MM.YYYY --end-date DD.MM.YYYY
```

Результат: `report_13_import.xlsx` с полными данными.

### Пошагово

```bash
# 1. Извлечь через CDP
python extract_ws.py
# → report_13_import_full.csv

# 2. Конвертировать в Excel
python csv_to_excel.py report_13_import_full.csv
# → report_13_import_full.xlsx
```

### Из Python

```python
from delo_tech import DeloTechClient

client = DeloTechClient()
client.login()  # SSO-аутентификация

# Извлечь отчёт 13
report = client.get_report_13(
    contract_id="...",
    start_date="01.08.2026",
    end_date="21.08.2026"
)

# Сохранить
report.to_excel("report.xlsx")
```

---

## Примеры CDP-скриптов

### Проверка iframe

```javascript
// В CDP: какие iframe есть на странице?
const iframes = document.querySelectorAll('iframe');
let result = '';
for (let i=0; i<iframes.length; i++) {
    result += `iframe${i}: ${iframes[i].src}\n`;
}
return result;
```

### Клик по кнопке в iframe

```javascript
// В CDP: нажать кнопку выгрузки
const frame = document.querySelectorAll('iframe')[1];
const doc = frame.contentDocument || frame.contentWindow.document;
const buttons = doc.querySelectorAll('button');
for (let btn of buttons) {
    if (btn.textContent.includes('💾') || btn.title.includes('Выгрузить')) {
        btn.click();
        return 'clicked';
    }
}
```

### Извлечение таблицы

```javascript
// В CDP: извлечь все данные таблицы
const frame = document.querySelectorAll('iframe')[1];
const doc = frame.contentDocument || frame.contentWindow.document;
let csv = '';
const tables = doc.querySelectorAll('table');
for (let t of tables) {
    const rows = t.querySelectorAll('tr');
    for (let r of rows) {
        const cells = r.querySelectorAll('td, th');
        if (cells.length > 3) {
            let row = [];
            for (let c of cells) {
                row.push(c.textContent.trim().replace(/\s+/g, ' '));
            }
            csv += row.join(';') + '\n';
        }
    }
}
return csv;
```

---

## Безопасность

- Учётные данные хранятся в `.env` (gitignored)
- Все операции через HTTPS
- Сессионные cookies в памяти (не сохраняются)
- CDP-доступ только локальный (`127.0.0.1`)

---

## Расширение

### Планируемые функции

- [x] Извлечение отчёта 13 (Движение по импорту)
- [ ] Парсинг релиз-ордеров
- [ ] Проверка статуса контейнера по номеру
- [ ] Скачивание таможенных документов
- [ ] Отслеживание баланса и алерты
- [ ] Интеграция с Telegram-уведомлениями

---

## Уроки и паттерны

### Универсальные паттерны (применимо к любым enterprise-системам)

1. **iframe-изоляция:** Если данные в iframe — используйте CDP, а не простой Playwright
2. **SSO-аутентификация:** Входите через основной сайт, а не напрямую в iframe
3. **Проверка количества строк:** Всегда проверяйте `wc -l` после извлечения
4. **Конвертация форматов:** Сохраняйте и CSV (для отладки), и Excel (для пользователя)
5. **Error handling:** iframe может быть недоступен — проверяйте `contentDocument`

### Антипаттерны

❌ Пытаться кликнуть через Playwright на элемент внутри iframe  
❌ Использовать `page.frame()` — работает только с same-origin  
❌ Пытаться скачать файл через кнопку (не работает в headless)  
✅ Использовать CDP + JavaScript для извлечения DOM-данных

---

## Автор

Создано для Artur A.  
2026-08-22 — Полная переработка с добавлением универсального шаблона разработки агентов
