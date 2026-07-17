#!/usr/bin/env python3
"""Finance Audit — Subscription Killer

Анализирует CSV выписку, находит подписки, дубликаты, аномалии.
"""

import csv
import json
import sys
import argparse
from collections import defaultdict
from datetime import datetime


def load_transactions(csv_path):
    """Загружает CSV: date, amount, description, category (optional)"""
    transactions = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                amount = float(row['amount'].replace(',', '.').replace(' ', ''))
            except ValueError:
                amount = 0.0
            transactions.append({
                'date': row.get('date', ''),
                'amount': amount,
                'description': row.get('description', ''),
                'category': row.get('category', 'other')
            })
    return transactions


def find_subscriptions(transactions, threshold=0.05, min_occurrences=2):
    """Находит recurring payments (подписки) по повторяющимся описаниям."""
    by_desc = defaultdict(list)
    for t in transactions:
        # Normalize description: lower, strip numbers/dates
        desc = t['description'].lower()
        # Remove amounts/dates from desc for grouping
        key = ''.join(c for c in desc if c.isalpha() or c.isspace()).strip()[:20]
        if len(key) > 3:
            by_desc[key].append(t)
    
    subscriptions = []
    for key, items in by_desc.items():
        if len(items) >= min_occurrences:
            amounts = [abs(t['amount']) for t in items]
            avg = sum(amounts) / len(amounts)
            variance = max(abs(a - avg) for a in amounts) / avg if avg else 0
            if variance < threshold:  # Similar amounts = subscription
                monthly = avg * 12 if avg > 0 else 0
                subscriptions.append({
                    'name': items[0]['description'][:30],
                    'key': key,
                    'count': len(items),
                    'avg_amount': round(avg, 2),
                    'yearly_cost': round(monthly, 2),
                    'category': items[0]['category']
                })
    
    return sorted(subscriptions, key=lambda x: x['yearly_cost'], reverse=True)


def find_duplicates(subscriptions):
    """Находит дубликаты по категории/ключевым словам."""
    categories = defaultdict(list)
    for s in subscriptions:
        categories[s['category']].append(s)
    
    duplicates = []
    for cat, items in categories.items():
        if len(items) > 1:
            # Check for similar names
            for i in range(len(items)):
                for j in range(i + 1, len(items)):
                    if items[i]['key'] != items[j]['key'] and \
                       any(word in items[j]['name'].lower() for word in items[i]['name'].lower().split() if len(word) > 3):
                        duplicates.append({
                            'category': cat,
                            'sub1': items[i]['name'],
                            'sub2': items[j]['name'],
                            'yearly_total': round(items[i]['yearly_cost'] + items[j]['yearly_cost'], 2)
                        })
    return duplicates


def generate_report(transactions, subscriptions, duplicates, output_path):
    """Генерирует Markdown отчёт."""
    total_spent = sum(abs(t['amount']) for t in transactions)
    total_yearly_subs = sum(s['yearly_cost'] for s in subscriptions)
    
    lines = [
        "# Finance Audit Report",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Summary",
        f"- Total transactions: {len(transactions)}",
        f"- Total spent: {total_spent:,.2f} ₽",
        f"- Subscriptions found: {len(subscriptions)}",
        f"- Yearly subscription cost: {total_yearly_subs:,.2f} ₽",
        f"- Potential duplicates: {len(duplicates)}",
        "",
        "## Subscriptions (sorted by yearly cost)",
        "",
        "| Name | Count | Avg/Month | Yearly | Category |",
        "|------|-------|-----------|--------|----------|",
    ]
    
    for s in subscriptions:
        lines.append(f"| {s['name']} | {s['count']} | {s['avg_amount']:,.2f} ₽ | {s['yearly_cost']:,.2f} ₽ | {s['category']} |")
    
    if duplicates:
        lines.extend([
            "",
            "## ⚠️ Potential Duplicates",
            "",
        ])
        for d in duplicates:
            lines.append(f"- **{d['category']}**: {d['sub1']} + {d['sub2']} = {d['yearly_total']:,.2f} ₽/year")
    
    lines.extend([
        "",
        "## Recommendations",
        "",
        f"1. Review top subscriptions: potential savings = {total_yearly_subs * 0.2:,.2f} ₽/year (if cut 20%)",
    ])
    
    if duplicates:
        lines.append(f"2. Merge duplicates: save {sum(d['yearly_total'] for d in duplicates) * 0.5:,.2f} ₽/year (estimated)")
    
    lines.append("3. Check unused subscriptions: cancel if no activity for 90 days")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    return output_path


def main():
    parser = argparse.ArgumentParser(description='Finance Audit — Subscription Killer')
    parser.add_argument('--input', '-i', required=True, help='CSV file with transactions')
    parser.add_argument('--output', '-o', default='report.md', help='Output markdown report')
    args = parser.parse_args()
    
    print(f"Loading transactions from {args.input}...")
    transactions = load_transactions(args.input)
    print(f"Loaded {len(transactions)} transactions")
    
    print("Finding subscriptions...")
    subscriptions = find_subscriptions(transactions)
    print(f"Found {len(subscriptions)} subscriptions")
    
    print("Checking for duplicates...")
    duplicates = find_duplicates(subscriptions)
    print(f"Found {len(duplicates)} potential duplicates")
    
    print(f"Generating report: {args.output}")
    report_path = generate_report(transactions, subscriptions, duplicates, args.output)
    print(f"Done: {report_path}")
    
    # Print summary to stdout
    print(f"\n💰 Yearly subscription cost: {sum(s['yearly_cost'] for s in subscriptions):,.2f} ₽")
    if duplicates:
        print(f"⚠️  Potential duplicates: {len(duplicates)} (review recommended)")


if __name__ == '__main__':
    main()
