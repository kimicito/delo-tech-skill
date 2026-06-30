#!/bin/bash
# Проверка наличия новых писем Минстроя на ФГИС ЦС
# Использует browser automation (JS SPA)
# Запуск: 0 9 1 * * (1-е число каждого месяца в 9:00)

LOG="/var/log/smeta_monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')
HISTORY_FILE="/root/.openclaw/workspace/skills/smeta/data/indices_history.json"

echo "[$DATE] === Проверка ФГИС ЦС (browser) ===" >> $LOG

# Проверяем через browser (JS SPA)
# Здесь будет вызов browser automation через OpenClaw API
# Или простая проверка: если сайт доступен — уведомить пользователя

STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://fgiscs.minstroyrf.ru/frsn/reference/indexes)

echo "[$DATE] ФГИС ЦС индексы: HTTP $STATUS" >> $LOG

if [ "$STATUS" = "200" ]; then
    echo "[$DATE] ✅ ФГИС ЦС доступен. Запуск browser automation..." >> $LOG
    # Browser automation выполняется через OpenClaw вручную или через API
    # Результат: если есть новые письма — уведомить пользователя
    echo "[$DATE] ⚠️ Нужно проверить новые письма на https://fgiscs.minstroyrf.ru/frsn/reference/indexes" >> $LOG
else
    echo "[$DATE] ❌ ФГИС ЦС недоступен (HTTP $STATUS)" >> $LOG
fi

echo "[$DATE] Проверка завершена" >> $LOG
echo "---" >> $LOG
