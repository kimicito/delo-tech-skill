#!/bin/bash
# cleanup-checkpoints.sh - Автоматическая очистка старых чекпоинтов сессий
# Запуск: bash cleanup-checkpoints.sh [--dry-run]

set -euo pipefail

SESSIONS_DIR="/root/.openclaw/agents/main/sessions"
KEEP_COUNT=3
DRY_RUN=0
LOG_FILE="/root/.openclaw/workspace/logs/cleanup-$(date +%Y%m%d-%H%M%S).log"

# Проверка аргументов
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=1
    echo "[DRY-RUN] Ничего не удаляю, только показываю что бы удалилось"
fi

# Создаём лог-директорию
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_FILE"
}

# Проверяем существование директории
if [[ ! -d "$SESSIONS_DIR" ]]; then
    log "ERROR: Директория $SESSIONS_DIR не найдена"
    exit 1
fi

# Получаем список уникальных сессий
mapfile -t SESSIONS < <(find "$SESSIONS_DIR" -maxdepth 1 -name "*.checkpoint.*.jsonl" | sed 's/.*\/\([a-f0-9-]*\)\.checkpoint.*/\1/' | sort -u)

if [[ ${#SESSIONS[@]} -eq 0 ]]; then
    log "INFO: Чекпоинты не найдены"
    exit 0
fi

TOTAL_FREED=0
TOTAL_DELETED=0

for SESSION in "${SESSIONS[@]}"; do
    # Получаем все чекпоинты сессии, отсортированные по времени (новые первые)
    mapfile -t CHECKPOINTS < <(find "$SESSIONS_DIR" -maxdepth 1 -name "${SESSION}.checkpoint.*.jsonl" -printf '%T@ %p\n' | sort -rn | cut -d' ' -f2-)
    
    COUNT=${#CHECKPOINTS[@]}
    
    if [[ $COUNT -le $KEEP_COUNT ]]; then
        continue
    fi
    
    TO_DELETE=$(($COUNT - $KEEP_COUNT))
    log "INFO: Сессия $SESSION - $COUNT чекпоинтов, удаляю $TO_DELETE (оставляю $KEEP_COUNT)"
    
    # Удаляем старые (все после первых KEEP_COUNT)
    for ((i=KEEP_COUNT; i<COUNT; i++)); do
        FILE="${CHECKPOINTS[$i]}"
        SIZE=$(stat -c%s "$FILE" 2>/dev/null || echo 0)
        SIZE_MB=$((SIZE / 1024 / 1024))
        
        if [[ $DRY_RUN -eq 0 ]]; then
            rm -f "$FILE"
            log "DELETED: $(basename "$FILE") (${SIZE_MB}Mb)"
        else
            log "[DRY-RUN] Будет удалено: $(basename "$FILE") (${SIZE_MB}Mb)"
        fi
        
        TOTAL_FREED=$((TOTAL_FREED + SIZE))
        TOTAL_DELETED=$((TOTAL_DELETED + 1))
    done
done

# Конвертируем байты в Mb
TOTAL_FREED_MB=$((TOTAL_FREED / 1024 / 1024))

if [[ $DRY_RUN -eq 0 ]]; then
    log "DONE: Удалено $TOTAL_DELETED чекпоинтов, освобождено ${TOTAL_FREED_MB}Mb"
    
    # Показываем текущее состояние диска
    DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    DISK_AVAIL=$(df -h / | awk 'NR==2 {print $4}')
    log "DISK: Использовано ${DISK_USAGE}%, доступно $DISK_AVAIL"
    
    # Предупреждение если всё ещё мало места
    if [[ $DISK_USAGE -gt 90 ]]; then
        log "WARNING: Диск всё ещё заполнен на ${DISK_USAGE}%! Требуется дополнительная очистка."
    fi
else
    log "[DRY-RUN] Было бы удалено $TOTAL_DELETED чекпоинтов, освобождено ${TOTAL_FREED_MB}Mb"
fi

echo ""
echo "Лог: $LOG_FILE"
