# HEARTBEAT.md

```markdown
# Keep this file empty (or with only comments) to skip heartbeat API calls.

# Add tasks below when you want the agent to check something periodically.
```

## Автоматические проверки при heartbeat

### 1. Дисковое пространство
```bash
df -h / | awk 'NR==2 {print $5}' | sed 's/%//'
```
- **>90%** — предупредить пользователя
- **>98%** — критическое уведомление + автоочистка

### 2. Git статус
```bash
cd ~/.openclaw/workspace && git status --short
```
- Если есть изменения — закоммитить и push

### 3. Instagram cron
```bash
crontab -l | grep logistoria
```
- Проверить, что cron активен

### 4. Заявки Instagram (если есть)
```bash
cd ~/.openclaw/workspace/projects/logistoria-social && python3 scripts/check_leads.py
```
