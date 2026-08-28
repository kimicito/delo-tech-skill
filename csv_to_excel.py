#!/usr/bin/env python3
"""Конвертация CSV → Excel."""
import sys
import csv
from pathlib import Path
from openpyxl import Workbook


def csv_to_excel(csv_path: str, xlsx_path: str = None) -> str:
    """Конвертирует CSV-файл в Excel.
    
    Args:
        csv_path: Путь к CSV-файлу
        xlsx_path: Путь для сохранения Excel (опционально)
    
    Returns:
        Путь к созданному Excel-файлу
    """
    csv_file = Path(csv_path)
    if not csv_file.exists():
        raise FileNotFoundError(f"CSV-файл не найден: {csv_path}")
    
    if xlsx_path is None:
        xlsx_path = str(csv_file.with_suffix('.xlsx'))
    
    wb = Workbook()
    ws = wb.active
    ws.title = 'Импорт'
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        # Определяем разделитель
        sample = f.read(4096)
        f.seek(0)
        
        delimiter = ';' if sample.count(';') > sample.count(',') else ','
        
        reader = csv.reader(f, delimiter=delimiter)
        for row in reader:
            ws.append(row)
    
    wb.save(xlsx_path)
    print(f"✅ Сохранено: {xlsx_path}")
    return xlsx_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python csv_to_excel.py <input.csv> [output.xlsx]")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    xlsx_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    csv_to_excel(csv_path, xlsx_path)
