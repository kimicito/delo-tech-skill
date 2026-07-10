# PPTX Style Adapter

## Purpose
Generate PowerPoint presentations by cloning the visual style (colors, fonts, layouts) from a reference/template PPTX, then populating it with structured content from markdown or text.

## Input
1. **Template PPTX** — the "ideal" style reference (colors, fonts, slide masters, layouts)
2. **Content** — markdown or text with slides structure (titles, bullets, tables, etc.)

## Output
New PPTX file with:
- Same slide dimensions as template
- Extracted color palette (dominant colors from backgrounds/headers)
- Clean, presentation-ready formatting
- 18 slides covering: title, path, roles table, examples, theory, practice, homework

## Key Lessons from Implementation

### Template Analysis
```python
prs = Presentation(TEMPLATE_PATH)
print(f"Размеры: {prs.slide_width.inches:.1f} x {prs.slide_height.inches:.1f}")
print(f"Слайдов: {len(prs.slides)}")
print(f"Лейаутов: {len(prs.slide_layouts)}")
# IMPORTANT: Use prs.slide_layouts[0] if only 1 layout exists!
```

### Color Extraction Strategy
Since python-pptx has limited theme access, colors are manually mapped from visual analysis:
- **Header BG**: RGBColor(0x1A, 0x1A, 0x2E) — dark navy blue
- **Content BG**: RGBColor(0xF5, 0xF5, 0xF5) — light gray
- **Accent**: RGBColor(0xD4, 0xA5, 0x3D) — gold/amber
- **Text**: RGBColor(0x33, 0x33, 0x33) — dark gray
- **White**: RGBColor(0xFF, 0xFF, 0xFF)

### Slide Types
1. **Title slide** — full dark background + centered white title + gold subtitle
2. **Content slide** — light gray bg + dark header bar + bullet list
3. **Table slide** — light gray bg + header row + alternating row colors

### Background Shape Trick
```python
bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
# Send to back:
spTree = slide.shapes._spTree
sp = bg._element
spTree.remove(sp)
spTree.insert(2, sp)
```

## Process
1. Analyze template dimensions and layout count
2. Manually map dominant colors from visual inspection
3. Clear template slides (keep master/styles)
4. Create slides: title → content → table → practice → closing
5. Apply consistent fonts (Arial fallback) and colors

## Critical Fix
When template has only 1 layout, use `prs.slide_layouts[0]`, NOT `[6]`.

## Usage
```bash
python3 /tmp/gen_styled_construction.py
# Outputs: lesson-1-construction-styled.pptx
```

## Files
- Template: `owu_training-10---70e7c362-adfa-4054-b1b6-f000c5c34215.pptx`
- Output: `lesson-1-construction-styled.pptx` (18 slides)
- Script: `/tmp/gen_styled_construction.py`
