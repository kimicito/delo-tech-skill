#!/bin/bash
# check_updates.sh — Проверка обновлений ФГИС ЦС и писем Минстроя
# Запуск: 1-го числа каждого месяца (cron)
# Результат: лог + возможное обновление config/indexes.json

PROJECT_DIR="/root/.openclaw/workspace/projects/smeta"
LOG_FILE="/var/log/smeta_updates.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] === Проверка обновлений нормативов ===" | tee -a "$LOG_FILE"

# Проверяем ФГИС ЦС (если доступен)
echo "[$DATE] Проверка ФГИС ЦС..." | tee -a "$LOG_FILE"
FGIS_URL="https://fgiscs.minstroyrf.ru/frsn/reference/indexes/74a617f7-36bc-4990-a3aa-29ff20b9c0f4"

# Пытаемся получить страницу (timeout 30 сек)
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 30 "$FGIS_URL" 2>/dev/null)

if [ "$HTTP_CODE" = "200" ]; then
    echo "[$DATE] ФГИС ЦС доступен (HTTP 200)" | tee -a "$LOG_FILE"
    echo "[$DATE] ВНИМАНИЕ: Требуется ручная проверка индексов (curl -L $FGIS_URL)" | tee -a "$LOG_FILE"
else
    echo "[$DATE] ФГИС ЦС недоступен (HTTP $HTTP_CODE) — возможно geo-block или тех. работы" | tee -a "$LOG_FILE"
fi

# Проверяем publication.pravo.gov.ru на изменения в приказах
echo "[$DATE] Проверка изменений в приказах..." | tee -a "$LOG_FILE"
PRAVO_URL="http://publication.pravo.gov.ru"
HTTP_CODE_PRAVO=$(curl -s -o /dev/null -w "%{http_code}" --max-time 30 "$PRAVO_URL" 2>/dev/null)

if [ "$HTTP_CODE_PRAVO" = "200" ]; then
    echo "[$DATE] publication.pravo.gov.ru доступен" | tee -a "$LOG_FILE"
else
    echo "[$DATE] publication.pravo.gov.ru недоступен (HTTP $HTTP_CODE_PRAVO)" | tee -a "$LOG_FILE"
fi

# Итог
echo "[$DATE] Проверка завершена." | tee -a "$LOG_FILE"
echo "[$DATE] Действие: Проверить вручную ФГИС ЦС и прислать свежие данные для обновления config/indexes.json" | tee -a "$LOG_FILE"
echo "---" | tee -a "$LOG_FILE"
