#!/usr/bin/env python3
"""Основной скрипт для извлечения отчёта из ДЕЛО ТЕХ.

Использует CDP (Chrome DevTools Protocol) для доступа к iframe с отчётом.
"""
import asyncio
import json
import websockets
import argparse
from pathlib import Path


async def find_rlisystems_page(cdp_port: int = 18800) -> str:
    """Находит WebSocket URL страницы ДЕЛО ТЕХ."""
    import urllib.request
    
    with urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json") as response:
        pages = json.loads(response.read())
        
        for page in pages:
            url = page.get("url", "")
            if "rlisystems.ru" in url and "reports" not in url:
                return page["webSocketDebuggerUrl"]
    
    raise RuntimeError("Страница ДЕЛО ТЕХ не найдена в CDP")


async def extract_report(ws_url: str) -> str:
    """Извлекает данные отчёта из iframe."""
    
    async with websockets.connect(ws_url) as ws:
        # Включаем Runtime
        await ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
        
        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            if data.get("id") == 1:
                break
        
        # Скрипт для извлечения данных
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
        
        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            if data.get("id") == 2:
                break
        
        if "result" in data and "result" in data["result"]:
            return data["result"]["result"]["value"]
        
        raise RuntimeError(f"Ошибка извлечения: {data}")


async def main():
    parser = argparse.ArgumentParser(description='Извлечение отчёта из ДЕЛО ТЕХ')
    parser.add_argument('--cdp-port', type=int, default=18800,
                       help='Порт Chrome DevTools (по умолчанию 18800)')
    parser.add_argument('--output', '-o', default='report_13_import.csv',
                       help='Имя выходного CSV-файла')
    
    args = parser.parse_args()
    
    print("🔍 Поиск страницы ДЕЛО ТЕХ...")
    ws_url = await find_rlisystems_page(args.cdp_port)
    
    print(f"✅ Найдена страница: {ws_url[:50]}...")
    print("📊 Извлечение данных...")
    
    data = await extract_report(ws_url)
    
    if data.startswith('error:'):
        print(f"❌ Ошибка: {data}")
        return
    
    # Сохраняем
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(data)
    
    rows = data.strip().split('\n')
    print(f"✅ Сохранено {len(rows)} строк в {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
