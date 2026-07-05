#!/usr/bin/env python3
"""
ozon_tax_calculator.py — расчёт налога Ozon на АУСН.

Поддерживает:
- Отчёт о реализации (Excel/CSV)
- Отчёт о взаиморасчётах (Excel/CSV)

Usage:
    python ozon_tax_calculator.py --realization отчет_реализации.xlsx --mutual отчет_взаиморасчетов.xlsx

Output:
    Расчёт возвратов, услуг, итоговые суммы для внесения в ЛКН АУСН.
"""

import argparse
import pandas as pd
import sys
from pathlib import Path


def read_file(path: Path) -> pd.DataFrame:
    """Read Excel or CSV file."""
    if path.suffix.lower() in ('.xlsx', '.xls'):
        return pd.read_excel(path)
    elif path.suffix.lower() == '.csv':
        return pd.read_csv(path, sep=';')
    else:
        raise ValueError(f"Unsupported format: {path.suffix}")


def calculate_returns(df: pd.DataFrame) -> float:
    """Calculate total returns from realization report."""
    col_return = 'Возвращено на сумму, руб.'
    col_loyalty = 'Выплаты по механикам лояльности партнёров, руб.'
    
    total_return = df[col_return].sum() if col_return in df.columns else 0.0
    total_loyalty = df[col_loyalty].sum() if col_loyalty in df.columns else 0.0
    
    return round(total_return + total_loyalty, 2)


def calculate_services(df: pd.DataFrame) -> float:
    """Calculate total services from mutual settlements report."""
    col_amount = 'Суммы дебиторской задолженности'
    
    if col_amount not in df.columns:
        raise ValueError(f"Column not found: {col_amount}")
    
    # Filter rows by service type
    service_types = [
        'Отчет о реализации',
        'Акт выполненных работ',
        'Отчет о перевыставлении услуг',
        'Акт об оказанных услугах'
    ]
    
    total = 0.0
    for service_type in service_types:
        rows = df[df.apply(lambda row: row.astype(str).str.contains(service_type, case=False, na=False).any(), axis=1)]
        if not rows.empty:
            total += rows[col_amount].sum()
    
    return round(total, 2)


def main():
    parser = argparse.ArgumentParser(description='Ozon Tax Calculator')
    parser.add_argument('--realization', required=True, help='Отчёт о реализации (Excel/CSV)')
    parser.add_argument('--mutual', required=True, help='Отчёт о взаиморасчётах (Excel/CSV)')
    
    args = parser.parse_args()
    
    # Read files
    realization = read_file(Path(args.realization))
    mutual = read_file(Path(args.mutual))
    
    # Calculate
    total_returns = calculate_returns(realization)
    total_services = calculate_services(mutual)
    
    total_income = total_returns + total_services
    
    # Output
    print("=" * 60)
    print("РАСЧЁТ НАЛОГА OZON на АУСН")
    print("=" * 60)
    print(f"Возвраты:                  {total_returns:>15,.2f} руб.")
    print(f"Услуги (комиссия):         {total_services:>15,.2f} руб.")
    print("-" * 60)
    print(f"ИТОГО (Приход в ЛКН):      {total_income:>15,.2f} руб.")
    print("=" * 60)
    print("\nРекомендация по ЛКН АУСН (операция 'Взаимозачёт'):")
    print(f"  • Приход:            {total_income:>15,.2f} руб.")
    print(f"  • Возврат прихода:   {total_returns:>15,.2f} руб.")
    print(f"  • Расход:            {total_services:>15,.2f} руб.")
    if total_returns == 0:
        print("  • Возвратов нет — можно внести одной суммой")
    print("=" * 60)


if __name__ == '__main__':
    main()
