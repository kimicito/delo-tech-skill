# cost-aware-router — Каскадная маршрутизация по цене

## Description

Платим за топ-модель только когда дешёвая не справилась: каскад от дешёвой к дорогой с проверкой качества (quality-gate).

## Triggers

- `/cost-aware-router`
- "выбери модель подешевле"
- "сократи расходы на LLM"
- "каскад моделей"
- "какую модель взять под задачу"

## Usage

1. Задай лестницу моделей по возрастанию цены: `CASCADE = [("gemini-flash",1),("sonnet-4.6",10),("opus-4.8",30)]`.
2. Дай `answer_fn(model, request)` и `quality_fn(request, answer)->[0..1]`.
3. Запусти каскад через `cost_router.py`.
4. Результат: `{model, answer, quality, cost}` — самая дешёвая модель, прошедшая gate.

## Files

- `cost_router.py` — движок каскада.

## When to Apply

Массовые/смешанные нагрузки, где часть запросов простая. Дополняй prompt caching (−90%) и batch (−50%).
