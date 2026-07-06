**Мантра:** Если не в git — его не существует.

---

## Project Templates

**Plan.md** — шаблон планирования сложных задач  
`templates/Plan.md`

**State Machine** — фазы выполнения скиллов  
`docs/state-machine.md`

**HARNESS.md** — структура проекта для агентов  
Пример: `projects/drawings-to-vor/HARNESS.md`

---

## Drawing OCR / VOR Extraction

**Repo:** `github.com/kimicito/drawings-to-vor` (separate project)
**Local:** `projects/drawings-to-vor/`

**Workflow:**
1. `python3 preprocess.py input.tiff` — tile into 1000×1000
2. `python3 tile_ocr.py --tiles-dir tiles/ --output ocr_result.json` — OCR via Qwen-VL
3. `python3 extract_vor.py --ocr-json ocr_result.json --type piles` — extract VOR (ВОР)

**API:** Alibaba Qwen-VL-OCR (key in `~/.openclaw/workspace/.env`)

---

## WB Tax Calculator (РВБ / Wildberries)

**Skill:** `skills/wb-tax-calculator/`
**Docs:** `skills/wb-tax-calculator/SKILL.md`
**Script:** `skills/wb-tax-calculator/calculator.py`
**Tests:** `skills/wb-tax-calculator/tests/`

**Input files:**
1. Реестр еженедельных операций (Excel/CSV)
2. Детализация отчётов (Excel/CSV)
3. Уведомления о выкупе (Excel/CSV, optional)
4. Доп. расходы из Аналитики (optional)

**Run:**
```bash
python skills/wb-tax-calculator/calculator.py --registry реестр.xlsx --details детализация.xlsx
```

**Tests:**
```bash
cd skills/wb-tax-calculator && python3 tests/test_calculator.py
```

---

## Ozon Tax Calculator (ООО Интернет Решения)

**Skill:** `skills/ozon-tax-calculator/`
**Docs:** `skills/ozon-tax-calculator/SKILL.md`
**Script:** `skills/ozon-tax-calculator/calculator.py`

**Input files:**
1. Отчёт о реализации (Excel/CSV)
2. Отчёт о взаиморасчётах (Excel/CSV)

**Run:**
```bash
python skills/ozon-tax-calculator/calculator.py --realization отчёт_реализации.xlsx --mutual_settlement отчёт_взаиморасчётов.xlsx
```

---

## Git Notes

- **Main repo:** `github.com/kimicito/openclaw-workspace.git` (branch: `master`, remote: `workspace`)
- **Drawing repo:** `github.com/kimicito/drawings-to-vor.git` (branch: `master`, remote: `origin`)
- **Push main:** `git push workspace master`
- **Push drawing:** `cd projects/drawings-to-vor && git push origin master`

---

## Ozon Tax Calculator (ООО «Интернет Решения»)

**Skill:** `workspace/skills/ozon-tax-calculator/`
**Запуск:** Пользователь говорит «Рассчитай налог Ozon»

**Что нужно запросить:**
1. Отчёт о реализации (Excel/CSV) — столбцы: «Возвращено на сумму, руб.», «Выплаты по механикам лояльности партнёров, руб.»
2. Отчёт о взаиморасчётах (Excel/CSV) — столбец: «Суммы дебиторской задолженности»

**Алгоритм:**
- Возвраты = Σ(«Возвращено на сумму») + Σ(«Выплаты по механикам лояльности»)
- Услуги = Σ строк «Отчёт о реализации», «Акт выполненных работ», «Отчёт о перевыставлении услуг», «Акт об оказанных услугах» из взаиморасчётов
- В ЛКН АУСН: Приход = Услуги + Возвраты, Возврат прихода = Возвраты, Расход = Услуги

**Команда:**
```bash
python skills/ozon-tax-calculator/calculator.py --realization отчет.xlsx --mutual взаиморасчеты.xlsx
```

---

## WB Tax Calculator (РВБ / Wildberries)

**Skill:** `workspace/skills/wb-tax-calculator/`
**Запуск:** Пользователь говорит «Рассчитай налог РВБ»

**Что нужно запросить:**
1. Реестр еженедельных операций (Excel/CSV) — столбцы: Тип отчета, Продажа, Итого к оплате
2. Детализация отчётов (Excel/CSV) — столбцы: Тип документа, Вайлдберриз реализовал Товар (Пр)
3. Уведомления о выкупе (Excel/CSV, опционально) — столбец: Сумма
4. Доп. расходы (потери/подмены/дефекты) из Аналитики → Доходы и расходы

**Алгоритм:**
- Комиссия (Основной) = Σ(Продажа) − Σ(Итого к оплате)
- Комиссия (Выкупы) = Сумма Уведомления − Сумма в реестре
- Итого комиссия = Основной + Выкупы + Доп. расходы
- Возвраты = Σ из детализации (фильтр по «возврат»)
- ЛКН АУСН: взаимозачёт на сумму комиссии, возвраты отдельно

**Команда:**
```bash
python skills/wb-tax-calculator/calculator.py --registry реестр.xlsx --details детализация.xlsx [--purchases уведомления.xlsx --losses 9104.28]
```
