#!/usr/bin/env python3
"""
wb_tax_calculator.py — расчёт налога РВБ (Wildberries) на АУСН.

Поддерживает:
- Реестр еженедельных операций (Excel/CSV)
- Детализации отчётов (Excel/CSV)
- Уведомления о выкупе (вручную или CSV)

Usage:
    python wb_tax_calculator.py --registry реестр.xlsx --details детализация.xlsx --purchases уведомления.xlsx

Output:
    Расчёт комиссий, возвратов, итоговая сумма для внесения в ЛКН АУСН.
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


def calculate_main_commission(df: pd.DataFrame) -> float:
    """Calculate commission for 'Основной' report type."""
    # Filter by report type
    main_df = df[df['Тип отчета'] == 'Основной']
    if main_df.empty:
        return 0.0
    
    total_sales = main_df['Продажа'].sum()
    total_payout = main_df['Итого к оплате'].sum()
    commission = total_sales - total_payout
    
    return round(commission, 2)


def calculate_purchase_commission(df: pd.DataFrame, purchases_df: pd.DataFrame = None) -> float:
    """Calculate commission for 'По выкупам' report type.
    
    If purchases_df is provided, compare amounts automatically.
    Otherwise return 0 (manual input needed).
    """
    purchase_df = df[df['Тип отчета'] == 'По выкупам']
    if purchase_df.empty:
        return 0.0
    
    if purchases_df is not None and not purchases_df.empty:
        # Auto-calculate: sum of notifications - sum of registry payouts
        total_registry = purchase_df['Итого к оплате'].sum()
        total_notifications = purchases_df['Сумма'].sum() if 'Сумма' in purchases_df.columns else 0
        commission = total_notifications - total_registry
        return round(commission, 2) if commission > 0 else 0.0
    
    return 0.0  # Manual calculation needed


def calculate_returns(df: pd.DataFrame) -> float:
    """Calculate total returns from details."""
    # Filter by document type = return
    returns_df = df[df['Тип документа'].str.contains('возврат', case=False, na=False)]
    if returns_df.empty:
        return 0.0
    
    column = 'Вайлдберриз реализовал Товар (Пр)'
    if column not in returns_df.columns:
        # Try alternative names
        alt_cols = [c for c in returns_df.columns if 'реализовал' in c.lower()]
        if alt_cols:
            column = alt_cols[0]
        else:
            return 0.0
    
    total_returns = returns_df[column].sum()
    return round(total_returns, 2)


def main():
    parser = argparse.ArgumentParser(description='WB Tax Calculator')
    parser.add_argument('--registry', required=True, help='Реестр еженедельных операций (Excel/CSV)')
    parser.add_argument('--details', required=True, help='Детализация отчётов (Excel/CSV)')
    parser.add_argument('--purchases', help='Уведомления о выкупе (Excel/CSV, optional)')
    parser.add_argument('--losses', type=float, default=0, help='Доп. расходы: потери/подмены/дефекты')
    
    args = parser.parse_args()
    
    # Read files
    registry = read_file(Path(args.registry))
    details = read_file(Path(args.details))
    purchases = read_file(Path(args.purchases)) if args.purchases else None
    
    # Calculate
    main_commission = calculate_main_commission(registry)
    purchase_commission = calculate_purchase_commission(registry, purchases)
    total_commission = main_commission + purchase_commission + args.losses
    total_returns = calculate_returns(details)
    
    # Output
    print("=" * 60)
    print("РАСЧЁТ НАЛОГА РВБ (Wildberries) на АУСН")
    print("=" * 60)
    print(f"Комиссия (Основной):       {main_commission:>15,.2f} руб.")
    print(f"Комиссия (Выкупы):        {purchase_commission:>15,.2f} руб.")
    print(f"Доп. расходы (потери):     {args.losses:>15,.2f} руб.")
    print("-" * 60)
    print(f"ИТОГО КОМИССИЯ:            {total_commission:>15,.2f} руб.")
    print(f"ВОЗВРАТЫ:                 {total_returns:>15,.2f} руб.")
    print("=" * 60)
    print("\nРекомендация по ЛКН АУСН:")
    print(f"  • Внести взаимозачет на сумму: {total_commission:,.2f} руб.")
    if total_returns > 0:
        print(f"  • Возвраты: {total_returns:,.2f} руб. (несколько операций)")
    print("=" * 60)


if __name__ == '__main__':
    main()
