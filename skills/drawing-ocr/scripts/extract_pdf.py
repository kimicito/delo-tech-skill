#!/usr/bin/env python3
"""
Extract text from PDF using multiple methods (fallback pipeline).
Level 1: Text layer (pdftotext)
Level 2: pdfplumber tables and text
Level 3: OCR (Tesseract) on rendered pages
"""

import sys
import subprocess
import json
import argparse
from pathlib import Path
import tempfile
import shutil


def check_command(cmd):
    """Check if command is available."""
    return shutil.which(cmd) is not None


def extract_text_layer(pdf_path, output_dir, pages=None):
    """Extract text layer using pdftotext."""
    if not check_command('pdftotext'):
        print("Warning: pdftotext not found, skipping text layer extraction")
        return None
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    # Get number of pages
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
    except:
        total_pages = 10  # Default guess
    
    page_range = pages if pages else range(1, total_pages + 1)
    
    for page_num in page_range:
        output_file = output_dir / f"page-{page_num}.txt"
        
        cmd = ['pdftotext', '-f', str(page_num), '-l', str(page_num), '-layout', str(pdf_path), str(output_file)]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            
            if output_file.exists():
                text = output_file.read_text(encoding='utf-8', errors='ignore')
                if text.strip():
                    results[page_num] = {
                        'method': 'pdftotext',
                        'text': text,
                        'file': str(output_file)
                    }
        except Exception as e:
            print(f"Error extracting page {page_num}: {e}")
    
    return results


def extract_tables_pdfplumber(pdf_path, pages=None):
    """Extract tables using pdfplumber."""
    try:
        import pdfplumber
    except ImportError:
        print("Warning: pdfplumber not installed, skipping table extraction")
        return None
    
    results = {}
    
    with pdfplumber.open(pdf_path) as pdf:
        page_range = pages if pages else range(1, len(pdf.pages) + 1)
        
        for page_num in page_range:
            page_idx = page_num - 1
            if page_idx >= len(pdf.pages):
                continue
            
            page = pdf.pages[page_idx]
            
            # Try text extraction first
            text = page.extract_text()
            
            # Try table extraction with different strategies
            tables = []
            
            # Strategy 1: Lines-based
            try:
                line_tables = page.extract_tables({
                    "vertical_strategy": "lines",
                    "horizontal_strategy": "lines",
                    "intersection_x_tolerance": 10,
                    "intersection_y_tolerance": 10,
                })
                if line_tables:
                    tables.extend(line_tables)
            except:
                pass
            
            # Strategy 2: Text-based (fallback)
            if not tables:
                try:
                    text_tables = page.extract_tables({
                        "vertical_strategy": "text",
                        "horizontal_strategy": "text",
                    })
                    if text_tables:
                        tables.extend(text_tables)
                except:
                    pass
            
            if text or tables:
                results[page_num] = {
                    'text': text,
                    'tables': tables,
                    'method': 'pdfplumber'
                }
    
    return results


def extract_ocr(pdf_path, output_dir, pages=None, dpi=400, lang='rus+eng'):
    """Extract text using OCR on rendered pages."""
    if not check_command('pdftoppm') or not check_command('tesseract'):
        print("Warning: pdftoppm or tesseract not found, skipping OCR")
        return None
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Convert PDF to images
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Get page count
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
        except:
            total_pages = 10
        
        page_range = pages if pages else range(1, total_pages + 1)
        
        # Convert specific pages
        for page_num in page_range:
            cmd = [
                'pdftoppm', '-png', '-r', str(dpi),
                '-f', str(page_num), '-l', str(page_num),
                str(pdf_path), str(tmpdir / f'page')
            ]
            
            try:
                subprocess.run(cmd, check=True, capture_output=True)
            except Exception as e:
                print(f"Error converting page {page_num}: {e}")
                continue
        
        # Find generated images
        images = sorted(tmpdir.glob('*.png'))
        
        results = {}
        for i, img_path in enumerate(images, 1):
            page_num = page_range[i-1] if i <= len(page_range) else i
            
            output_file = output_dir / f"page-{page_num}-ocr.txt"
            
            try:
                subprocess.run([
                    'tesseract', str(img_path), str(output_file.with_suffix('')),
                    '-l', lang, '--psm', '6'  # Assume uniform block of text
                ], check=True, capture_output=True)
                
                if output_file.exists():
                    text = output_file.read_text(encoding='utf-8', errors='ignore')
                    results[page_num] = {
                        'method': 'tesseract-ocr',
                        'text': text,
                        'file': str(output_file)
                    }
            except Exception as e:
                print(f"Error OCR on page {page_num}: {e}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description='Extract text from PDF using multiple methods')
    parser.add_argument('pdf', help='Input PDF file')
    parser.add_argument('--output', '-o', default='extraction', help='Output directory')
    parser.add_argument('--pages', '-p', type=int, nargs='+', help='Specific pages to process')
    parser.add_argument('--method', '-m', choices=['text', 'tables', 'ocr', 'all'], default='all',
                        help='Extraction method')
    parser.add_argument('--dpi', type=int, default=400, help='DPI for OCR (default: 400)')
    parser.add_argument('--lang', '-l', default='rus+eng', help='OCR language (default: rus+eng)')
    
    args = parser.parse_args()
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    all_results = {}
    
    # Level 1: Text layer
    if args.method in ['text', 'all']:
        print("Level 1: Extracting text layer...")
        text_results = extract_text_layer(args.pdf, output_dir / 'text-layer', args.pages)
        if text_results:
            all_results['text_layer'] = text_results
            print(f"  Extracted {len(text_results)} pages with text layer")
    
    # Level 2: Tables and structured text
    if args.method in ['tables', 'all']:
        print("Level 2: Extracting tables with pdfplumber...")
        table_results = extract_tables_pdfplumber(args.pdf, args.pages)
        if table_results:
            all_results['tables'] = table_results
            print(f"  Extracted {len(table_results)} pages with tables")
            
            # Save tables to files
            for page_num, data in table_results.items():
                if data.get('tables'):
                    tables_file = output_dir / f'page-{page_num}-tables.json'
                    with open(tables_file, 'w', encoding='utf-8') as f:
                        json.dump(data['tables'], f, ensure_ascii=False, indent=2)
    
    # Level 3: OCR
    if args.method in ['ocr', 'all']:
        print("Level 3: OCR processing...")
        ocr_results = extract_ocr(args.pdf, output_dir / 'ocr', args.pages, args.dpi, args.lang)
        if ocr_results:
            all_results['ocr'] = ocr_results
            print(f"  OCR processed {len(ocr_results)} pages")
    
    # Save combined results
    summary_file = output_dir / 'extraction-summary.json'
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\nResults saved to: {output_dir}")
    print(f"Summary: {summary_file}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
