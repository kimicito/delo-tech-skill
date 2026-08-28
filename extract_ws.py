#!/usr/bin/env python3
"""Подключение к CDP WebSocket и извлечение данных из iframe."""
import asyncio
import websockets
import json

async def extract_via_cdp():
    ws_url = "ws://127.0.0.1:18800/devtools/page/F6C79098678A3960FBC9A173C3AE4D1F"
    
    async with websockets.connect(ws_url) as ws:
        # Включаем Runtime
        await ws.send(json.dumps({
            "id": 1,
            "method": "Runtime.enable"
        }))
        
        # Ждём ответ на Runtime.enable
        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            if data.get("id") == 1:
                break
        
        # Выполняем скрипт для извлечения данных из iframe
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
                                row.push(c.textContent.trim().replace(/\\s+/g, ' '));
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
        
        # Ждём ответ на evaluate
        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            if data.get("id") == 2:
                break
        
        if "result" in data and "result" in data["result"]:
            csv_data = data["result"]["result"]["value"]
            
            if csv_data.startswith('error:'):
                print(csv_data)
                return
            
            # Сохраняем в файл
            csv_path = '/root/.openclaw/workspace/skills/delo-tech/report_13_import_full.csv'
            with open(csv_path, 'w', encoding='utf-8') as f:
                f.write(csv_data)
            
            rows = csv_data.strip().split('\n')
            print(f"Saved {len(rows)} rows to {csv_path}")
            
            # Конвертируем в Excel
            from openpyxl import Workbook
            import csv
            
            wb = Workbook()
            ws = wb.active
            ws.title = 'Импорт'
            
            reader = csv.reader(rows, delimiter=';')
            for row in reader:
                ws.append(row)
            
            xlsx_path = '/root/.openclaw/workspace/skills/delo-tech/report_13_import_full.xlsx'
            wb.save(xlsx_path)
            print(f"Saved Excel to {xlsx_path}")
        else:
            print("Error:", data)

if __name__ == "__main__":
    asyncio.run(extract_via_cdp())
