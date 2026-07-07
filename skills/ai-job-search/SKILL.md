---
name: ai-job-search
---
# AI Job Search (Russian Market)

AI-powered job application framework for the Russian market, built on Kimi/OpenClaw. Searches hh.ru, evaluates job fit, tailors CVs, writes cover letters, and prepares for interviews.

## Workflow

```
/setup → /scrape → /apply <url>
```

| Command | Description |
|---------|-------------|
| `/setup` | Fill candidate profile (read `references/candidate-profile.md`) |
| `/scrape` | Search hh.ru for jobs matching profile (read `references/hh-scraper.md`) |
| `/apply <url>` | Evaluate fit, draft CV + cover letter, review (read `references/job-evaluation.md`, `references/cv-templates.md`, `references/cover-letter-templates.md`) |

## Candidate Profile

Store candidate profile in `memory/candidate-profile.md`. This file is read by all commands. See `references/candidate-profile.md` for the template structure.

## Job Search (hh.ru)

API hh.ru заблокирован для многих IP. Используй альтернативные методы:

### Метод 1: kimi_search (рекомендуется)
```
kimi_search: "site:hh.ru [query] вакансия"
```

### Метод 2: web_fetch
```
web_fetch: https://hh.ru/search/vacancy?text=[query]
```

### Метод 3: browser
```
browser: open https://hh.ru/search/vacancy?text=[query]
browser: snapshot
```

### Скрипт (fallback)
Если API доступен, используй `scripts/hh_scraper.py`:
```bash
python scripts/hh_scraper.py --query "Python разработчик" --area 1 --limit 20
```

Используй `scripts/hh_scraper.py` как fallback если API доступен. Основной метод — `kimi_search` или `browser`.

## Job Evaluation

Read `references/job-evaluation.md` for the evaluation framework. Score each job on:
- Skills match (0-10)
- Experience match (0-10)
- Culture fit (0-10)
- Career growth (0-10)
- Compensation alignment (0-10)

Total score: weighted average. Present top 5 matches.

## CV Tailoring

Read `references/cv-templates.md` for CV templates. Use markdown format (simpler than LaTeX for OpenClaw). Tailor the CV by:
1. Matching keywords from job description
2. Highlighting relevant experience
3. Quantifying achievements
4. Adapting skills section

## Cover Letter

Read `references/cover-letter-templates.md` for templates. Structure:
1. Hook (why this company/role)
2. Proof (relevant experience with metrics)
3. Fit (why you + this role = success)
4. Forward-looking closing

## Interview Prep

Read `references/interview-prep.md` for interview preparation. Generate:
- 5 likely questions with model answers
- 3 questions to ask the interviewer
- Talking points for salary negotiation

## Token Efficiency

- Never re-read files already in context
- Pass draft content inline to subagents
- Run verification checklist once at the end
- Use subagents for drafter-reviewer pipeline
