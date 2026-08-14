# HEARTBEAT.md

```markdown
# Keep this file empty (or with only comments) to skip heartbeat API calls.

# Add tasks below when you want the agent to check something periodically.
```

## Автоматические проверки при heartbeat

### 1. Дисковое пространство
```bash
# Проверка
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')

# >90% — предупредить пользователя
# >95% — автоочистка старых чекпоинтов (оставить последние 3)
# >98% — критическое уведомление + полная очистка
```

**Скрипт очистки:** `~/.openclaw/workspace/scripts/cleanup-checkpoints.sh`
- Оставляет последние 3 чекпоинта на сессию
- Не влияет на: память, skills, проекты, .env, конфиги
- Только история чатов (session checkpoints)
- **Безопасно запускать:** `bash ~/.openclaw/workspace/scripts/cleanup-checkpoints.sh`
- **Симуляция:** `bash ~/.openclaw/workspace/scripts/cleanup-checkpoints.sh --dry-run`

### 2. Git статус
```bash
cd ~/.openclaw/workspace && git status --short
```
- Если есть изменения — закоммитить и push

