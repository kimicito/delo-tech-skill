#!/usr/bin/env python3
"""
delo-tech — Automation for ДЕЛО ТЕХ (rlisystems.ru/conterra/)

Usage:
    python delo_tech.py --action login
    python delo_tech.py --action balance
    python delo_tech.py --action orders
"""

import os
import sys
import time
import argparse
from dataclasses import dataclass
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


@dataclass
class DashboardInfo:
    """Parsed dashboard data."""
    user: str
    company: str
    inn: str
    balance: str
    terminal: str
    orders: list


class DeloTechClient:
    """Client for ДЕЛО ТЕХ automation."""

    BASE_URL = os.getenv("DELOTECH_BASE_URL", "https://rlisystems.ru/conterra/")
    SSO_URL = os.getenv("DELOTECH_SSO_URL", "https://rlisystems.ru/webiom/sso/")
    TIMEOUT = int(os.getenv("DELOTECH_TIMEOUT", "30"))

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None, headless: bool = True):
        self.username = username or os.getenv("DELOTECH_USERNAME", "")
        self.password = password or os.getenv("DELOTECH_PASSWORD", "")
        self.headless = headless
        self.driver: Optional[webdriver.Chrome] = None
        self._logged_in = False

    def _init_driver(self) -> webdriver.Chrome:
        """Initialize Chrome WebDriver."""
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument(
            "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        try:
            self.driver = webdriver.Chrome(options=options)
        except Exception:
            # Fallback: try with default ChromeDriver path
            try:
                service = Service()
                self.driver = webdriver.Chrome(service=service, options=options)
            except Exception as e:
                raise RuntimeError(
                    f"Failed to initialize Chrome WebDriver: {e}\n"
                    "Install Chrome and chromedriver:\n"
                    "  apt-get install chromium-browser chromium-chromedriver\n"
                    "Or use: playwright install chromium"
                )

        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        return self.driver

    def login(self) -> bool:
        """Log in to ДЕЛО ТЕХ. Returns True on success."""
        if not self.username or not self.password:
            raise ValueError("Username and password required. Set DELOTECH_USERNAME and DELOTECH_PASSWORD env vars.")

        if self.driver is None:
            self._init_driver()

        driver = self.driver
        wait = WebDriverWait(driver, self.TIMEOUT)

        # Open direct SSO page (avoids iframe issues)
        driver.get(self.SSO_URL)
        time.sleep(2)

        # Find and fill login form
        try:
            # Try by name first
            user_field = driver.find_element(By.NAME, "user")
        except NoSuchElementException:
            # Fallback: find first visible text input
            user_field = driver.find_element(By.XPATH, "//input[@type='text']")

        try:
            pass_field = driver.find_element(By.NAME, "password")
        except NoSuchElementException:
            pass_field = driver.find_element(By.XPATH, "//input[@type='password']")

        user_field.clear()
        user_field.send_keys(self.username)

        pass_field.clear()
        pass_field.send_keys(self.password)

        # Click login button
        try:
            login_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
        except NoSuchElementException:
            login_btn = driver.find_element(By.XPATH, "//input[@type='submit']")

        login_btn.click()

        # Wait for redirect to dashboard (or error)
        time.sleep(3)

        # Check if we're logged in (look for dashboard elements)
        current_url = driver.current_url
        if "error" in current_url.lower():
            # Sometimes there's an intermediate error page, wait for auto-redirect
            time.sleep(5)
            current_url = driver.current_url

        self._logged_in = "webiom" in current_url and "sso" not in current_url
        return self._logged_in

    def get_page_source(self) -> str:
        """Get current page HTML."""
        if self.driver is None:
            raise RuntimeError("Not initialized. Call login() first.")
        return self.driver.page_source

    def get_current_url(self) -> str:
        """Get current URL."""
        if self.driver is None:
            return ""
        return self.driver.current_url

    def parse_dashboard(self) -> Optional[DashboardInfo]:
        """Parse dashboard info from current page."""
        if not self._logged_in:
            return None

        source = self.get_page_source()
        # Basic parsing — can be enhanced with BeautifulSoup
        return None  # TODO: implement parsing

    def screenshot(self, path: str = "delo_tech_screenshot.png") -> str:
        """Take screenshot of current page."""
        if self.driver is None:
            raise RuntimeError("Not initialized. Call login() first.")
        self.driver.save_screenshot(path)
        return path

    def close(self):
        """Close browser and cleanup."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self._logged_in = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def main():
    parser = argparse.ArgumentParser(description="ДЕЛО ТЕХ Automation")
    parser.add_argument("--action", choices=["login", "balance", "orders", "screenshot"], default="login")
    parser.add_argument("--username", help="Login username")
    parser.add_argument("--password", help="Login password")
    parser.add_argument("--headless", action="store_true", default=True, help="Run in headless mode")
    parser.add_argument("--no-headless", dest="headless", action="store_false", help="Show browser window")
    args = parser.parse_args()

    client = DeloTechClient(
        username=args.username,
        password=args.password,
        headless=args.headless
    )

    try:
        if args.action == "login":
            success = client.login()
            print(f"Login: {'SUCCESS' if success else 'FAILED'}")
            print(f"Current URL: {client.get_current_url()}")
            if success:
                path = client.screenshot("delo_tech_dashboard.png")
                print(f"Screenshot saved: {path}")

        elif args.action == "screenshot":
            client.login()
            path = client.screenshot()
            print(f"Screenshot saved: {path}")

        elif args.action in ("balance", "orders"):
            client.login()
            print(f"Action '{args.action}' — TODO: implement parsing")
            print(f"Current URL: {client.get_current_url()}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    main()
