#!/usr/bin/env python3
"""
ДЕЛО ТЕХ — ядро системы.

Единая точка входа для всех операций.
Управляет сессией, CDP-подключением и роутингом задач.

Примеры использования:
    >>> from skills.delo-tech.delo_tech import DeloTechCore
    >>> core = DeloTechCore()
    >>> 
    # Отчёт 13 — Импорт
    >>> result = core.run_report("import", start_date="01.08.2026", end_date="21.08.2026")
    >>> print(result['xlsx'])
    
    # Статус контейнера
    >>> status = core.get_container_status("TKRU3055043")
    
    # Релиз-ордера
    >>> orders = core.get_release_orders()

Архитектура:
    ┌─────────────────────────────────────┐
    │         delo_tech.py (ядро)         │
    │  - Сессия                           │
    │  - CDP-клиент                       │
    │  - Роутер операций                  │
    └──────────────┬──────────────────────┘
                   │
    ┌──────────────┼──────────────┬──────────────┐
    ▼              ▼              ▼              ▼
┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐
│reports/│   │operat- │   │customs/│   │utils/  │
│        │   │ions/   │   │        │   │        │
│-import │   │-status │   │-docs   │   │-cdp    │
│-export │   │-orders │   │-declar │   │-excel  │
│-balance│   │-docs   │   │        │   │-session│
└────────┘   └────────┘   └────────┘   └────────┘
"""
import asyncio
import json
import csv
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ReportConfig:
    """Конфигурация отчёта."""
    report_type: str           # "13", "7", "balance" и т.д.
    start_date: str            # DD.MM.YYYY
    end_date: str              # DD.MM.YYYY
    contract_id: Optional[str] = None
    additional_params: Optional[Dict[str, Any]] = None


@dataclass  
class OperationResult:
    """Результат операции."""
    success: bool
    data: Optional[Any] = None
    files: Optional[Dict[str, str]] = None  # пути к файлам
    message: str = ""
    row_count: Optional[int] = None


class CDPClient:
    """Клиент Chrome DevTools Protocol.
    
    Управляет подключением к Chrome и выполнением скриптов.
    """
    
    def __init__(self, port: int = 18800):
        self.port = port
        self._ws_url: Optional[str] = None
    
    async def connect(self) -> bool:
        """Находит страницу ДЕЛО ТЕХ в CDP.
        
        Returns:
            True если подключение успешно
        """
        import urllib.request
        
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/json") as response:
                pages = json.loads(response.read())
                
                # Сначала ищем авторизованную страницу (с именем пользователя в title)
                for page in pages:
                    url = page.get("url", "")
                    title = page.get("title", "")
                    if "rlisystems.ru" in url and "reports" not in url:
                        # Авторизованная страница содержит pl_ (ID пользователя)
                        if "pl_" in title:
                            self._ws_url = page["webSocketDebuggerUrl"]
                            return True
                
                # Fallback — любая страница ДЕЛО ТЕХ
                for page in pages:
                    url = page.get("url", "")
                    if "rlisystems.ru" in url and "reports" not in url:
                        self._ws_url = page["webSocketDebuggerUrl"]
                        return True
                        
        except Exception as e:
            print(f"❌ Ошибка подключения к CDP: {e}")
            return False
        
        return False
    
    async def execute(self, script: str) -> Optional[str]:
        """Выполняет JavaScript в контексте страницы.
        
        Args:
            script: JavaScript-код для выполнения
            
        Returns:
            Результат выполнения (строка)
        """
        import websockets
        
        if not self._ws_url:
            if not await self.connect():
                return None
        
        async with websockets.connect(self._ws_url) as ws:
            # Включаем Runtime
            await ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
            
            while True:
                msg = await ws.recv()
                data = json.loads(msg)
                if data.get("id") == 1:
                    break
            
            # Выполняем скрипт
            await ws.send(json.dumps({
                "id": 2,
                "method": "Runtime.evaluate",
                "params": {
                    "expression": f"(function(){{ {script} }})()",
                    "returnByValue": True
                }
            }))
            
            while True:
                msg = await ws.recv()
                data = json.loads(msg)
                if data.get("id") == 2:
                    break
            
            if "result" in data and "result" in data["result"]:
                return data["result"]["result"].get("value")
            
            return None
    
    async def extract_table_data(self, iframe_index: int = 1) -> Optional[str]:
        """Извлекает данные таблицы из основного документа (Vaadin больше не в iframe)."""
        script = """
            try {
                // Ищем таблицы в основном документе
                let csv = '';
                const tables = document.querySelectorAll('table');
                
                for (let t of tables) {
                    const rows = t.querySelectorAll('tr');
                    for (let r of rows) {
                        const cells = r.querySelectorAll('td, th');
                        if (cells.length > 3) {
                            let row = [];
                            for (let c of cells) {
                                row.push(c.textContent.trim().replace(/\\s+/g, ' '));
                            }
                            csv += row.join(';') + '\\n';
                        }
                    }
                }
                return csv || 'no tables found';
            } catch(e) {
                return 'error: ' + e.message;
            }
        """
        
        return await self.execute(script)


class SessionManager:
    """Управление сессией пользователя.
    
    Проверяет, авторизован ли пользователь, 
    управляет cookies и состоянием.
    """
    
    def __init__(self, cdp: CDPClient):
        self.cdp = cdp
        self._is_authenticated: Optional[bool] = None
    
    async def check_auth(self) -> bool:
        """Проверяет, авторизован ли пользователь."""
        script = """
            const hasDashboard = document.querySelector('.v-app') !== null;
            const hasLogin = document.querySelector('input[type="password"]') !== null;
            const hasBalance = document.body.textContent.includes('Баланс:');
            return (hasDashboard && !hasLogin) || hasBalance;
        """
        
        result = await self.cdp.execute(script)
        # CDP возвращает boolean True/False
        self._is_authenticated = bool(result)
        return self._is_authenticated
    
    async def ensure_auth(self) -> bool:
        """Гарантирует, что пользователь авторизован.
        
        Если не авторизован — предупреждает.
        
        Returns:
            True если можно продолжать
        """
        if await self.check_auth():
            return True
        
        print("⚠️ Пользователь не авторизован в ДЕЛО ТЕХ")
        print("Пожалуйста, войдите в систему через браузер:")
        print("https://rlisystems.ru/conterra/")
        return False


class ReportManager:
    """Управление отчётами.
    
    Все операции с отчётами: извлечение, конвертация, сохранение.
    
    Рабочий метод (август 2026):
    1. Пользователь открывает отчёт 13 в браузере вручную
    2. Агент подключается через CDP к авторизованной странице
    3. Извлекает таблицу из основного документа (Vaadin больше не в iframe)
    4. Сохраняет в CSV и Excel
    
    Навигация по меню Vaadin автоматически НЕ работает — 
    только извлечение данных из уже открытого отчёта.
    """
    
    def __init__(self, cdp: CDPClient, output_dir: Path):
        self.cdp = cdp
        self.output_dir = output_dir
    
    async def extract(self, config: ReportConfig) -> OperationResult:
        """Извлекает отчёт и сохраняет в файлы.
        
        Args:
            config: Конфигурация отчёта
            
        Returns:
            Результат операции с путями к файлам
        """
        # Извлекаем данные из основного документа
        csv_data = await self.cdp.extract_table_data()
        
        if not csv_data or csv_data.startswith('error:'):
            return OperationResult(
                success=False,
                message=f"Ошибка извлечения: {csv_data}"
            )
        
        if csv_data == 'no tables found':
            return OperationResult(
                success=False,
                message="Таблицы не найдены. Убедитесь, что отчёт открыт в браузере."
            )
        
        # Сохраняем CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"report_{config.report_type}_{timestamp}.csv"
        csv_path = self.output_dir / csv_filename
        
        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write(csv_data)
        
        # Конвертируем в Excel
        xlsx_filename = csv_filename.replace('.csv', '.xlsx')
        xlsx_path = self.output_dir / xlsx_filename
        self._csv_to_excel(csv_path, xlsx_path)
        
        row_count = len([l for l in csv_data.strip().split('\n') if l.strip()])
        
        return OperationResult(
            success=True,
            data=csv_data,
            files={
                'csv': str(csv_path),
                'xlsx': str(xlsx_path)
            },
            message=f"Отчёт {config.report_type} извлечён ({row_count} строк)",
            row_count=row_count
        )
    
    def _csv_to_excel(self, csv_path: Path, xlsx_path: Path):
        """Конвертирует CSV в Excel."""
        from openpyxl import Workbook
        
        wb = Workbook()
        ws = wb.active
        ws.title = 'Данные'
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                ws.append(row)
        
        wb.save(xlsx_path)


class DeloTechCore:
    """Ядро системы ДЕЛО ТЕХ.
    
    Единая точка входа для всех операций.
    Управляет сессией, CDP-подключением и выполняет задачи.
    
    Attributes:
        cdp: Клиент CDP
        session: Менеджер сессии
        reports: Менеджер отчётов
        output_dir: Директория для сохранения файлов
    
    Example:
        >>> core = DeloTechCore()
        >>> result = core.run_report("13", "01.08.2026", "21.08.2026")
        >>> print(result.files['xlsx'])
    """
    
    def __init__(self, output_dir: Optional[str] = None, cdp_port: int = 18800):
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).parent
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Инициализируем компоненты
        self.cdp = CDPClient(port=cdp_port)
        self.session = SessionManager(self.cdp)
        self.reports = ReportManager(self.cdp, self.output_dir)
    
    def run_report(self, report_type: str, start_date: str, end_date: str,
                   contract_id: Optional[str] = None) -> OperationResult:
        """Запускает извлечение отчёта.
        
        Args:
            report_type: Тип отчёта ("13", "7", "balance" и т.д.)
            start_date: Начало периода (DD.MM.YYYY)
            end_date: Конец периода (DD.MM.YYYY)
            contract_id: ID договора (опционально)
            
        Returns:
            Результат операции с файлами
            
        Example:
            >>> core = DeloTechCore()
            >>> result = core.run_report("13", "01.08.2026", "21.08.2026")
            >>> if result.success:
            ...     print(f"Сохранено {result.row_count} строк")
            ...     print(f"Excel: {result.files['xlsx']}")
        """
        # Проверяем авторизацию
        auth_ok = asyncio.run(self.session.ensure_auth())
        if not auth_ok:
            return OperationResult(
                success=False,
                message="Требуется авторизация в ДЕЛО ТЕХ"
            )
        
        # Формируем конфигурацию
        config = ReportConfig(
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            contract_id=contract_id
        )
        
        # Запускаем извлечение
        return asyncio.run(self.reports.extract(config))
    
    async def _get_container_status_async(self, container_number: str) -> Dict[str, Any]:
        """Асинхронное получение статуса контейнера.
        
        Args:
            container_number: Номер контейнера (например, "TKRU3055043")
            
        Returns:
            Словарь со статусом контейнера
        """
        # TODO: Реализовать поиск контейнера в интерфейсе
        script = f"""
            // Ищем контейнер в таблице
            const frame = document.querySelectorAll('iframe')[1];
            const doc = frame.contentDocument || frame.contentWindow.document;
            
            const rows = doc.querySelectorAll('tr');
            for (let r of rows) {{
                const cells = r.querySelectorAll('td');
                if (cells.length > 1 && cells[1].textContent.includes('{container_number}')) {{
                    return JSON.stringify({{
                        container: '{container_number}',
                        status: cells[0].textContent,
                        location: cells.length > 5 ? cells[5].textContent : ''
                    }});
                }}
            }}
            return JSON.stringify({{error: 'Контейнер не найден'}});
        """
        
        result = await self.cdp.execute(script)
        if result:
            return json.loads(result)
        return {"error": "Не удалось получить статус"}
    
    def get_container_status(self, container_number: str) -> Dict[str, Any]:
        """Получает статус контейнера.
        
        Args:
            container_number: Номер контейнера
            
        Returns:
            Словарь со статусом
        """
        return asyncio.run(self._get_container_status_async(container_number))
    
    def get_release_orders(self) -> List[Dict[str, Any]]:
        """Получает список релиз-ордеров.
        
        Returns:
            Список релиз-ордеров
        """
        # TODO: Реализовать переход в раздел релиз-ордеров
        pass
    
    def get_balance(self) -> Dict[str, Any]:
        """Получает баланс.
        
        Returns:
            Словарь с балансом
        """
        # TODO: Реализовать переход в раздел баланса
        pass


# CLI-интерфейс
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='ДЕЛО ТЕХ — автоматизация')
    parser.add_argument('--action', choices=['report', 'status', 'orders', 'balance'],
                       required=True, help='Действие')
    parser.add_argument('--report-type', default='13', help='Тип отчёта')
    parser.add_argument('--start-date', help='Начало периода (DD.MM.YYYY)')
    parser.add_argument('--end-date', help='Конец периода (DD.MM.YYYY)')
    parser.add_argument('--container', help='Номер контейнера')
    parser.add_argument('--output', '-o', default='.', help='Директория для сохранения')
    
    args = parser.parse_args()
    
    core = DeloTechCore(output_dir=args.output)
    
    if args.action == 'report':
        if not args.start_date or not args.end_date:
            print("❌ Укажите --start-date и --end-date")
            sys.exit(1)
        
        result = core.run_report(args.report_type, args.start_date, args.end_date)
        
        if result.success:
            print(f"✅ {result.message}")
            print(f"   Строк: {result.row_count}")
            print(f"   CSV:   {result.files['csv']}")
            print(f"   Excel: {result.files['xlsx']}")
        else:
            print(f"❌ {result.message}")
    
    elif args.action == 'status':
        if not args.container:
            print("❌ Укажите --container")
            sys.exit(1)
        
        status = core.get_container_status(args.container)
        print(json.dumps(status, indent=2, ensure_ascii=False))
    
    elif args.action == 'orders':
        orders = core.get_release_orders()
        print(json.dumps(orders, indent=2, ensure_ascii=False))
    
    elif args.action == 'balance':
        balance = core.get_balance()
        print(json.dumps(balance, indent=2, ensure_ascii=False))
