#!/usr/bin/env python3
"""Модуль для автоматизации работы с ДЕЛО ТЕХ.

Примеры использования:
    >>> from delo_tech import DeloTechClient
    >>> client = DeloTechClient()
    >>> client.extract_report_13()  # Извлечь отчёт через CDP
"""
import asyncio
import json
import csv
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class ReportConfig:
    """Конфигурация отчёта."""
    contract_id: str
    start_date: str  # DD.MM.YYYY
    end_date: str    # DD.MM.YYYY
    report_type: str = "13"  # Тип отчёта


class DeloTechClient:
    """Клиент для работы с системой ДЕЛО ТЕХ.
    
    Использует CDP (Chrome DevTools Protocol) для извлечения данных
    из iframe с Vaadin-отчётами.
    
    Attributes:
        cdp_port: Порт для подключения к Chrome DevTools (по умолчанию 18800)
        output_dir: Директория для сохранения файлов
    """
    
    def __init__(self, cdp_port: int = 18800, output_dir: Optional[str] = None):
        self.cdp_port = cdp_port
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).parent
        self._ws_url: Optional[str] = None
    
    async def _find_page(self) -> Optional[str]:
        """Находит WebSocket URL страницы ДЕЛО ТЕХ в CDP.
        
        Returns:
            WebSocket URL или None, если страница не найдена
        """
        import urllib.request
        
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{self.cdp_port}/json") as response:
                pages = json.loads(response.read())
                
                for page in pages:
                    url = page.get("url", "")
                    if "rlisystems.ru" in url and "reports" not in url:
                        self._ws_url = page["webSocketDebuggerUrl"]
                        return self._ws_url
        except Exception as e:
            print(f"❌ Ошибка подключения к CDP: {e}")
            return None
        
        return None
    
    async def _extract_data(self) -> Optional[str]:
        """Извлекает данные отчёта из iframe.
        
        Returns:
            CSV-строка с данными или None
        """
        import websockets
        
        if not self._ws_url:
            await self._find_page()
        
        if not self._ws_url:
            return None
        
        async with websockets.connect(self._ws_url) as ws:
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
            
            return None
    
    def extract_report_13(self) -> dict:
        """Извлекает отчёт 13 (Движение по импорту).
        
        Returns:
            Словарь с путями к файлам:
                - csv: путь к CSV
                - xlsx: путь к Excel
        """
        # Запускаем асинхронную часть
        data = asyncio.run(self._extract_data())
        
        if not data or data.startswith('error:'):
            raise RuntimeError(f"Ошибка извлечения: {data}")
        
        # Сохраняем CSV
        csv_path = self.output_dir / 'report_13_import.csv'
        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write(data)
        
        # Конвертируем в Excel
        xlsx_path = self.output_dir / 'report_13_import.xlsx'
        self._csv_to_excel(csv_path, xlsx_path)
        
        return {
            'csv': str(csv_path),
            'xlsx': str(xlsx_path),
            'rows': len(data.strip().split('\n'))
        }
    
    def _csv_to_excel(self, csv_path: Path, xlsx_path: Path):
        """Конвертирует CSV в Excel."""
        from openpyxl import Workbook
        
        wb = Workbook()
        ws = wb.active
        ws.title = 'Импорт'
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                ws.append(row)
        
        wb.save(xlsx_path)


# CLI-интерфейс
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='ДЕЛО ТЕХ — автоматизация')
    parser.add_argument('--action', choices=['report13'], required=True,
                       help='Действие: report13 — извлечь отчёт 13')
    parser.add_argument('--output', '-o', default='.',
                       help='Директория для сохранения')
    
    args = parser.parse_args()
    
    if args.action == 'report13':
        client = DeloTechClient(output_dir=args.output)
        result = client.extract_report_13()
        print(f"✅ Извлечено {result['rows']} строк")
        print(f"   CSV:  {result['csv']}")
        print(f"   Excel: {result['xlsx']}")
