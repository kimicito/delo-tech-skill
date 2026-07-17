# AI Pipeline — Orchestrating AI Pipeline

**Путь:** `projects/ai-pipeline/`
**Репо:** `github.com/kimicito/openclaw-workspace`

## Что делает

Последовательный pipeline: Шаг 1 → Шаг 2 → Шаг 3. Retry на ошибке, checkpoint после каждого шага.

**Пример для контента:**
1. Сгенерировать слайды (openclaw-slides skill)
2. Сделать озвучку (tts)
3. Залить на YouTube (browser)
4. Отправить ссылку в Telegram

## Архитектура

```
Input → [Step 1] → Checkpoint → [Step 2] → Checkpoint → [Step 3] → Output
              ↓ error              ↓ error
           Retry 3x            Retry 3x
              ↓ fail              ↓ fail
           Alert user          Alert user
```

## Запуск

### Через Telegram
```
/pipeline name:course topic:"ИИ для закупщика"
```

### Через CLI
```bash
python scripts/pipeline.py --config config/pipelines.json --pipeline course --input "ИИ для закупщика"
```

### Через Cron
```bash
# Еженедельный контент
0 10 * * 1 openclaw run projects/ai-pipeline --pipeline weekly_content
```

## Структура

```
ai-pipeline/
├── scripts/
│   └── pipeline.py         # State machine, executor
├── config/
│   └── pipelines.json      # Определения pipeline'ов
├── state/                  # Checkpoint'ы (не в git)
├── output/                 # Результаты (не в git)
└── SKILL.md                # Этот файл
```

## Pipeline Definition (pipelines.json)

```json
{
  "pipelines": [
    {
      "id": "course",
      "name": "Course Content Pipeline",
      "steps": [
        {
          "id": "slides",
          "name": "Generate Slides",
          "skill": "openclaw-slides",
          "input_template": "Создай курс: {input}",
          "output_format": "pptx",
          "retry": 3,
          "timeout": 300
        },
        {
          "id": "voiceover",
          "name": "Generate Voiceover",
          "skill": "tts",
          "input_from": "slides",
          "output_format": "mp3",
          "retry": 3,
          "timeout": 120
        },
        {
          "id": "youtube",
          "name": "Upload to YouTube",
          "skill": "browser",
          "action": "upload",
          "input_from": "voiceover",
          "retry": 2,
          "timeout": 600
        },
        {
          "id": "notify",
          "name": "Send Telegram",
          "skill": "telegram",
          "action": "send",
          "message": "Курс готов: {youtube_url}",
          "retry": 1
        }
      ]
    }
  ]
}
```

## State Machine

```python
states = ["idle", "running", "step_N", "retry", "failed", "completed"]

transitions = {
    "idle": "running",
    "running": "step_N",
    "step_N": "step_N+1" or "retry",
    "retry": "step_N" or "failed",
    "failed": "alert",
    "completed": "deliver"
}
```

## Checkpoint System

После каждого шага pipeline сохраняет state в `state/{pipeline_id}_{timestamp}.json`:

```json
{
  "pipeline_id": "course",
  "current_step": 2,
  "completed_steps": [0, 1],
  "outputs": {
    "slides": "/output/course_2026-07-18.pptx",
    "voiceover": "/output/course_2026-07-18.mp3"
  },
  "errors": []
}
```

**Восстановление:** Если pipeline упал — перезапуск продолжает с последнего checkpoint.

## Error Handling

| Сценарий | Действие |
|----------|----------|
| API timeout | Retry через 30s |
| API error 5xx | Retry через 60s |
| API error 4xx | Skip step + alert |
| Step failed 3x | Pipeline failed → alert user |
| Disk full | Pause pipeline → alert |

## Требования

- **RAM:** 200-500M (последовательно, не параллельно)
- **Время:** Зависит от pipeline (курс: 10-30 минут)
- **Disk:** Зависит от выходных файлов (PPTX, MP3, видео)

## Пример Telegram Output

```
✅ Pipeline completed: course
📊 Steps: 4/4
⏱ Time: 18 min
📁 Output: https://youtube.com/watch?v=...
```

## Безопасность

- Checkpoint'ы локально, не теряем прогресс
- Ошибки не ломают систему — graceful degradation
- Retry с backoff, не DDoS'им API

---
_Создано: 2026-07-18_
