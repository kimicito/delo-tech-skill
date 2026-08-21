#!/usr/bin/env python3
"""
delo-tech-impreport.py — Выгрузка отчёта 13 "Движение по импорту"

Запуск (с окном браузера):
    python3 delo_tech_impreport.py --headed --date-from 01.08.2026 --date-to 21.08.2026

Требования:
    pip install playwright
    playwright install chromium
"""

import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

from playwright.sync_api import sync_playwright


def run_report(date_from: str, date_to: str, output: str, headed: bool = False):
    username = os.getenv("DELO_TECH_USERNAME", "pl_11640")
    password = os.getenv("DELO_TECH_PASSWORD", "Qwerty123")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not headed)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        
        try:
            # 1. Login
            print("Step 1/5: Login...")
            page.goto("https://rlisystems.ru/webiom/sso/", wait_until="networkidle")
            time.sleep(1)
            
            page.fill("input[type='text']", username)
            page.fill("input[type='password']", password)
            
            # Click by text content (handles both "Войти" and "Вход")
            page.locator("button", has_text="Войти").first.click()
            
            page.wait_for_url(lambda u: "conterra" in u, timeout=15000)
            print("  ✓ Logged in")
            
            # 2. Navigate to report
            print("Step 2/5: Navigate to report...")
            page.click("text=Дополнительные услуги")
            time.sleep(0.5)
            page.click("text=Отчетность по обработке груза")
            time.sleep(2)
            
            # Double-click on report 13
            page.locator("text=13. Движение по импорту").dblclick()
            time.sleep(1)
            print("  ✓ Form opened")
            
            # 3. Fill dates
            print(f"Step 3/5: Fill dates {date_from} — {date_to}...")
            page.wait_for_selector("text=Начало периода", timeout=10000)
            
            # Find date inputs by their current values
            inputs = page.query_selector_all("input[type='text']")
            filled = 0
            for inp in inputs:
                val = inp.get_attribute("value") or ""
                if ".2026" in val or ".2025" in val:
                    if filled == 0:
                        inp.fill(f"{date_from} 00:00")
                        filled += 1
                    elif filled == 1:
                        inp.fill(f"{date_to} 23:59")
                        filled += 1
                        break
            
            if filled < 2:
                # JavaScript fallback
                page.evaluate(f"""() => {{
                    document.querySelectorAll('input[type="text"]').forEach((inp, i) => {{
                        if (inp.value && inp.value.includes('2026')) {{
                            inp.value = i === 0 ? '{date_from} 00:00' : '{date_to} 23:59';
                            inp.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        }}
                    }});
                }}""")
            
            time.sleep(0.5)
            print("  ✓ Dates filled")
            
            # 4. Show report
            print("Step 4/5: Show report...")
            page.click("button:has-text('ПОКАЗАТЬ ОТЧЁТ')")
            page.wait_for_selector("text=ТЕРМИНАЛ ВРАНГЕЛЬ", timeout=20000)
            time.sleep(2)
            print("  ✓ Report loaded")
            
            # 5. Download Excel
            print("Step 5/5: Download Excel...")
            with page.expect_download(timeout=30000) as dl:
                # Click the diskette/save button (second button in toolbar)
                page.locator(".v-slot .v-button").nth(1).click()
            
            download = dl.value
            download.save_as(output)
            print(f"  ✓ Saved to: {output}")
            
            return output
            
        except Exception as e:
            page.screenshot(path="/tmp/delo_tech_error.png")
            print(f"  ✗ Error: {e}")
            print(f"  Screenshot: /tmp/delo_tech_error.png")
            raise
            
        finally:
            browser.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date-from", required=True, help="DD.MM.YYYY")
    parser.add_argument("--date-to", required=True, help="DD.MM.YYYY")
    parser.add_argument("--output", default="/tmp/import_report.xlsx")
    parser.add_argument("--headed", action="store_true", help="Show browser window")
    args = parser.parse_args()
    
    # Validate dates
    for d in [args.date_from, args.date_to]:
        try:
            datetime.strptime(d, "%d.%m.%Y")
        except ValueError:
            print(f"Invalid date: {d}. Use DD.MM.YYYY format.", file=sys.stderr)
            sys.exit(1)
    
    result = run_report(args.date_from, args.date_to, args.output, args.headed)
    print(f"\n✅ Done: {result}")


if __name__ == "__main__":
    main()
