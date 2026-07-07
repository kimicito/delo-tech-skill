# Self-Improving HOT Memory

## Skill Selection Rules (Confirmed)

- When user mentions "вакансия", "работа", "hh", "резюме", "CV" → ALWAYS load ai-job-search skill
- When user mentions "проект", "задача", "запомни", "свяжи", "кто делает" → ALWAYS load ontology skill
- When user mentions "найди", "поиск", "google", "новости" → Check multi-search-engine skill
- When user mentions "deploy", "server", "docker", "VPS" → Check node-connect, docker skills
- When user mentions "PDF", "document", "word", "excel" → Load word-docx, excel-xlsx, nano-pdf
- When user asks about "skill install", "clawhub", "установи скилл" → Load skill-vetter first for security check
- When user mentions "youtube", "видео", "transcript" → Load youtube-watcher
- All changes MUST be committed to git and pushed to GitHub

## User Preferences

- User prefers Russian language for explanations
- User wants concise answers, not verbose
- User prefers all work committed to git (workspace master branch)
- User runs OpenClaw on Linux server (Asia/Shanghai timezone)
