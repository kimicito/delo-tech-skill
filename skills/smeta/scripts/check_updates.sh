#!/bin/bash
# Проверка доступности ФГИС ЦС и наличия новых писем Минстроя
# Запуск: 0 9 1 * * (1-е число каждого месяца в 9:00)

LOG="/var/log/smeta_monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Проверяем ФГИС ЦС
echo "[$DATE] Проверка ФГИС ЦС..." >> $LOG

# Проверка цен (SPA — требуется JS, но статус HTTP можно проверить)
STATUS_PRICES=$(curl -s -o /dev/null -w "%{http_code}" https://fgiscs.minstroyrf.ru/prices)
STATUS_INDEXES=$(curl -s -o /dev/null -w "%{http_code}" https://fgiscs.minstroyrf.ru/frsn/reference/indexes/74a617f7-36bc-4990-a3aa-29ff20b9c0f4)

echo "[$DATE] fgiscs.minstroyrf.ru/prices: HTTP $STATUS_PRICES" >> $LOG
echo "[$DATE] fgiscs.minstroyrf.ru/indexes: HTTP $STATUS_INDEXES" >> $LOG

# Если доступны — уведомить пользователя (через OpenClaw message или лог)
if [ "$STATUS_PRICES" = "200" ] && [ "$STATUS_INDEXES" = "200" ]; then
    echo "[$DATE] ⚠️ ФГИС ЦС доступен! Проверить новые письма Минстроя: https://fgiscs.minstroyrf.ru/prices" >> $LOG
    # Можно добавить отправку уведомления через OpenClaw API
else
    echo "[$DATE] ❌ ФГИС ЦС недоступен (геоблок). Нужен PDF от пользователя." >> $LOG
fi

# Проверка gge.ru (Приказ 421/пр)
STATUS_GGE=$(curl -s -o /dev/null -w "%{http_code}" "https://gge.ru/upload/iblock/7a4/4gxng03p845iv50n47nh50jv49tkwn3o/%D0%9F%D1%80%D0%B8%D0%BA%D0%B0%D0%B7%20%D0%9C%D0%B8%D0%BD%D1%81%D1%82%D1%80%D0%BE%D1%8F%20%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D0%B8%20%D0%BE%D1%82%2004.08.2020%20N%20421_%D0%BF%D1%80%20(%D1%80%D0%B5%D0%B4.%20%D0%BE%D1%82%2030.01.pdf")
echo "[$DATE] gge.ru (Приказ 421/пр): HTTP $STATUS_GGE" >> $LOG

echo "[$DATE] Проверка завершена" >> $LOG
echo "---" >> $LOG
