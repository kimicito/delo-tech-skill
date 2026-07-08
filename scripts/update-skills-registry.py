#!/usr/bin/env python3
"""
update-skills-registry.py — Unified Skills Registry Builder

Scans all SKILL.md files across all skill directories and builds
memory/skills-registry.json — a single index of all available skills.

Usage:
    python3 scripts/update-skills-registry.py

Scans:
    - workspace/skills/
    - ~/.openclaw/kimi-skills/
    - ~/.openclaw/skills/
    - /usr/lib/node_modules/openclaw/skills/
    - ~/.openclaw/extensions/*/skills/
"""

import json
import re
from pathlib import Path


def extract_skill_info(skill_md_path: Path) -> dict:
    """Parse SKILL.md for name, description, keywords."""
    content = skill_md_path.read_text(encoding='utf-8', errors='ignore')
    
    # Try to extract name from frontmatter
    name = None
    desc = None
    
    # --- name: ... ---
    name_match = re.search(r'^---\s*\n.*?name:\s*(.+?)\n', content, re.MULTILINE | re.DOTALL)
    if name_match:
        name = name_match.group(1).strip()
    
    # # Header as fallback
    if not name:
        header_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if header_match:
            name = header_match.group(1).strip()
    
    # Description from frontmatter or first paragraph
    desc_match = re.search(r'description:\s*>?\s*(.+?)(?:\n\w|$)', content, re.DOTALL)
    if desc_match:
        desc = desc_match.group(1).strip().replace('\n', ' ').replace('  ', ' ')[:200]
    
    # Extract keywords from content (first 500 chars for context)
    text = content[:1000].lower()
    keywords = []
    
    # Auto-extract keywords from description and content
    for word in re.findall(r'[а-яa-z]+', text):
        if len(word) > 4 and word not in {'skill', 'skills', 'script', 'python', 'usage', 'install'}:
            keywords.append(word)
    
    # Unique keywords, limit to 20
    keywords = list(dict.fromkeys(keywords))[:20]
    
    return {
        'name': name or skill_md_path.parent.name,
        'description': desc or '(no description)',
        'keywords': keywords,
        'path': str(skill_md_path.parent),
        'skill_md': str(skill_md_path),
    }


def scan_skills_dir(base_path: Path, source: str) -> list:
    """Scan a directory for SKILL.md files."""
    skills = []
    if not base_path.exists():
        return skills
    
    for skill_md in base_path.rglob('SKILL.md'):
        # Skip nested SKILL.md inside node_modules or .git
        if '.git' in str(skill_md) or 'node_modules' in str(skill_md):
            continue
        try:
            info = extract_skill_info(skill_md)
            info['source'] = source
            skills.append(info)
        except Exception as e:
            print(f"  WARN: {skill_md}: {e}")
    
    return skills


def main():
    workspace = Path('/root/.openclaw/workspace')
    registry = {
        'meta': {
            'version': '1.0',
            'description': 'Unified index of all available skills across all directories',
            'auto_generated': True,
        },
        'sources': [
            'workspace/skills/',
            '~/.openclaw/kimi-skills/',
            '~/.openclaw/skills/',
            '/usr/lib/node_modules/openclaw/skills/',
            '~/.openclaw/extensions/*/skills/',
        ],
        'skills': [],
    }
    
    sources = [
        (workspace / 'skills', 'local'),
        (Path('/root/.openclaw/kimi-skills'), 'kimi'),
        (Path('/root/.openclaw/skills'), 'custom'),
        (Path('/usr/lib/node_modules/openclaw/skills'), 'system'),
    ]
    
    # Extensions
    extensions_dir = Path('/root/.openclaw/extensions')
    if extensions_dir.exists():
        for ext in extensions_dir.iterdir():
            if ext.is_dir() and 'skills' in (ext / 'skills').name:
                skills_dir = ext / 'skills'
                if skills_dir.exists():
                    sources.append((skills_dir, f'extension/{ext.name}'))
    
    for path, source in sources:
        print(f"Scanning {source}: {path}")
        found = scan_skills_dir(path, source)
        registry['skills'].extend(found)
        print(f"  Found {len(found)} skills")
    
    # Sort by name
    registry['skills'].sort(key=lambda x: x['name'].lower())
    
    # Write registry
    output = workspace / 'memory' / 'skills-registry.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Registry saved: {output}")
    print(f"Total skills: {len(registry['skills'])}")
    print(f"{'='*60}")
    
    # Print summary by source
    by_source = {}
    for s in registry['skills']:
        by_source[s['source']] = by_source.get(s['source'], 0) + 1
    
    print("\nBy source:")
    for src, count in sorted(by_source.items(), key=lambda x: -x[1]):
        print(f"  {src}: {count}")


if __name__ == '__main__':
    main()
