# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## Skill Priority — CRITICAL

**Always use workspace/skills/ first.** OpenClaw resolves skills in this order:

1. `~/.openclaw/workspace/skills/` ← **ACTIVE — use these**
2. `~/.openclaw/skills/` ← global fallback (do not edit here)
3. `/usr/lib/node_modules/openclaw/skills/` ← system builtins

### Active Workspace Skills (authoritative)

| Skill | Path | Status |
|-------|------|--------|
| **price-comparison** | `workspace/skills/price-comparison/` | v3.0 — matrices, analogs, eval |
| **smeta** | `workspace/skills/smeta/` | БИМ-methodology, FER-2020 |
| **soulsaying** | `workspace/skills/soulsaying/` | Conversation mode |
| email-objection-handler | `workspace/skills/email-objection-handler/` | ⚪ standby |
| notion | `workspace/skills/notion/` | ⚪ standby |

### Rule
- **Never** use `~/.openclaw/skills/smeta.skill` (old ZIP archive — renamed to `.old`)
- **Always** check `workspace/skills/` before falling back to global
- If a skill exists in workspace — that is the canonical version
- Commit skill changes to Git immediately after editing

### Cleanup done
- `~/.openclaw/skills/smeta.skill` → `smeta.skill.old` (archived)
- `price-comparison` lives **only** in workspace

---

## 🔒 Правило бэкапа — ВСЁ ВАЖНОЕ в GitHub

**Принцип:** Всё, что нарабатываем — skills, проекты, MD-файлы, таблицы, PDF-документы — должно сохраняться в Git (`openclaw-workspace`).

### Что бэкапится (обязательно)

| Категория | Примеры | Статус |
|---|---|---|
| **Skills** | `workspace/skills/price-comparison/`, `smeta/`, `soulsaying/` | ✅ tracked |
| **Projects** | `projects/smeta/`, `botgame/`, `educai8/` | ✅ tracked |
| **Личные** | `personal/company_programs.md`, `internship.md` | ✅ tracked |
| **Рабочие** | `work/задачи_шефа.md` | ✅ tracked |
| **Таблицы** | `*.xlsx` в `personal/` и проектах | ✅ tracked |
| **Документы** | `*.pdf` (ФЕР-20, сметы) в проектах | ✅ tracked |
| **Memory** | `memory/YYYY-MM-DD.md` | ✅ tracked |
| **Bootstrap** | `AGENTS.md`, `SOUL.md`, `TOOLS.md` | ✅ tracked |

### Что НЕ бэкапится (исключения в `.gitignore`)

- `venv/`, `node_modules/`, `__pycache__/` — генерируемое
- `media/inbound/` — входящие медиа
- `*.log`, `*.tmp`, `*.zip` — временное
- `projects/educai8/` — свой git-репозиторий

### Процесс бэкапа

1. **Авто:** cron каждый день в 3:00 AM (`backup.sh`)
2. **Ручной:** `./backup.sh "[тип] описание"`
3. **Проверка:** `git status` — покажет что не в бэкапе

### При создании нового

- Новый skill → `workspace/skills/<name>/` + `git add`
- Новый проект → `projects/<name>/` + `git add`
- Новый MD → `personal/` или `work/` + `git add`
- Важный PDF/XLSX → `git add -f` если в `.gitignore`

**Мантра:** Если не в git — его не существует.
