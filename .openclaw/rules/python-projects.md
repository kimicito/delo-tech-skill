# Python Projects — правила

Для: drawings-to-vor, skills/*, wb-tax-calculator, ozon-tax-calculator

## Стек и conventions

- **Python 3.10+**, type hints где возможно
- **Venv**: каждый проект — свой venv
- **Зависимости**: `requirements.txt` или `pyproject.toml`
- **Тесты**: `pytest` или `unittest`, минимум 70% coverage для критичного кода

## Файловая структура

```
project/
  main.py / script.py
  requirements.txt
  tests/
    test_main.py
  README.md
```

## API Keys и secrets

- **Никогда** не хардкодить ключи в коде
- Использовать `.env` файл + `python-dotenv`
- `.env` добавить в `.gitignore`

## OCR / AI-скрипты

- **Preprocessing**: tile больших изображений перед OCR
- **API**: Qwen-VL-OCR, OpenAI Vision, или другие
- **Rate limits**: добавить sleep между запросами (минимум 1s)
- **Retry**: 3 попытки с exponential backoff

## Калькуляторы (tax, etc.)

- **Input**: Excel/CSV через pandas
- **Output**: CSV или stdout
- **Валидация**: проверять наличие обязательных столбцов
- **Тесты**: минимум 3 тест-кейса (happy path, edge cases, error handling)
