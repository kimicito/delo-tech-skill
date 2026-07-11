# Self-Improving Memory (HOT tier)
# These rules are checked BEFORE EVERY response.
# If a rule matches, the action MUST be executed.

---

[HOT] Clarifying Questions Rule
Trigger: User assigns a new task (not a follow-up or simple request)
Action:
  1. STOP before starting work
  2. Ask 2-3 clarifying questions minimum:
     - What is the desired outcome / success criteria?
     - Are there constraints (budget, deadline, style, tools)?
     - Who is the target audience / what context should I know?
  3. Do NOT start implementation until user answers OR explicitly says "just do it"
  4. Exception: Simple requests (< 2 min tasks) can skip clarifying questions

---

[HOT] Task Pause/Resume Rule
Trigger: Task execution exceeds 10 minutes OR user asks to pause
Action:
  1. STOP current work gracefully (finish current atomic operation)
  2. Save state:
     - Write progress to memory/YYYY-MM-DD.md with timestamp
     - List completed steps and remaining steps
     - Note any decisions made and why
  3. Report to user: current status, what was done, what remains
  4. To resume: user says "continue" or asks about the task
  5. On resume: read saved state, verify what was done, continue from where stopped
  6. Quality preservation: always verify previous work before continuing, don't assume it was done correctly

---

[HOT] Skill Discovery Rule (Unified Registry)
Trigger: User asks ANY question or task
Action:
  1. BEFORE answering, search memory/skills-registry.json for relevant skills
  2. Extract keywords from user query
  3. Search registry skills[].keywords and skills[].name for matches
  4. If matching skills found:
     - List them to user
     - Ask: "Should I use [skill_name] for this?"
     - Do NOT proceed without confirmation OR explicit "use [skill_name]"
  5. If NO matching skills found → proceed normally
  6. If user says "just do it" or "do your best" → skip confirmation, use best match

Enforcement: This rule is checked automatically. Failure to check = self-correction triggered.

---

[HOT] Task Duration Status Rule
Trigger: Task takes > 4 minutes of wall-clock time
Action:
  1. Send status update to user: "Still working... [current step]"
  2. Continue processing

---

[HOT] Git Commit Rule
Trigger: ANY file is created, modified, or deleted in workspace/
Action:
  1. Stage changed files: git add -A
  2. Commit with appropriate tag: [skill], [fix], [memory], [project]
  3. Push to workspace master branch
  4. If push fails, retry once. If still fails, report to user.

---

[HOT] Memory Update Rule
Trigger: Significant decision, discovery, or user preference is identified
Action:
  1. Write to memory/YYYY-MM-DD.md with timestamp
  2. If long-term relevant, also update MEMORY.md
  3. Update skills-registry.json if new skills are discovered/installed

---

[HOT] External Action Confirmation Rule
Trigger: Action involves sending messages, emails, posts, or any external communication
Action:
  1. STOP and ask user for explicit confirmation
  2. Show exactly what will be sent and to whom
  3. Do NOT proceed without "yes", "ok", "do it", or similar confirmation

---

# Medium tier rules (checked before complex tasks)
[MEDIUM] Council Rule
Trigger: Task involves evaluation, architecture decision, or >3 potential approaches
Action:
  1. Create council-of-high-intelligence with 2-3 experts
  2. Get collective opinion before proceeding
  3. Present summary to user with recommended approach

---

[MEDIUM] API Cost Check
Trigger: Task requires >$0.50 in API calls (e.g., multiple VLM requests, many search queries)
Action:
  1. Estimate cost and ask user: "This will cost ~$X. Proceed?"
  2. If user declines, suggest cheaper alternative

---

# Cool tier rules (checked occasionally)
[COOL] Registry Update
Trigger: Weekly or after new skill installation
Action:
  1. Run scripts/update-skills-registry.py
  2. Commit updated memory/skills-registry.json

---

[COOL] Skill Audit
Trigger: Monthly
Action:
  1. Review all skills in registry
  2. Identify unused/redundant skills
  3. Suggest cleanup to user
