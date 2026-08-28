#!/usr/bin/env python3
"""
Навигация по ДЕЛО ТЕХ — отчёт 13 (Движение по импорту).

Использует Playwright для кликов (Vaadin принимает только реальные события браузера).

Запуск:
    python navigate_report13.py --start-date 12.08.2026 --end-date 28.08.2026

Ограничения:
    - Максимум 30 дней (ограничение ДЕЛО ТЕХ)
    - Требуется активная сессия (пользователь авторизован)
    - Chrome должен быть запущен с --remote-debugging-port=18800

Процесс:
    1. Подключается к CDP (порт 18800)
    2. Кликает "Отчеты" → "Отчетность по обработке груза" → "13. Движение по импорту"
    3. Заполняет даты
    4. Нажимает "ПОКАЗАТЬ ОТЧЕТ"
    5. Отчёт загружается в iframe
"""
import asyncio
import json
import sys
import argparse
import urllib.request
from typing import Optional

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("❌ Установите Playwright: pip install playwright")
    print("   Затем: playwright install chromium")
    sys.exit(1)


class DeloTechNavigator:
    """Навигатор по ДЕЛО ТЕХ с использованием Playwright."""
    
    def __init__(self, cdp_port: int = 18800):
        self.cdp_port = cdp_port
        self.page = None
    
    async def connect(self):
        """Подключается к существующему Chrome через CDP."""
        # Получаем WebSocket URL из CDP
        with urllib.request.urlopen(f"http://127.0.0.1:{self.cdp_port}/json") as response:
            pages = json.loads(response.read())
        
        # Ищем авторизованную страницу ДЕЛО ТЕХ
        target_url = None
        for page in pages:
            url = page.get("url", "")
            title = page.get("title", "")
            if "rlisystems.ru" in url and "pl_" in title:
                target_url = page["webSocketDebuggerUrl"]
                break
        
        if not target_url:
            print("❌ Авторизованная страница ДЕЛО ТЕХ не найдена")
            print("   Убедитесь, что:")
            print("   1. Chrome запущен с --remote-debugging-port=18800")
            print("   2. Вы авторизованы в ДЕЛО ТЕХ")
            sys.exit(1)
        
        # Подключаемся через Playwright
        playwright = await async_playwright().start()
        browser = await playwright.chromium.connect_over_cdp(f"http://127.0.0.1:{self.cdp_port}")
        
        # Ищем страницу ДЕЛО ТЕХ
        for page in browser.pages:
            if "rlisystems.ru" in page.url:
                self.page = page
                break
        
        if not self.page:
            print("❌ Страница ДЕЛО ТЕХ не найдена в браузере")
            sys.exit(1)
        
        print(f"✅ Подключено: {self.page.url}")
    
    async def navigate_to_report13(self):
        """Навигирует к отчёту 13 через меню."""
        print("🔄 Навигация к отчёту 13...")
        
        # Шаг 1: Клик на "Отчеты"
        print("  → Клик 'Отчеты'")
        await self.page.click('text="Отчеты"')
        await asyncio.sleep(1)
        
        # Шаг 2: Клик на "Отчетность по обработке груза"
        print("  → Клик 'Отчетность по обработке груза'")
        await self.page.click('text="Отчетность по обработке груза"')
        await asyncio.sleep(2)
        
        # Шаг 3: Клик на "13. Движение по импорту"
        print("  → Клик '13. Движение по импорту'")
        await self.page.click('text="13. Движение по импорту"')
        await asyncio.sleep(2)
        
        print("✅ Форма отчёта 13 открыта")
    
    async def fill_dates(self, start_date: str, end_date: str):
        """Заполняет даты в форме отчёта."""
        print(f"🔄 Заполнение дат: {start_date} - {end_date}")
        
        # Находим поля дат (gwt-uid-11 и gwt-uid-13)
        # или используем placeholder
        try:
            # Пробуем по placeholder
            start_field = await self.page.query_selector('input[placeholder*="Начало"]')
            if not start_field:
                # Пробуем по ID
                start_field = await self.page.query_selector('input[id*="gwt-uid"][type="text"]')
            
            if start_field:
                await start_field.fill(start_date)
                print(f"  → Начало периода: {start_date}")
            
            # End date — следующее поле
            all_inputs = await self.page.query_selector_all('input[type="text"]')
            for inp in all_inputs:
                val = await inp.get_attribute('value') or ''
                if start_date in val:
                    # Следующее поле — конец периода
                    pass
            
            # Пробуем по label
            end_fields = await self.page.query_selector_all('input[type="text"]')
            for i, field in enumerate(end_fields):
                val = await field.get_attribute('value') or ''
                if start_date in val and i + 1 < len(end_fields):
                    await end_fields[i + 1].fill(end_date)
                    print(f"  → Окончание периода: {end_date}")
                    break
            
        except Exception as e:
            print(f"⚠️ Ошибка заполнения дат: {e}")
            print("   Возможно, форма ещё не загрузилась")
    
    async def click_show_report(self):
        """Нажимает кнопку 'ПОКАЗАТЬ ОТЧЕТ'."""
        print("🔄 Нажатие 'ПОКАЗАТЬ ОТЧЕТ'...")
        
        try:
            await self.page.click('text="ПОКАЗАТЬ ОТЧЕТ"')
            print("✅ Кнопка нажата")
            await asyncio.sleep(5)  # Ждём загрузки
        except Exception as e:
            print(f"⚠️ Ошибка: {e}")
    
    async def run(self, start_date: str, end_date: str):
        """Полный цикл навигации."""
        await self.connect()
        await self.navigate_to_report13()
        await self.fill_dates(start_date, end_date)
        await self.click_show_report()
        
        print("\n✅ Отчёт загружен!")
        print("   Теперь можно извлечь данные через delo_tech.py")
        print(f"   python delo_tech.py --action report --report-type 13 \\")
        print(f"       --start-date {start_date} --end-date {end_date}")


def main():
    parser = argparse.ArgumentParser(description='Навигация к отчёту 13 в ДЕЛО ТЕХ')
    parser.add_argument('--start-date', required=True, help='Начало периода (DD.MM.YYYY)')
    parser.add_argument('--end-date', required=True, help='Конец периода (DD.MM.YYYY)')
    parser.add_argument('--cdp-port', type=int, default=18800, help='CDP порт (default: 18800)')
    
    args = parser.parse_args()
    
    print(f"🚀 Навигация к отчёту 13: {args.start_date} - {args.end_date}")
    print()
    
    navigator = DeloTechNavigator(cdp_port=args.cdp_port)
    asyncio.run(navigator.run(args.start_date, args.end_date))


if __name__ == "__main__":
    main()
