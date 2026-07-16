# Headless Automation — автоматизация без интерактивной сессии

Запускать OpenClaw/skills из скриптов, cron, CI без TUI.

## Паттерн: One-shot skill

```bash
# Запуск skill с аргументами
python3 skills/wb-tax-calculator/calculator.py --registry реестр.xlsx --details детализация.xlsx

# Сохранить output в файл
python3 skills/wb-tax-calculator/calculator.py --registry реестр.xlsx > result.csv
```

## Паттерн: Subagent из скрипта

```bash
# Запустить read-only subagent для анализа
openclaw run --read-only "Analyze codebase in /path/to/project and report issues"
```

## Паттерн: Cron + skill

```bash
# crontab: ежедневный бэкап
0 2 * * * cd ~/.openclaw/workspace && bash backup.sh "daily backup"

# crontab: проверка disk space
0 * * * * df -h / | awk 'NR==2{if($5 > 90) print "DISK ALERT: "$5}' | telegram-send
```

## Паттерн: CI pipeline

```yaml
# .github/workflows/update-course.yml
- name: Update search index
  run: |
    cd projects/ai-nontechnical-course
    npx pagefind --source . --glob "**/*.html"
    git add pagefind/
    git diff --cached --quiet || git commit -m "[course] Update search index"
```

## Паттерн: Batch processing

```bash
# Обработать несколько файлов
for file in data/*.xlsx; do
  python3 skills/my-skill/script.py --input "$file" --output "results/$(basename $file .xlsx).csv"
done
```

## Правила headless-скриптов

- **Не интерактивные**: всё через CLI flags, env vars, или config files
- **Deterministic**: одинаковый input = одинаковый output
- **Idempotent**: можно запускать несколько раз без побочных эффектов
- **Логирование**: stdout для результатов, stderr для ошибок, exit code для статуса

## Примеры use-case

| Use case | Команда | Частота |
|----------|---------|---------|
| Обновление search index | `pagefind --source .` | После каждого commit |
| Генерация PDF | `python3 generate-pdf.py` | По запросу |
| Скрейпинг цен | `python3 skills/browser-scraping/...` | Раз в день |
| Бэкап workspace | `bash backup.sh` | Ежедневно |
| Проверка disk space | `df -h` | Каждый час |
