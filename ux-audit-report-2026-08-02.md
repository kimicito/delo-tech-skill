# UX/UI Audit Report — ai-nontechnical-course
**Date:** 2026-08-02
**URL:** https://kimicito.github.io/ai-nontechnical-course/
**Languages checked:** RU, EN (FR, ZH partially)

---

## 🔴 CRITICAL ISSUES (Broken Links / 404)

### RU — index.html
| Level | Current Link | Should Be |
|-------|-------------|-----------|
| 7 (Этика) | `catalog.html#level9` | `catalog.html#level7` |
| 8 (Закупки) | `catalog.html#level9` | `catalog.html#level8` |
| 11 (PR) | `catalog.html#level18` | `catalog.html#level11` |
| 12 (Качество) | `catalog.html#level18` | `catalog.html#level12` |
| 13 (ТОиР) | `catalog.html#level18` | `catalog.html#level13` |
| 14 (Логистика) | `catalog.html#level18` | `catalog.html#level14` |
| 15 (Продажи) | `catalog.html#level18` | `catalog.html#level15` |
| 16 (Юристы) | `catalog.html#level18` | `catalog.html#level16` |
| 17 (Комплаенс) | `catalog.html#level18` | `catalog.html#level17` |

### RU — catalog.html (Wrong folder paths)
| Level | Lesson | Current Path | Should Be |
|-------|--------|-------------|-----------|
| 8 (Закупки) | 8.1 | `lessons/09-1-on-prem/` | `lessons/08-1-on-prem/` |
| 8 (Закупки) | 8.2 | `lessons/09-2-cloud/` | `lessons/08-2-cloud/` |
| 8 (Закупки) | 8.3 | `lessons/09-3-hybrid/` | `lessons/08-3-hybrid/` |
| 12 (Качество) | 12.1 | `lessons/09-1-on-prem/` | `lessons/12-1-on-prem/` |
| 12 (Качество) | 12.2 | `lessons/09-2-cloud/` | `lessons/12-2-cloud/` |
| 12 (Качество) | 12.3 | `lessons/09-3-hybrid/` | `lessons/12-3-hybrid/` |
| 14 (Логистика) | 14.1 | `lessons/13-1-on-prem/` | `lessons/14-1-on-prem/` |
| 14 (Логистика) | 14.2 | `lessons/13-2-cloud/` | `lessons/14-2-cloud/` |
| 14 (Логистика) | 14.3 | `lessons/13-3-hybrid/` | `lessons/14-3-hybrid/` |

### EN — catalog.html (Wrong folder paths)
| Level | Lesson | Current Path | Should Be |
|-------|--------|-------------|-----------|
| 11 (Quality) | 11.1 | `lessons/08-1-on-prem/` | `lessons/11-1-on-prem/` |
| 11 (Quality) | 11.2 | `lessons/08-2-cloud/` | `lessons/11-2-cloud/` |
| 11 (Quality) | 11.3 | `lessons/08-3-hybrid/` | `lessons/11-3-hybrid/` |
| 12 (MRO) | 12.1 | `lessons/11-1-on-prem/` | `lessons/12-1-on-prem/` |
| 12 (MRO) | 12.2 | `lessons/11-2-cloud/` | `lessons/12-2-cloud/` |
| 12 (MRO) | 12.3 | `lessons/11-3-hybrid/` | `lessons/12-3-hybrid/` |
| 13 (Logistics) | 13.1 | `lessons/12-1-on-prem/` | `lessons/13-1-on-prem/` |
| 13 (Logistics) | 13.2 | `lessons/12-2-cloud/` | `lessons/13-2-cloud/` |
| 13 (Logistics) | 13.3 | `lessons/12-3-hybrid/` | `lessons/13-3-hybrid/` |

---

## 🟡 MAJOR ISSUES (Wrong Lesson Numbers / Duplicates)

### RU — catalog.html (Lesson numbers all show "18.x")
- **Levels 9-18**: All lesson numbers display as "18.1", "18.2", "18.3", "18.4", "18.5" instead of correct numbers
- Example: Level 9 (Стройка) shows "18.1", "18.2", "18.3", "18.4", "18.5" instead of "9.1", "9.2", "9.3", "9.4", "9.5"
- Same for Levels 10, 11, 12, 13, 14, 15, 16, 17, 18

### EN — index.html (Duplicate Level 8)
- **Two Level 8 cards**: "AI for Procurement" and "AI for Construction" both link to `catalog.html#level8`
- **Missing Level 18**: "AI for HR" shown as Level 17, no Level 18 card exists

### EN — catalog.html (Duplicate Level 8 heading)
- Two Level 8 sections: "AI for Procurement" and "AI for Construction"
- Construction should be Level 9

---

## 🟢 MINOR ISSUES

### Consistency
- **RU index**: "11 специализаций" but only 10 shown in audience grid (missing Audit)
- **EN index**: Missing "Audit" role in audience grid

### Content
- **FR/ZH**: Not fully verified (need browser check)

---

## 📋 Fix Priority

### Priority 1 — Fix immediately (404s)
1. Fix RU index.html level links (7→#level7, 8→#level8, 11-17→correct anchors)
2. Fix RU catalog.html folder paths (08, 12, 14 levels)
3. Fix EN catalog.html folder paths (11, 12, 13 levels)
4. Fix EN index.html duplicate Level 8 / missing Level 18

### Priority 2 — Fix soon (wrong numbers)
5. Fix RU catalog.html lesson numbers (18.x → correct numbers for all levels)
6. Verify FR/ZH catalogs have same fixes applied

### Priority 3 — Polish
7. Add missing "Audit" role to audience grids
8. Run full 404 check on all language versions
