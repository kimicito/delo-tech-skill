#!/usr/bin/env python3
"""
Site Tester — основной скрипт для тестирования сайтов
Генерирует структурированный отчёт для автоматического исправления
"""

import asyncio
import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

from playwright.async_api import async_playwright


class SiteTester:
    def __init__(self, base_url, email=None, output_dir=None):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.email = email or os.getenv('TESTER_EMAIL', '')
        self.visited_urls = set()
        self.broken_links = []
        self.forms = []
        self.console_errors = []
        self.performance_data = {}
        self.responsive_issues = []
        self.issues = []  # Структурированные проблемы для исправления
        self.screenshots_dir = None
        
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            self.output_dir = Path('reports') / timestamp
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.screenshots_dir = self.output_dir / 'screenshots'
        self.screenshots_dir.mkdir(exist_ok=True)
    
    def add_issue(self, severity, category, title, description, location, fix_suggestion, auto_fixable=False):
        """Добавление структурированной проблемы."""
        issue = {
            'id': len(self.issues) + 1,
            'severity': severity,  # critical, major, minor
            'category': category,  # navigation, forms, email, responsive, performance, content, seo, security
            'title': title,
            'description': description,
            'location': location,
            'fix_suggestion': fix_suggestion,
            'auto_fixable': auto_fixable,  # Можно ли исправить автоматически
            'status': 'open'
        }
        self.issues.append(issue)
        return issue['id']
    
    async def test_site(self):
        """Запуск полного тестирования."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
            
            print(f"🚀 Начинаю тестирование: {self.base_url}")
            
            await self.crawl_site(context)
            await self.test_forms(context)
            await self.test_responsiveness(browser)
            await self.test_performance(context)
            await self.collect_console_errors(context)
            
            await browser.close()
            
            self.generate_report()
            
            print(f"\n✅ Тестирование завершено!")
            print(f"📁 Отчёт: {self.output_dir}/report.md")
            print(f"🔧 Actionable items: {self.output_dir}/actionable.json")
    
    def _normalize_url(self, url):
        """Нормализация URL — убираем якоря (#) для избежания дублей."""
        return url.split('#')[0]
    
    async def crawl_site(self, context, max_pages=50):
        """Обход страниц с проверкой ссылок."""
        print("\n📄 Обход страниц...")
        
        page = await context.new_page()
        to_visit = [self._normalize_url(self.base_url)]
        
        while to_visit and len(self.visited_urls) < max_pages:
            url = to_visit.pop(0)
            normalized = self._normalize_url(url)
            if normalized in self.visited_urls:
                continue
            
            try:
                response = await page.goto(url, wait_until='networkidle', timeout=30000)
                self.visited_urls.add(normalized)
                status = response.status if response else 0
                
                if status >= 400:
                    self.broken_links.append({'url': url, 'status': status})
                    self.add_issue(
                        severity='major' if status == 404 else 'critical',
                        category='navigation',
                        title=f'Битая ссылка ({status})',
                        description=f'Страница вернула статус {status}',
                        location=url,
                        fix_suggestion='Проверить URL, исправить или удалить ссылку',
                        auto_fixable=False
                    )
                
                # Собираем внутренние ссылки (только http/https)
                links = await page.eval_on_selector_all('a[href]', '''
                    links => links.map(link => ({
                        href: link.href,
                        text: link.textContent.trim(),
                        is_external: !link.href.includes(window.location.host),
                        is_navigable: link.href.startsWith('http') || link.href.startsWith('/')
                    }))
                ''')
                
                for link in links:
                    normalized_link = self._normalize_url(link['href'])
                    if not link['is_external'] and link['is_navigable']:
                        if normalized_link not in self.visited_urls and normalized_link not in [self._normalize_url(u) for u in to_visit]:
                            to_visit.append(link['href'])
                        
            except Exception as e:
                self.add_issue(
                    severity='critical',
                    category='navigation',
                    title='Страница не загружается',
                    description=str(e),
                    location=url,
                    fix_suggestion='Проверить сервер, DNS, конфигурацию',
                    auto_fixable=False
                )
        
        await page.close()
        print(f"  ✅ Проверено: {len(self.visited_urls)} страниц")
        print(f"  ❌ Битых ссылок: {len(self.broken_links)}")
    
    async def test_forms(self, context):
        """Тестирование форм."""
        print("\n📝 Тестирование форм...")
        
        page = await context.new_page()
        
        for url in list(self.visited_urls)[:10]:
            normalized_url = self._normalize_url(url)
            try:
                await page.goto(url, wait_until='networkidle', timeout=30000)
                forms = await page.query_selector_all('form')
                
                for i, form in enumerate(forms):
                    form_data = {'page': normalized_url, 'form_index': i, 'fields': [], 'issues': []}
                    
                    inputs = await form.query_selector_all('input, textarea, select')
                    for inp in inputs:
                        field_type = await inp.get_attribute('type') or 'text'
                        field_name = await inp.get_attribute('name') or 'unnamed'
                        is_required = await inp.get_attribute('required') is not None
                        has_label = await inp.evaluate('el => !!el.labels.length') or False
                        
                        form_data['fields'].append({
                            'name': field_name,
                            'type': field_type,
                            'required': is_required,
                            'has_label': has_label
                        })
                        
                        # Проблема: поле без лейбла (проверяем и <label> и aria-label)
                        has_aria_label = await inp.get_attribute('aria-label') is not None
                        has_title = await inp.get_attribute('title') is not None
                        is_labeled = has_label or has_aria_label or has_title
                        
                        if not is_labeled and field_type not in ['hidden', 'submit']:
                            self.add_issue(
                                severity='major',
                                category='forms',
                                title='Поле формы без label',
                                description=f'Поле {field_name} ({field_type}) не имеет связанного label, aria-label или title',
                                location=f'{normalized_url} — форма #{i}',
                                fix_suggestion='Добавить <label for="id"> или aria-label',
                                auto_fixable=True
                            )
                    
                    # Проверяем кнопку отправки
                    submit = await form.query_selector('button[type="submit"], input[type="submit"]')
                    if not submit:
                        self.add_issue(
                            severity='critical',
                            category='forms',
                            title='Форма без кнопки отправки',
                            description='Форма не имеет кнопки type="submit"',
                            location=f'{normalized_url} — форма #{i}',
                            fix_suggestion='Добавить <button type="submit">Отправить</button>',
                            auto_fixable=True
                        )
                    
                    self.forms.append(form_data)
                    
            except Exception as e:
                print(f"  ❌ Ошибка на {url}: {e}")
        
        await page.close()
        print(f"  ✅ Проверено форм: {len(self.forms)}")
    
    async def test_responsiveness(self, browser):
        """Проверка адаптивности."""
        print("\n📱 Проверка адаптивности...")
        
        viewports = [
            {'width': 1920, 'height': 1080, 'name': 'desktop'},
            {'width': 768, 'height': 1024, 'name': 'tablet'},
            {'width': 375, 'height': 667, 'name': 'mobile'}
        ]
        
        for viewport in viewports:
            ctx = await browser.new_context(viewport=viewport)
            page = await ctx.new_page()
            
            try:
                await page.goto(self.base_url, wait_until='networkidle', timeout=30000)
                
                # Проверяем горизонтальный скролл
                has_scroll = await page.evaluate('''() => {
                    return document.documentElement.scrollWidth > window.innerWidth;
                }''')
                
                if has_scroll and viewport['name'] in ['tablet', 'mobile']:
                    self.add_issue(
                        severity='major',
                        category='responsive',
                        title=f'Горизонтальный скролл на {viewport["name"]}',
                        description=f'Контент не помещается в ширину viewport ({viewport["width"]}px)',
                        location=self.base_url,
                        fix_suggestion='Проверить overflow, ширину элементов, media queries',
                        auto_fixable=False
                    )
                
                # Делаем скриншот
                await page.screenshot(path=str(self.screenshots_dir / f"{viewport['name']}.png"), full_page=True)
                
            except Exception as e:
                self.add_issue(
                    severity='major',
                    category='responsive',
                    title=f'Ошибка на {viewport["name"]}',
                    description=str(e),
                    location=self.base_url,
                    fix_suggestion='Проверить адаптивные стили',
                    auto_fixable=False
                )
            
            await page.close()
            await ctx.close()
    
    async def test_performance(self, context):
        """Проверка скорости."""
        print("\n⚡ Проверка скорости...")
        
        page = await context.new_page()
        
        try:
            start = time.time()
            response = await page.goto(self.base_url, wait_until='networkidle', timeout=30000)
            load_time = time.time() - start
            
            self.performance_data = {
                'url': self.base_url,
                'load_time': round(load_time, 2),
                'status': response.status if response else 0
            }
            
            if load_time > 3:
                self.add_issue(
                    severity='major',
                    category='performance',
                    title='Медленная загрузка страницы',
                    description=f'Время загрузки: {load_time:.1f}s (цель: < 3s)',
                    location=self.base_url,
                    fix_suggestion='Оптимизировать изображения, включить сжатие, использовать CDN',
                    auto_fixable=False
                )
            
        except Exception as e:
            self.add_issue(
                severity='critical',
                category='performance',
                title='Ошибка загрузки',
                description=str(e),
                location=self.base_url,
                fix_suggestion='Проверить сервер, оптимизировать ресурсы',
                auto_fixable=False
            )
        
        await page.close()
    
    async def collect_console_errors(self, context):
        """Сбор ошибок консоли."""
        print("\n🔍 Сбор ошибок...")
        
        page = await context.new_page()
        
        page.on('console', lambda msg: self.console_errors.append({
            'type': msg.type, 'text': msg.text
        }))
        page.on('pageerror', lambda err: self.console_errors.append({
            'type': 'pageerror', 'text': str(err)
        }))
        
        try:
            await page.goto(self.base_url, wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(3000)
            
            errors = [e for e in self.console_errors if e['type'] in ['error', 'pageerror']]
            
            for error in errors[:10]:  # Лимитируем
                self.add_issue(
                    severity='major',
                    category='content',
                    title=f'JS ошибка: {error["text"][:50]}',
                    description=error['text'],
                    location=self.base_url,
                    fix_suggestion='Исправить JavaScript код',
                    auto_fixable=False
                )
            
        except Exception as e:
            pass
        
        await page.close()
    
    def generate_report(self):
        """Генерация отчётов."""
        # JSON с actionable items
        actionable = {
            'timestamp': datetime.now().isoformat(),
            'url': self.base_url,
            'total_issues': len(self.issues),
            'critical': len([i for i in self.issues if i['severity'] == 'critical']),
            'major': len([i for i in self.issues if i['severity'] == 'major']),
            'minor': len([i for i in self.issues if i['severity'] == 'minor']),
            'auto_fixable': len([i for i in self.issues if i['auto_fixable']]),
            'issues': self.issues
        }
        
        with open(self.output_dir / 'actionable.json', 'w', encoding='utf-8') as f:
            json.dump(actionable, f, ensure_ascii=False, indent=2)
        
        # Markdown отчёт
        self._generate_markdown()
        
        return actionable
    
    def _generate_markdown(self):
        """Генерация Markdown."""
        md = f"""# UX/UI Отчёт тестирования

**URL:** {self.base_url}  
**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Статус:** {'✅ Всё хорошо' if not self.issues else '⚠️ Найдены проблемы'}

---

## 📊 Сводка

| Метрика | Значение |
|---------|----------|
| Проверено страниц | {len(self.visited_urls)} |
| Битые ссылки | {len(self.broken_links)} |
| Форм проверено | {len(self.forms)} |
| Всего проблем | {len(self.issues)} |
| 🔴 Critical | {len([i for i in self.issues if i['severity'] == 'critical'])} |
| 🟡 Major | {len([i for i in self.issues if i['severity'] == 'major'])} |
| 🟢 Minor | {len([i for i in self.issues if i['severity'] == 'minor'])} |
| 🤖 Auto-fixable | {len([i for i in self.issues if i['auto_fixable']])} |

---

## 🔴 Critical Issues

"""
        
        critical = [i for i in self.issues if i['severity'] == 'critical']
        if critical:
            for issue in critical:
                md += f"""### #{issue['id']}: {issue['title']}

- **Категория:** {issue['category']}
- **Локация:** `{issue['location']}`
- **Описание:** {issue['description']}
- **Исправление:** {issue['fix_suggestion']}
- **Auto-fix:** {'✅ Да' if issue['auto_fixable'] else '❌ Нет'}

---

"""
        else:
            md += "Критических проблем не найдено. ✅\n\n---\n\n"
        
        md += """## 🟡 Major Issues

"""
        
        major = [i for i in self.issues if i['severity'] == 'major']
        if major:
            for issue in major:
                md += f"""### #{issue['id']}: {issue['title']}

- **Локация:** `{issue['location']}`
- **Описание:** {issue['description']}
- **Исправление:** {issue['fix_suggestion']}

---

"""
        else:
            md += "Major проблем не найдено. ✅\n\n---\n\n"
        
        md += """## 📋 Формы

"""
        if self.forms:
            for form in self.forms:
                md += f"**Страница:** `{form['page']}`\n\n"
                md += "| Поле | Тип | Обязательное | Label |\n"
                md += "|------|-----|--------------|-------|\n"
                for field in form['fields']:
                    md += f"| {field['name']} | {field['type']} | {'Да' if field['required'] else 'Нет'} | {'✅' if field['has_label'] else '❌'} |\n"
                md += "\n---\n\n"
        
        md += """## ⚡ Производительность

"""
        if self.performance_data:
            md += f"- **Время загрузки:** {self.performance_data.get('load_time', 'N/A')}s\n"
            md += f"- **Статус:** {self.performance_data.get('status', 'N/A')}\n"
        
        md += """

---

## ✅ Рекомендации по исправлению

"""
        
        auto_fixable = [i for i in self.issues if i['auto_fixable']]
        manual_fix = [i for i in self.issues if not i['auto_fixable']]
        
        if auto_fixable:
            md += "### 🤖 Автоматическое исправление\n\n"
            for issue in auto_fixable:
                md += f"- [ ] #{issue['id']}: {issue['title']} — `{issue['location']}`\n"
            md += "\n"
        
        if manual_fix:
            md += "### 🔧 Ручное исправление\n\n"
            for issue in manual_fix:
                md += f"- [ ] #{issue['id']}: {issue['title']}\n"
            md += "\n"
        
        with open(self.output_dir / 'report.md', 'w', encoding='utf-8') as f:
            f.write(md)
        
        return md


def main():
    parser = argparse.ArgumentParser(description='UX Site Tester')
    parser.add_argument('--url', required=True, help='URL для тестирования')
    parser.add_argument('--email', help='Email для форм')
    parser.add_argument('--output', '-o', help='Директория отчёта')
    
    args = parser.parse_args()
    tester = SiteTester(args.url, args.email, args.output)
    asyncio.run(tester.test_site())


if __name__ == '__main__':
    main()
