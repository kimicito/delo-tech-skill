# Wiki Log

Append-only хронология изменений в базе знаний.

## [2026-06-28] setup | Wiki initialization
- Created vault structure: 00-Inbox, 01-Projects, 02-Areas, 03-Resources, 04-Archive
- Created schema: [[KIMI.md]]
- Created index and log

## [2026-06-28] ingest | WEF AI Playbook for Financial Services
- Source: https://www.weforum.org/publications/the-ai-playbook-for-financial-services/
- Type: Report (PDF)
- Summary: [[WEF AI Playbook 2026]]
- Entities created: [[Agentic AI]], [[KBTG]], [[AI Governance]]
- Key insights: 4 findings, Framework for Transformational AI, Agentic AI spectrum

## [2026-06-28] query | Презентация для топ-менеджмента
- Question: "Подготовь 7-слайдовую презентацию по WEF AI Playbook"
- Output: [[AI Playbook Presentation]] (PPTX + MD)
- Filed to wiki: Yes

## [2026-06-28] ingest | Gist — LLM Knowledge Base Pattern
- Source: https://gist.github.com/kimicito/6f33a4457b8c2c9767e960c692e6d7a3
- Type: Pattern / Architecture
- Summary: Паттерн для LLM-управляемой базы знаний (не RAG)
- Impact: Created [[KIMI.md]] schema for this wiki

## [2026-06-29] ingest | Отчёт по AI в финансах
- Source: raw/Отчет по AI в финансах.md
- Type: Report (Markdown)
- Summary: [[Отчет по AI в финансах]]
- Entities created: [[Сбер]], [[Т-Банк]], [[Predictive AI]], [[Generative AI]], [[Multimodal AI]]
- Key insights: 78 % банков с ML в production, средний ROI 14 мес, топ-3 причины провалов
- Updated: [[KBTG]] (добавлена ссылка на отчёт)

## [2026-06-29] ingest | Нормативные документы Минстроя (сметы)
- Source: Минстрой России (pravo.gov.ru, fgiscs.minstroyrf.ru)
- Type: Normative documents
- Documents added:
  - [[Приказ Минстроя 421-пр]] — Методика определения сметной стоимости (ред. 30.01.2026)
  - [[Приказ Минстроя 812-пр]] — Методика НР (накладных расходов)
  - [[Приказ Минстроя 774-пр]] — Методика СП (сметной прибыли)
  - [[Приказ Минстроя 571-пр]] — Методика применения сметных норм
  - [[ФГИС ЦС]] — Федеральная система ценообразования
  - [[Индексы ФГИС ЦС]] — Индексы по статьям (INDEX_ZP, INDEX_MACH, INDEX_MAT)
- Note: Текущие редакции, следить за обновлениями

---

*Format: `## [YYYY-MM-DD] operation | description`*
