#!/usr/bin/env python3
"""Corporate Reports Analyzer — Quarterly & Annual

Анализирует P&L, Balance Sheet, Cash Flow из Excel/CSV.
"""

import pandas as pd
import pdfplumber
import argparse
import sys
from pathlib import Path
from datetime import datetime


def extract_tables_from_pdf(path):
    """Извлекает таблицы из PDF, возвращает DataFrame с первой найденной таблицей."""
    print(f"Extracting tables from PDF: {path}")
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for j, table in enumerate(tables):
                if len(table) > 2 and len(table[0]) > 2:
                    # Первая строка = заголовки, первая колонка = индекс
                    df = pd.DataFrame(table[1:], columns=table[0])
                    df = df.set_index(df.columns[0])
                    # Преобразуем числа
                    for col in df.columns:
                        df[col] = pd.to_numeric(df[col].astype(str).str.replace(' ', '').str.replace(',', '.'), errors='coerce')
                    print(f"  Found table on page {i+1}, table {j+1}: {len(df)} rows × {len(df.columns)} cols")
                    return df
    raise ValueError("No valid tables found in PDF")


def load_report(path):
    """Загружает отчёт: Excel, CSV или PDF."""
    ext = Path(path).suffix.lower()
    if ext in ('.xlsx', '.xls'):
        return pd.read_excel(path, index_col=0)
    elif ext == '.csv':
        return pd.read_csv(path, index_col=0)
    elif ext == '.pdf':
        return extract_tables_from_pdf(path)
    else:
        raise ValueError(f"Unsupported format: {ext}. Use .xlsx, .xls, .csv, .pdf")


def calculate_margins(df):
    """Считает маржинальность из P&L."""
    results = {}
    
    # Ищем ключевые строки (гибкая логика)
    revenue = find_row(df, ['выручка', 'revenue', 'доход', 'sales'])
    cogs = find_row(df, ['себестоимость', 'cogs', 'cost of goods', 'cost'])
    opex = find_row(df, ['операционные расходы', 'opex', 'operating expenses', 'расходы'])
    net_income = find_row(df, ['чистая прибыль', 'net income', 'прибыль', 'profit'])
    
    if revenue is not None:
        results['revenue'] = revenue
        if cogs is not None:
            gross_profit = revenue - cogs
            results['gross_margin'] = (gross_profit / revenue * 100).round(2)
        if opex is not None and cogs is not None:
            operating_profit = revenue - cogs - opex
            results['operating_margin'] = (operating_profit / revenue * 100).round(2)
        if net_income is not None:
            results['net_margin'] = (net_income / revenue * 100).round(2)
    
    return results


def find_row(df, keywords):
    """Ищет строку по ключевым словам (case-insensitive)."""
    for idx in df.index:
        idx_lower = str(idx).lower()
        if any(kw in idx_lower for kw in keywords):
            # Берём последний квартал (последняя колонка)
            return df.loc[idx].iloc[-1]
    return None


def qoq_change(df):
    """Считает изменение квартал-к-кварталу (последние 2 колонки)."""
    if len(df.columns) < 2:
        return None
    
    current = df.iloc[:, -1]
    previous = df.iloc[:, -2]
    
    # Избегаем деления на ноль
    change = ((current - previous) / previous.abs().replace(0, pd.NA) * 100).fillna(0)
    return change.round(2)


def find_anomalies(df, threshold=30):
    """Находит аномалии: изменение > threshold%."""
    changes = qoq_change(df)
    if changes is None:
        return []
    
    anomalies = []
    for idx, val in changes.items():
        if abs(val) > threshold:
            anomalies.append({
                'item': idx,
                'change_pct': val,
                'direction': '↑' if val > 0 else '↓'
            })
    
    return sorted(anomalies, key=lambda x: abs(x['change_pct']), reverse=True)


def generate_report(df, margins, anomalies, output_path):
    """Генерирует Markdown отчёт."""
    lines = [
        "# Corporate Report Analysis",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Summary",
        f"- Report periods: {len(df.columns)}",
        f"- Line items: {len(df)}",
        f"- Anomalies found: {len(anomalies)}",
        "",
    ]
    
    # Margins
    if margins:
        lines.extend([
            "## Margins (latest quarter)",
            "",
        ])
        if 'gross_margin' in margins:
            lines.append(f"- **Gross Margin:** {margins['gross_margin']}%")
        if 'operating_margin' in margins:
            lines.append(f"- **Operating Margin:** {margins['operating_margin']}%")
        if 'net_margin' in margins:
            lines.append(f"- **Net Margin:** {margins['net_margin']}%")
        lines.append("")
    
    # QoQ changes
    changes = qoq_change(df)
    if changes is not None:
        lines.extend([
            "## Quarter-over-Quarter Changes",
            "",
            "| Item | Change |",
            "|------|--------|",
        ])
        for idx, val in changes.head(10).items():
            lines.append(f"| {idx} | {val:+.1f}% |")
        lines.append("")
    
    # Anomalies
    if anomalies:
        lines.extend([
            "## ⚠️ Anomalies (>30% change)",
            "",
            "| Item | Direction | Change |",
            "|------|-----------|--------|",
        ])
        for a in anomalies[:10]:
            lines.append(f"| {a['item']} | {a['direction']} | {a['change_pct']:+.1f}% |")
        lines.append("")
    
    # Raw data preview
    lines.extend([
        "## Latest Quarter Data",
        "",
    ])
    lines.append(df.iloc[:, -1].head(20).to_markdown())
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    return output_path


def main():
    parser = argparse.ArgumentParser(description='Corporate Reports Analyzer')
    parser.add_argument('--input', '-i', required=True, help='Excel/CSV report')
    parser.add_argument('--output', '-o', default='report.md', help='Output markdown')
    parser.add_argument('--compare', '-c', help='Compare with previous report')
    args = parser.parse_args()
    
    print(f"Loading report: {args.input}")
    df = load_report(args.input)
    print(f"Loaded: {len(df)} items × {len(df.columns)} periods")
    
    print("Calculating margins...")
    margins = calculate_margins(df)
    
    print("Checking for anomalies...")
    anomalies = find_anomalies(df)
    
    if args.compare:
        print(f"Comparing with: {args.compare}")
        # TODO: implement comparison logic
    
    print(f"Generating report: {args.output}")
    report_path = generate_report(df, margins, anomalies, args.output)
    
    print(f"Done: {report_path}")
    print(f"\n📊 Revenue: {margins.get('revenue', 'N/A')}")
    print(f"📈 Gross Margin: {margins.get('gross_margin', 'N/A')}%")
    print(f"⚠️ Anomalies: {len(anomalies)}")


if __name__ == '__main__':
    main()
