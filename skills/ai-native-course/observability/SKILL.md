# observability — Трейсинг шагов агента

## Description

Делает путь агента видимым: вложенные spans (шаг → подшаг) с атрибутами и длительностью — мини-OpenTelemetry для отладки в проде.

## Triggers

- `/observability`
- "трейс агента"
- "где тормозит агент"
- "добавь spans"
- "observability/tracing"

## Usage

1. Оберни шаги агента в spans через `Tracer.span()`.
2. Смотри дерево: `tr.spans` (name/parent/duration/attrs), `tr.total_duration()`, `tr.slowest()` — узкое место.
3. Для тестов подменяй `clock` на детерминированный.

```python
import tracer
tr = tracer.Tracer()
with tr.span("agent_run"):
    with tr.span("retrieve", k=3):
        ...
    with tr.span("llm_call", model="sonnet-4.6"):
        ...
```

## Files

- `tracer.py` — `Tracer.span(...)`, `total_duration()`, `slowest()`.

## When to Apply

Когда агент выдал странный результат или тормозит — трейс покажет, на каком шаге. В проде переноси на OpenTelemetry GenAI + Phoenix/LangSmith/Langfuse.
