# Результаты звонков

В этой папке сохраняются результаты всех звонков.

## Формат файлов

`call_{CALL_ID}_{ДАТА}.json`

## Структура

```json
{
  "call_id": "abc123",
  "timestamp": "2026-08-25T10:30:00Z",
  "status": "completed",
  "phone_number": "+79001234567",
  "duration_seconds": 45,
  "cost_usd": 0.07,
  "transcript": "Алло... Да, здравствуйте...",
  "analysis": {
    "success": true,
    "summary": "Клиент согласен на встречу",
    "details": "Назначена встреча на завтра в 15:00"
  },
  "recording_url": "https://..."
}
```

## Получить результат

```bash
# Сразу после звонка (когда call_id известен)
node skills/bland-phone-caller/reference/scripts/get-result.js --call-id abc123
```
