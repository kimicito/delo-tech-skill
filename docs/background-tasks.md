# Background Tasks — паттерны мониторинга и автоматизации

## /loop — периодические проверки

Запускать повторяющиеся задачи через cron или heartbeat-скрипты.

### Примеры

```bash
# Проверка CI каждые 5 минут
# heartbeat: /loop 5m Check GitHub Actions status for open PRs

# Мониторинг дискового пространства
# heartbeat: /loop 1h Check disk space, alert if < 500MB

# Суммаризация новых коммитов
# heartbeat: /loop 2h Summarize new commits since last check
```

## monitor — стриминг событий

Для real-time событий: логи, file watchers, webhook-поллинг.

### Паттерн: мониторинг логов

```bash
# Watch errors in application log
tail -f /var/log/app.log | grep --line-buffered "ERROR"

# Watch file changes
inotifywait -m --format '%e %f' /watched/dir

# Poll remote API with rate-limit respect
while true; do
  curl -s https://api.example.com/status || true
  sleep 30
done
```

**Правила:**
- Всегда использовать `grep --line-buffered` в pipes
- Обрабатывать transient failures (`|| true`)
- Интервал 30s+ для remote APIs, 0.5–1s для local

## scheduler — отложенные и recurring задачи

### Одноразовая (напоминание)
```bash
# Напомнить через 20 минут
# scheduler_create: recurring=false, delay=20m, prompt="Напомни проверить почту"
```

### Постоянная (мониторинг)
```bash
# Каждые 5 минут проверять статус
# scheduler_create: interval=5m, prompt="Check test suite status"
```

## Улучшение heartbeat

Добавить в `HEARTBEAT.md`:
- `monitor` секцию для логов и CI
- `/loop` секцию для периодических проверок
- Ротация: email → calendar → мониторинг → (повтор)

## Приоритеты

| Приоритет | Проверка | Частота |
|-----------|----------|---------|
| P0 | CI failures, ERROR в логах | Real-time / 5m |
| P1 | Disk space, memory | 1h |
| P2 | Email, calendar | 2–4x / день |
| P3 | Новости, коммиты | 1–2x / день |
