#!/usr/bin/env python3
"""Полный pipeline: извлечение отчёта из ДЕЛО ТЕХ через CDP → CSV → Excel."""
import asyncio
import websockets
import json
import sys
import csv
from pathlib import Path
from openpyxl import Workbook


# Конфигурация
CDP_PORT = 18800
DEFAULT_OUTPUT_DIR = Path(__file__).parent


async def find_page_ws_url() -> str:
    """Находит WebSocket URL страницы с rlisystems.ru."""
    import urllib.request
    
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json") as response:
            pages = json.loads(response.read())
            
            for page in pages:
                if "rlisystems.ru" in page.get("url", "") and "reports" not in page.get("url", ""):
                    return page["webSocketDebuggerUrl"]
            
            # Если не нашли, берём первую подходящую
            for page in pages:
                if page.get("type") == "page" and "rlisystems.ru" in page.get("url", ""):
                    return page["webSocketDebuggerUrl"]
    except Exception as e:
        print(f"❌ Ошибка подключения к CDP: {e}")
        print(f"Убедитесь, что Chrome запущен с флагом --remote-debugging-port={CDP_PORT}")
        sys.exit(1)
    
    return None


async def extract_report_data(ws_url: str) -> str:
    """Извлекает данные отчёта из iframe через CDP."""
    
    async with websockets.connect(ws_url) as ws:
        # Включаем Runtime
        await ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
        
        # Ждём ответ
        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            if data.get("id") == 1:
                break
        
        # JavaScript для извлечения данных из iframe
        script = """
        (function() {
            const frame = document.querySelectorAll('iframe')[1];
            try {
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
                                let text = c.textContent.trim().replace(/\\s+/g, ' ');
                                row.push(text);
                            }
                            csv += row.join(';') + '\\n';
                        }
                    }
                }
                return csv;
            } catch(e) {
                return 'error: ' + e.message;
            }
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
        
        # Ждём ответ
        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            if data.get("id") == 2:
                break
        
        if "result" in data and "result" in data["result"]:
            return data["result"]["result"]["value"]
        else:
            print(f"❌ Ошибка: {data}")
            return None


def save_csv(data: str, output_path: Path) -> Path:
    """Сохраняет данные в CSV."""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(data)
    
    rows = data.strip().split('\n')
    print(f"✅ CSV сохранён: {output_path} ({len(rows)} строк)")
    return output_path


def convert_to_excel(csv_path: Path, xlsx_path: Path) -> Path:
    """Конвертирует CSV в Excel."""
    wb = Workbook()
    ws = wb.active
    ws.title = 'Импорт'
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            ws.append(row)
    
    wb.save(xlsx_path)
    print(f"✅ Excel сохранён: {xlsx_path}")
    return xlsx_path


async def main():
    """Основной pipeline."""
    print("=" * 60)
    print("🚀 ДЕЛО ТЕХ: Извлечение отчёта 13 (Движение по импорту)")
    print("=" * 60)
    
    # 1. Находим страницу
    print("\n1️⃣ Поиск страницы в CDP...")
    ws_url = await find_page_ws_url()
    
    if not ws_url:
        print("❌ Страница ДЕЛО ТЕХ не найдена в CDP")
        print("Убедитесь, что:")
        print("  - Chrome запущен с --remote-debugging-port=18800")
        print("  - Вы вошли в систему ДЕЛО ТЕХ")
        print("  - Открыт раздел с отчётами")
        sys.exit(1)
    
    print(f"✅ Найдена страница: {ws_url[:60]}...")
    
    # 2. Извлекаем данные
    print("\n2️⃣ Извлечение данных из iframe...")
    data = await extract_report_data(ws_url)
    
    if not data or data.startswith('error:'):
        print(f"❌ Ошибка извлечения: {data}")
        sys.exit(1)
    
    # 3. Сохраняем CSV
    print("\n3️⃣ Сохранение в CSV...")
    csv_path = DEFAULT_OUTPUT_DIR / 'report_13_import.csv'
    save_csv(data, csv_path)
    
    # 4. Конвертируем в Excel
    print("\n4️⃣ Конвертация в Excel...")
    xlsx_path = DEFAULT_OUTPUT_DIR / 'report_13_import.xlsx'
    convert_to_excel(csv_path, xlsx_path)
    
    print("\n" + "=" * 60)
    print("✅ Готово! Файлы сохранены:")
    print(f"   CSV:  {csv_path}")
    print(f"   Excel: {xlsx_path}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
