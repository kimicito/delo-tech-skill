# Technical Drawing OCR Skill

Extract text and tables from construction drawings (PDF, PNG, JPG) for VOR (Volume Statement) preparation.

## Overview

This skill addresses the limitations of standard OCR for technical construction drawings:
- **Large format sheets** (A0, A1, A3)
- **Mixed content** (text, tables, diagrams, dimensions)
- **Technical Russian language** with abbreviations
- **Tabular data** (specifications, material lists)
- **Scale-dependent calculations**

## Installation

```bash
# System dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-rus \
    tesseract-ocr-eng \
    poppler-utils \
    python3-pip \
    python3-venv

# Python dependencies
python3 -m venv ~/.venv/drawing-ocr
source ~/.venv/drawing-ocr/bin/activate
pip install \
    pdfplumber \
    opencv-python \
    pillow \
    numpy \
    pandas \
    openpyxl
```

## Commands

### 1. Extract Text Layer from PDF (Level 1)

```bash
# Check if PDF has text layer
drawing-ocr text-layer "drawing.pdf"

# Extract text from all pages
for page in {1..10}; do
    pdftotext -f $page -l $page -layout "drawing.pdf" "page-${page}.txt"
done
```

### 2. Extract Tables from PDF (Level 2)

```bash
# Extract tables using pdfplumber
drawing-ocr tables "drawing.pdf" --pages 5,6 --output "tables.json"

# Extract specifications page
drawing-ocr tables "drawing.pdf" --pages 6 --output "specs.xlsx"
```

### 3. OCR Image Processing (Level 3)

```bash
# Convert PDF to high-res image
drawing-ocr pdf-to-image "drawing.pdf" --dpi 400 --output "pages/"

# OCR with preprocessing
drawing-ocr ocr "page-6.png" --lang rus+eng --preprocess --output "page-6.txt"

# OCR specific region (for tables)
drawing-ocr ocr "page-6.png" --region "100,200,800,600" --output "table.txt"
```

### 4. Full Pipeline

```bash
# Complete extraction pipeline
drawing-ocr pipeline \
    --input "KJ6.pdf" \
    --output "extraction/" \
    --pages all \
    --method auto

# Output structure:
# extraction/
#   text-layer/      # Text from PDF layer
#   tables/          # Extracted tables (CSV/XLSX)
#   ocr/             # OCR results for image pages
#   combined/        # Merged results
```

## Python API

```python
from drawing_ocr import DrawingProcessor

# Initialize processor
processor = DrawingProcessor(
    language='rus+eng',
    dpi=400,
    table_extraction=True
)

# Process PDF
result = processor.process_pdf(
    'drawing.pdf',
    pages='all',  # or [5, 6] for specific pages
    output_dir='output/'
)

# Access results
for page_num, page_data in result.items():
    print(f"Page {page_num}:")
    print(f"  Text: {page_data['text'][:200]}...")
    print(f"  Tables: {len(page_data['tables'])}")
    for table in page_data['tables']:
        print(f"    Table: {table.to_dict()}")
```

## Image Preprocessing Pipeline

```python
import cv2
import numpy as np
from PIL import Image

def preprocess_for_ocr(image_path, output_path):
    """Preprocess image for optimal OCR on technical drawings."""
    
    # Read image
    img = cv2.imread(image_path)
    
    # 1. Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 2. Denoise
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    
    # 3. Increase contrast (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)
    
    # 4. Deskew (if needed)
    # Detect skew angle and rotate
    
    # 5. Binarization (Otsu)
    _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # 6. Save
    cv2.imwrite(output_path, binary)
    
    return output_path
```

## Table Extraction Strategy

For technical drawings with embedded tables (specifications):

```python
import pdfplumber

def extract_technical_tables(pdf_path, page_numbers):
    """Extract tables from technical drawing pages."""
    tables = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num in page_numbers:
            page = pdf.pages[page_num - 1]  # 0-indexed
            
            # Try multiple table extraction strategies
            page_tables = page.extract_tables(
                table_settings={
                    "vertical_strategy": "lines",
                    "horizontal_strategy": "lines",
                    "intersection_x_tolerance": 10,
                    "intersection_y_tolerance": 10,
                }
            )
            
            if not page_tables:
                # Fallback: text-based extraction
                page_tables = page.extract_tables(
                    table_settings={
                        "vertical_strategy": "text",
                        "horizontal_strategy": "text",
                    }
                )
            
            tables.extend({
                'page': page_num,
                'table': table,
                'method': 'lines' if page_tables else 'text'
            } for table in page_tables)
    
    return tables
```

## Technical Russian Dictionary

Common terms in construction drawings:

```python
TECHNICAL_TERMS = {
    'арматура': 'reinforcement',
    'бетон': 'concrete',
    'плита': 'plate/slab',
    'фундамент': 'foundation',
    'шов': 'joint/seam',
    'закладная': 'embedded part',
    'опалубка': 'formwork',
    'гидроизоляция': 'waterproofing',
    'пенополистирол': 'polystyrene foam',
    'герметик': 'sealant',
    'плёнка': 'film',
    'песок': 'sand',
    'щебень': 'crushed stone',
    'цемент': 'cement',
    'подготовка': 'preparation',
    'засыпка': 'backfill',
    'утеплитель': 'insulation',
    'грунт': 'soil/primer',
    'эмал': 'enamel',
    'краск': 'paint',
    'покрытие': 'coating',
    'ППС': 'EPS (Expanded Polystyrene)',
    'ПЭ': 'PE (Polyethylene)',
    'ПВХ': 'PVC',
    'А500С': 'A500C (rebar grade)',
    'А240': 'A240 (rebar grade)',
    'В25': 'B25 (concrete grade)',
    'W6': 'W6 (water resistance)',
    'F150': 'F150 (frost resistance)',
    'МН': 'MN (embedded part series)',
    'КЖ': 'KZh (reinforced concrete)',
    'ОВ': 'OV (heating/ventilation)',
    'ВК': 'VK (water supply/sewerage)',
    'ЭО': 'EO (electrical equipment)',
    'СС': 'SS (weak current)',
    'ТХ': 'TH (technological)',
    'КМ': 'KM (metal structures)',
    'ТМ': 'TM (technological equipment)',
    'ППР': 'PPR (work execution plan)',
    'ПГС': 'PGS (sand-gravel mix)',
    'ЩПС': 'ShchPS (crushed stone-sand mix)',
    'ГОСТ': 'GOST (state standard)',
    'СП': 'SP (set of rules)',
    'ТУ': 'TU (technical specifications)',
    'СНиП': 'SNiP (construction norms)',
}
```

## Configuration

```json
{
  "drawing_ocr": {
    "language": "rus+eng",
    "dpi": 400,
    "preprocessing": {
      "denoise": true,
      "contrast_enhancement": true,
      "deskew": true,
      "binarize": true
    },
    "table_extraction": {
      "method": "auto",
      "fallback_to_text": true,
      "merge_broken_tables": true
    },
    "output": {
      "format": "json",
      "include_images": false,
      "confidence_threshold": 0.7
    }
  }
}
```

## Integration with Drawings-to-VOR Pipeline

```bash
# Step 1: Extract all data from drawings
drawing-ocr pipeline --input "KJ6.pdf" --output "extraction/"

# Step 2: Convert to VOR format
python3 scripts/extraction_to_vor.py \
    --input "extraction/" \
    --output "ВОР.xlsx" \
    --template "templates/ВОР_шаблон.xlsx"

# Step 3: Validate
python3 scripts/eval_vor.py --vor "ВОР.xlsx" --example "data/vor_pro_example.xlsx"
```

## Known Limitations

1. **Handwritten annotations**: OCR accuracy drops significantly
2. **Very small text** (< 6pt): May require 600+ DPI
3. **Complex diagrams**: Table extraction may fail on non-tabular layouts
4. **Stamps and signatures**: Often detected as noise

## Troubleshooting

### Problem: Tables not extracted
```bash
# Solution 1: Increase DPI
drawing-ocr pdf-to-image --dpi 600 input.pdf

# Solution 2: Manual region OCR
drawing-ocr ocr page.png --region "x,y,w,h" --table-mode

# Solution 3: Use pdfplumber directly
python3 -c "import pdfplumber; pdfplumber.open('input.pdf').pages[5].extract_tables()"
```

### Problem: Russian text not recognized
```bash
# Check language packs
ls /usr/share/tesseract-ocr/4.00/tessdata/

# Install Russian
sudo apt-get install tesseract-ocr-rus

# Test
tesseract page.png output -l rus+eng
```

## See Also

- `drawings-to-vor` skill: Converting drawings to VOR
- `smeta` skill: Construction estimate preparation
- `pdfplumber` docs: https://github.com/jsvine/pdfplumber
- Tesseract docs: https://github.com/tesseract-ocr/tesseract
