#!/usr/bin/env python3
"""Fetch & Analyze Corporate Reports

Скачивает отчёт с сайта (URL) и запускает анализ.
Поддерживает: прямые ссылки на PDF/Excel, HTML-страницы (ищет ссылки на отчёты).
"""

import argparse
import sys
import re
import requests
from pathlib import Path
from urllib.parse import urljoin, urlparse
from datetime import datetime


def download_file(url, output_dir="data"):
    """Скачивает файл по прямой ссылке."""
    print(f"Downloading: {url}")
    response = requests.get(url, timeout=60, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    response.raise_for_status()
    
    # Определяем имя файла
    filename = Path(urlparse(url).path).name
    if not filename:
        filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    output_path = Path(output_dir) / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'wb') as f:
        f.write(response.content)
    
    print(f"Saved: {output_path} ({len(response.content)} bytes)")
    return output_path


def find_report_links(url):
    """Ищет ссылки на отчёты на HTML-странице."""
    print(f"Scanning page for report links: {url}")
    response = requests.get(url, timeout=60, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    response.raise_for_status()
    
    html = response.text
    
    # Ищем ссылки на PDF/Excel
    patterns = [
        r'href="([^"]+\.(?:pdf|xlsx|xls))"',
        r'href="([^"]+report[^"]*\.(?:pdf|xlsx|xls))"',
        r'href="([^"]+отч[её]т[^"]*\.(?:pdf|xlsx|xls))"',
    ]
    
    found = set()
    for pattern in patterns:
        for match in re.finditer(pattern, html, re.IGNORECASE):
            link = match.group(1)
            full_url = urljoin(url, link)
            found.add(full_url)
    
    if found:
        print(f"Found {len(found)} report links:")
        for link in sorted(found)[:5]:
            print(f"  - {link}")
    else:
        print("No direct report links found. Use --browser for JS-rendered pages.")
    
    return sorted(found)


def run_analyzer(file_path, output_path="reports/analysis.md"):
    """Запускает quarterly_analyzer.py на скачанном файле."""
    import subprocess
    
    cmd = [
        sys.executable,
        "scripts/quarterly_analyzer.py",
        "--input", str(file_path),
        "--output", str(output_path)
    ]
    
    print(f"\nRunning analyzer...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        return None
    
    return output_path


def main():
    parser = argparse.ArgumentParser(description='Fetch & Analyze Corporate Reports')
    parser.add_argument('--url', '-u', required=True, help='URL of report or page with reports')
    parser.add_argument('--output', '-o', default='reports/analysis.md', help='Output report')
    parser.add_argument('--data-dir', '-d', default='data', help='Download directory')
    parser.add_argument('--direct', action='store_true', help='URL is direct file link')
    args = parser.parse_args()
    
    print("=" * 50)
    print("Corporate Report: Fetch & Analyze")
    print("=" * 50)
    
    # Определяем тип URL
    if args.direct or args.url.endswith(('.pdf', '.xlsx', '.xls', '.csv')):
        # Прямая ссылка на файл
        file_path = download_file(args.url, args.data_dir)
    else:
        # HTML-страница — ищем ссылки
        links = find_report_links(args.url)
        if not links:
            print("\n❌ No reports found on page.")
            print("Tip: Use --direct if URL is a direct file link")
            print("Tip: Use browser-scraping skill for JS-rendered pages")
            sys.exit(1)
        
        # Скачиваем первый найденный
        file_path = download_file(links[0], args.data_dir)
    
    # Анализируем
    report_path = run_analyzer(file_path, args.output)
    
    if report_path:
        print(f"\n✅ Done! Report saved: {report_path}")
    else:
        print("\n❌ Analysis failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
