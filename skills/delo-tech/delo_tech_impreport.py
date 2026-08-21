#!/usr/bin/env python3
"""
delo-tech-impreport — Выгрузка отчёта 13 "Движение по импорту" из ДЕЛО ТЕХ

Usage:
    # Headless (требует X11 или xvfb-run для iframe-сайтов)
    xvfb-run python3 delo_tech_impreport.py --date-from 01.08.2026 --date-to 21.08.2026
    
    # Headed (с окном браузера, требует дисплей)
    python3 delo_tech_impreport.py --date-from 01.08.2026 --date-to 21.08.2026 --headed

Environment:
    DELO_TECH_USERNAME — логин
    DELO_TECH_PASSWORD — пароль
"""

import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


class DeloTechImportReport:
    """Client for downloading import report from ДЕЛО ТЕХ."""

    BASE_URL = "https://rlisystems.ru/conterra/"
    SSO_URL = "https://rlisystems.ru/webiom/sso/"

    def __init__(self, username: str = None, password: str = None, headless: bool = True, download_dir: str = "/tmp"):
        self.username = username or os.getenv("DELO_TECH_USERNAME", "")
        self.password = password or os.getenv("DELO_TECH_PASSWORD", "")
        self.headless = headless
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def _init_browser(self):
        """Initialize Playwright browser."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=["--no-sandbox", "--disable-dev-shm-usage"] if self.headless else []
        )
        self.context = self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            accept_downloads=True,
        )
        self.page = self.context.new_page()

    def login(self) -> bool:
        """Log in to ДЕЛО ТЕХ via SSO page."""
        if not self.username or not self.password:
            raise ValueError("DELO_TECH_USERNAME and DELO_TECH_PASSWORD required")

        self._init_browser()
        page = self.page

        # Open SSO page directly
        page.goto(self.SSO_URL, wait_until="networkidle")
        time.sleep(2)

        # Fill login form (button text is "Войти", not "Вход")
        page.fill("input[type='text']", self.username)
        page.fill("input[type='password']", self.password)
        
        # Click login and wait for navigation
        # Try multiple selectors for login button
        for selector in ["button:has-text('Войти')", "input[type='submit']", "button[type='submit']", ".btn-primary", "button.btn", "input[value*='Войти']"]:
            try:
                page.click(selector, timeout=5000)
                break
            except:
                continue
        else:
            # Fallback: click by coordinates
            page.mouse.click(600, 450)
        
        try:
            page.wait_for_url(lambda url: "conterra" in url and "sso" not in url, timeout=15000)
        except PlaywrightTimeout:
            pass

        time.sleep(3)
        return "conterra" in page.url and "sso" not in page.url

    def navigate_to_report(self):
        """Navigate to report 13 'Движение по импорту'."""
        page = self.page

        # Expand "Дополнительные услуги" menu
        page.click("text=Дополнительные услуги")
        time.sleep(1)

        # Click "Отчетность по обработке груза"
        page.click("text=Отчетность по обработке груза")
        time.sleep(3)

        # Wait for report list and double-click on "13. Движение по импорту"
        page.wait_for_selector("text=13. Движение по импорту", timeout=15000)
        report_item = page.locator("text=13. Движение по импорту")
        report_item.dblclick()
        time.sleep(2)

    def fill_form(self, date_from: str, date_to: str):
        """Fill the report form with date range."""
        page = self.page

        # Wait for form
        page.wait_for_selector("text=Начало периода", timeout=10000)

        # Find date inputs by scanning all text inputs
        inputs = page.query_selector_all("input[type='text']")
        
        date_start = None
        date_end = None
        
        for inp in inputs:
            val = inp.get_attribute("value") or ""
            if "2026" in val or "2025" in val:
                if date_start is None:
                    date_start = inp
                else:
                    date_end = inp
                    break

        if date_start and date_end:
            date_start.fill(f"{date_from} 00:00")
            date_end.fill(f"{date_to} 23:59")
        else:
            # JavaScript fallback
            page.evaluate(f"""() => {{
                const inputs = document.querySelectorAll('input[type="text"]');
                let found = 0;
                for (let inp of inputs) {{
                    if (inp.value && inp.value.match(/\\d{{2}}\\.\\d{{2}}\\.\\d{{4}}/)) {{
                        if (found === 0) {{
                            inp.value = '{date_from} 00:00';
                            inp.dispatchEvent(new Event('change'));
                            found++;
                        }} else if (found === 1) {{
                            inp.value = '{date_to} 23:59';
                            inp.dispatchEvent(new Event('change'));
                            break;
                        }}
                    }}
                }}
            }}""")

        time.sleep(1)

    def show_report(self):
        """Click 'ПОКАЗАТЬ ОТЧЁТ' button."""
        self.page.click("button:has-text('ПОКАЗАТЬ ОТЧЁТ')")
        self.page.wait_for_selector("text=ТЕРМИНАЛ ВРАНГЕЛЬ", timeout=20000)
        time.sleep(3)

    def download_excel(self, output_path: str) -> str:
        """Click diskette icon to download Excel."""
        page = self.page

        # Find save button (diskette icon) — second button in toolbar
        with page.expect_download(timeout=30000) as download_info:
            # Try clicking by position or icon
            buttons = page.query_selector_all("button")
            for btn in buttons:
                html = btn.inner_html()
                if "save" in html.lower() or "диск" in html.lower() or "💾" in html:
                    btn.click()
                    break
            else:
                # Fallback: click second toolbar button
                page.locator(".v-button >> nth=1").click()

        download = download_info.value
        download.save_as(output_path)
        return output_path

    def run(self, date_from: str, date_to: str, output: str) -> str:
        """Full workflow."""
        try:
            print("Step 1/5: Logging in...")
            if not self.login():
                raise RuntimeError("Login failed")
            print("  ✓ Logged in")

            print("Step 2/5: Navigating to report 13...")
            self.navigate_to_report()
            print("  ✓ Report form opened")

            print(f"Step 3/5: Setting dates {date_from} — {date_to}...")
            self.fill_form(date_from, date_to)
            print("  ✓ Dates set")

            print("Step 4/5: Loading report table...")
            self.show_report()
            print("  ✓ Table loaded")

            print("Step 5/5: Downloading Excel...")
            result = self.download_excel(output)
            print(f"  ✓ Saved: {result}")
            return result

        except PlaywrightTimeout as e:
            if self.page:
                debug_path = "/tmp/delo_tech_error.png"
                self.page.screenshot(path=debug_path, full_page=True)
                print(f"  ✗ Timeout. Debug screenshot: {debug_path}")
            raise

        finally:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()


def main():
    parser = argparse.ArgumentParser(
        description="ДЕЛО ТЕХ — Отчёт 13 'Движение по импорту'",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --date-from 01.08.2026 --date-to 21.08.2026
  %(prog)s --date-from 01.08.2026 --date-to 21.08.2026 --output report.xlsx
  xvfb-run %(prog)s --date-from 01.08.2026 --date-to 21.08.2026  # headless on Linux
        """
    )
    parser.add_argument("--date-from", required=True, help="Start date (DD.MM.YYYY)")
    parser.add_argument("--date-to", required=True, help="End date (DD.MM.YYYY)")
    parser.add_argument("--output", default="/tmp/import_report.xlsx", help="Output file path")
    parser.add_argument("--headed", action="store_true", help="Show browser window")
    parser.add_argument("--download-dir", default="/tmp", help="Download directory")
    args = parser.parse_args()

    # Validate dates
    for d in [args.date_from, args.date_to]:
        try:
            datetime.strptime(d, "%d.%m.%Y")
        except ValueError:
            print(f"Error: Invalid date '{d}'. Use DD.MM.YYYY format", file=sys.stderr)
            sys.exit(1)

    client = DeloTechImportReport(headless=not args.headed, download_dir=args.download_dir)
    result = client.run(args.date_from, args.date_to, args.output)
    print(f"\n✅ Report saved: {result}")


if __name__ == "__main__":
    main()
