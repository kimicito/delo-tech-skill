#!/usr/bin/env python3
"""Извлечение полного отчёта из iframe через CDP (порт 18800)."""
import asyncio
from playwright.async_api import async_playwright

async def extract_full_report():
    async with async_playwright() as p:
        # Подключаемся к открытому Chrome через CDP (порт 18800)
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:18800")
        context = browser.contexts[0]
        
        # Находим страницу с rlisystems.ru
        page = None
        for pg in context.pages:
            if "rlisystems.ru" in pg.url and "reports" not in pg.url:
                page = pg
                break
        
        if not page:
            print("Page not found!")
            print("Available pages:")
            for pg in context.pages:
                print(f"  - {pg.url}")
            return
        
        print(f"Found page: {page.url}")
        
        # Получаем все данные из iframe
        data = await page.evaluate("""() => {
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
        }""")
        
        if data.startswith('error:'):
            print(data)
            return
        
        # Сохраняем в CSV
        csv_path = '/root/.openclaw/workspace/skills/delo-tech/report_13_import_full.csv'
        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write(data)
        
        rows = data.strip().split('\n')
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
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(extract_full_report())
