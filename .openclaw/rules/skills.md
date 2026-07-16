# Skills — правила

Для: все custom skills в `~/.openclaw/workspace/skills/`

## Структура skill

```
skills/skill-name/
  SKILL.md            # Обязательно! Описание + workflow
  script.py           # Главный скрипт (если есть)
  README.md           # Дополнительная документация
  tests/              # Тесты (если скрипт)
  examples/           # Примеры input/output
```

## SKILL.md — обязательные секции

1. **Название** — краткое, понятное
2. **Описание** — что делает, зачем нужен
3. **Workflow** — пошаговая инструкция
4. **Input** — что нужно предоставить пользователю
5. **Output** — что получится на выходе
6. **Примеры** — минимум 1 пример использования

## Именование

- Kebab-case: `skill-name`, `wb-tax-calculator`
- Без пробелов, без camelCase
- Русские названия — только в SKILL.md, директория на английском

## Интеграция с OpenClaw

- Скрипты должны быть CLI-friendly: argparse, stdin/stdout
- Должны работать без интерактивного ввода (всё через flags)
- Exit code: 0 = success, 1 = error, 2 = bad args

## Обновление реестра

После добавления нового skill:
```bash
python3 scripts/update-skills-registry.py
```
Это обновляет `memory/skills-registry.json` и `memory/ontology/graph.jsonl`.
