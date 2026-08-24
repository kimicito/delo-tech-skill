---
name: bland-phone-caller
description: Make AI-powered phone calls via Bland.ai. Supports outbound calls (agent calls someone) and inbound setup (agent receives calls). Uses human-like voice AI for conversations.
version: 1.0.0
author: kimicito
metadata:
  openclaw:
    requires:
      env:
        - BLAND_API_KEY
      bins:
        - curl
        - jq
    primaryEnv: BLAND_API_KEY
---

# Bland.ai Phone Caller

AI-звонки через Bland.ai. Агент может звонить от вашего имени и принимать звонки.

## Стоимость

- **$0.14/минута** (тариф Start)
- **Бесплатный входящий номер** включён
- **100 звонков/день** лимит на Start
- Оплата только за фактическое время разговора

## Быстрый старт

### 1. Получить API ключ

1. Зарегистрируйтесь на [app.bland.ai](https://app.bland.ai)
2. Получите API ключ в настройках
3. Добавьте в `.env`:

```bash
BLAND_API_KEY=your_key_here
```

### 2. Исходящий звонок

**Простой звонок:**
```bash
curl -X POST https://api.bland.ai/v1/calls \
  -H "authorization: $BLAND_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+79001234567",
    "task": "Поздоровайтесь и скажите, что это тестовый звонок от AI ассистента",
    "voice": "ru-RU-Standard-A",
    "language": "ru",
    "max_duration": 300
  }'
```

**С конкретной целью:**
```bash
curl -X POST https://api.bland.ai/v1/calls \
  -H "authorization: $BLAND_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+79001234567",
    "task": "Запишите человека на приём к стоматологу на завтра в 15:00. Имя: Иван. Уточните адрес клиники и стоимость.",
    "voice": "ru-RU-Standard-A",
    "language": "ru",
    "max_duration": 600,
    "record": true,
    "webhook": "https://your-webhook.com/call-completed"
  }'
```

### 3. Проверить статус звонка

```bash
curl -X GET "https://api.bland.ai/v1/calls/{call_id}" \
  -H "authorization: $BLAND_API_KEY"
```

### 4. Получить запись

```bash
curl -X GET "https://api.bland.ai/v1/calls/{call_id}/recording" \
  -H "authorization: $BLAND_API_KEY"
```

## Параметры API

| Параметр | Тип | Описание | Обязательный |
|----------|-----|----------|--------------|
| `phone_number` | string | Номер в формате E.164 (+7900...) | ✅ |
| `task` | string | Что сказать/спросить у агента | ✅ |
| `voice` | string | Голос (см. список ниже) | ❌ |
| `language` | string | Язык ("ru", "en", etc.) | ❌ |
| `max_duration` | integer | Макс. длительность в секундах | ❌ |
| `record` | boolean | Записывать разговор | ❌ |
| `webhook` | string | URL для уведомления о завершении | ❌ |

## Голоса

| Код | Описание |
|-----|----------|
| `ru-RU-Standard-A` | Русский, женский |
| `ru-RU-Standard-B` | Русский, мужской |
| `en-US-Standard-A` | Английский, женский |
| `en-US-Standard-B` | Английский, мужской |

## Входящие звонки

### 1. Получить номер

```bash
curl -X POST https://api.bland.ai/v1/inbound-numbers \
  -H "authorization: $BLAND_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "area_code": "495",
    "country": "RU"
  }'
```

### 2. Настроить обработчик

```bash
curl -X PATCH "https://api.bland.ai/v1/inbound-numbers/{number_id}" \
  -H "authorization: $BLAND_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Вы — AI ассистент. Помогите клиенту с вопросами о наших услугах. Если нужно — запишите на приём.",
    "voice": "ru-RU-Standard-A",
    "language": "ru"
  }'
```

## Скрипт-обёртка

Используйте готовый скрипт для удобства:

```bash
# Исходящий звонок
node skills/bland-phone-caller/reference/scripts/call.js \
  --to +79001234567 \
  --task "Запишите на приём завтра в 15:00"

# С записью и webhook
node skills/bland-phone-caller/reference/scripts/call.js \
  --to +79001234567 \
  --task "Уточните статус заказа №12345" \
  --record \
  --webhook https://example.com/webhook
```

## Примеры задач

| Задача | Пример task |
|--------|-------------|
| Запись на приём | "Запишите Ивана Иванова на приём к терапевту на завтра в 14:00" |
| Уточнение заказа | "Уточните статус заказа №12345 и срок доставки" |
| Сбор информации | "Узнайте график работы и стоимость услуг" |
| Напоминание | "Напомните о встрече завтра в 10:00" |
| Опрос | "Проведите короткий опрос удовлетворённости" |

## Ограничения Start тарифа

- **100 звонков/день**
- **10 одновременных звонков**
- **$0.14/минута**
- **Бесплатный входящий номер**
- **Запись разговоров** включена

## Безопасность

⚠️ **Важно:**
- Не звоните на номера без согласия (spam)
- Предупреждайте, что это AI-звонок
- Соблюдайте законы о телемаркетинге
- Храните API ключ в `.env`, не в коде

## Полезные ссылки

- [Bland.ai Dashboard](https://app.bland.ai)
- [API Documentation](https://docs.bland.ai)
- [Pricing](https://www.bland.ai/pricing)
