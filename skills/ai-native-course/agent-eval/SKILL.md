# agent-eval — Оценка агента и защита от регрессий

## Description

Превращает «вроде стало лучше» в число: фиксированный тест-сет + метрики → сравнение версий агента и блок регрессий.

## Triggers

- `/agent-eval`
- "оцени агента"
- "сравни версии агента"
- "есть ли регрессия"
- "прогони eval агента"

## Usage

1. Собери тест-сет `cases = [{"input": ..., "expected": ...}, ...]` (реальные задачи + эталоны, включая граничные).
2. Заведи версии как функции `versions = {"v1": agent_fn1, "v2": agent_fn2}`.
3. Выбери метрику (`task_success` или своя: tool-correctness, число шагов).
4. Прогон и сравнение через `agent_eval.py`.
5. Покажи `success_rate`, рейтинг версий и `has_regression(baseline, candidate, cases)`.

## Files

- `agent_eval.py` — `evaluate_agent`, `compare_versions`, `has_regression`.

## When to Apply

Перед мерджем правки агента/промпта/инструмента — прогони eval, поставь порог в CI, блокируй регрессии. Online-evals в проде — LangSmith/Phoenix.
