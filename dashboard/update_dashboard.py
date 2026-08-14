#!/usr/bin/env python3
"""Update the Kimicito Status Dashboard with fresh data."""

import os
import subprocess
from datetime import datetime, timezone

WORKSPACE = "/root/.openclaw/workspace"
DASHBOARD_FILE = os.path.join(WORKSPACE, "dashboard", "index.html")

def run(cmd, cwd=WORKSPACE):
    return subprocess.check_output(cmd, shell=True, cwd=cwd, text=True).strip()

def get_timestamp():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

def count_projects():
    dirs = [d for d in os.listdir(os.path.join(WORKSPACE, "projects")) 
            if os.path.isdir(os.path.join(WORKSPACE, "projects", d))]
    return len(dirs), dirs

def count_skills():
    result = run("find . -name 'SKILL.md' -not -path '*/node_modules/*' -not -path '*/.git/*' 2>/dev/null | wc -l")
    return int(result)

def count_git_changes():
    try:
        result = run("git status --short | wc -l")
        return int(result)
    except:
        return 0

def count_memory_files():
    mem_dir = os.path.join(WORKSPACE, "memory")
    if not os.path.exists(mem_dir):
        return 0
    return len([f for f in os.listdir(mem_dir) if f.endswith('.md')])

def get_git_status_for_project(path):
    try:
        result = run("git status --short | wc -l", cwd=path)
        return int(result)
    except:
        return -1

def get_last_commit(path, cwd=WORKSPACE):
    try:
        result = run(f"git -C {path} log --oneline -1 2>/dev/null || echo 'N/A'")
        return result
    except:
        return "N/A"

def build_projects_table():
    _, projects = count_projects()
    rows = []
    for proj in sorted(projects):
        path = os.path.join(WORKSPACE, "projects", proj)
        git_changes = get_git_status_for_project(path)
        if git_changes == 0:
            status = '<span class="badge badge-success">clean</span>'
        elif git_changes == -1:
            status = '<span class="badge badge-info">no git</span>'
        else:
            status = f'<span class="badge badge-warning">{git_changes} modified</span>'
        last_commit = get_last_commit(path)
        rows.append(f'''        <tr>
          <td><strong>{proj}</strong></td>
          <td><span class="path">{path}</span></td>
          <td>{status}</td>
          <td>{last_commit}</td>
        </tr>''')
    return '\n'.join(rows)

def build_skills_table():
    skills_dir = os.path.join(WORKSPACE, "skills")
    rows = []
    if os.path.exists(skills_dir):
        for skill in sorted(os.listdir(skills_dir)):
            skill_path = os.path.join(skills_dir, skill)
            if not os.path.isdir(skill_path):
                continue
            has_doc = "yes" if os.path.exists(os.path.join(skill_path, "SKILL.md")) else "no"
            doc_badge = '<span class="badge badge-success">SKILL.md</span>' if has_doc == "yes" else '<span class="badge badge-warning">Нет</span>'
            status_badge = '<span class="badge badge-success">active</span>' if has_doc == "yes" else '<span class="badge badge-warning">draft</span>'
            rows.append(f'''        <tr>
          <td><strong>{skill}</strong></td>
          <td><span class="path">{skill_path}</span></td>
          <td>{status_badge}</td>
          <td>{doc_badge}</td>
        </tr>''')
    return '\n'.join(rows)

def build_memory_table():
    mem_dir = os.path.join(WORKSPACE, "memory")
    rows = []
    if os.path.exists(mem_dir):
        for f in sorted(os.listdir(mem_dir)):
            if not f.endswith('.md'):
                continue
            filepath = os.path.join(mem_dir, f)
            size = os.path.getsize(filepath)
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath), tz=timezone.utc).strftime("%Y-%m-%d %H:%M")
            rows.append(f'''        <tr>
          <td><strong>{f}</strong></td>
          <td><span class="path">{filepath}</span></td>
          <td>{size} bytes</td>
          <td>{mtime}</td>
        </tr>''')
    return '\n'.join(rows)

def main():
    ts = get_timestamp()
    proj_count, _ = count_projects()
    skill_count = count_skills()
    git_changes = count_git_changes()
    mem_count = count_memory_files()

    # Read existing dashboard
    with open(DASHBOARD_FILE, 'r', encoding='utf-8') as f:
        html = f.read()

    # Update stats
    html = re.sub(
        r'<p class="timestamp">Последнее обновление: .*?</p>',
        f'<p class="timestamp">Последнее обновление: {ts}</p>',
        html
    )
    html = re.sub(
        r'(<div class="stat-card">\s*<h3>Проекты</h3>\s*<div class="value">)\d+(</div>)',
        rf'\g<1>{proj_count}\g<2>',
        html
    )
    html = re.sub(
        r'(<div class="stat-card warning">\s*<h3>Изменений в git</h3>\s*<div class="value">)\d+(</div>)',
        rf'\g<1>{git_changes}\g<2>',
        html
    )
    html = re.sub(
        r'(<div class="stat-card success">\s*<h3>Активных skills</h3>\s*<div class="value">)\d+(</div>)',
        rf'\g<1>{skill_count}\g<2>',
        html
    )
    html = re.sub(
        r'(<div class="stat-card">\s*<h3>Файлов памяти</h3>\s*<div class="value">)\d+(</div>)',
        rf'\g<1>{mem_count}\g<2>',
        html
    )

    # Update Projects table
    projects_table = build_projects_table()
    html = re.sub(
        r'(<div class="section">\s*<h2>📁 Проекты</h2>\s*<div class="table-wrap">\s*<table>\s*<tr><th>Проект</th><th>Путь</th><th>Git статус</th><th>Последний коммит</th></tr>).*?(\s*</table>)',
        rf'\g<1>\n{projects_table}\g<2>',
        html,
        flags=re.DOTALL
    )

    # Update Skills table  
    skills_table = build_skills_table()
    html = re.sub(
        r'(<div class="section">\s*<h2>🛠️ Skills</h2>\s*<div class="table-wrap">\s*<table>\s*<tr><th>Skill</th><th>Путь</th><th>Статус</th><th>Документация</th></tr>).*?(\s*</table>)',
        rf'\g<1>\n{skills_table}\g<2>',
        html,
        flags=re.DOTALL
    )

    # Update Memory table
    memory_table = build_memory_table()
    html = re.sub(
        r'(<div class="section">\s*<h2>🧠 Память и конфиги</h2>\s*<div class="table-wrap">\s*<table>\s*<tr><th>Файл</th><th>Путь</th><th>Размер</th><th>Изменён</th></tr>).*?(\s*</table>)',
        rf'\g<1>\n{memory_table}\g<2>',
        html,
        flags=re.DOTALL
    )

    # Update Git status section
    try:
        workspace_branch = run("git branch --show-current")
        workspace_status = "clean" if git_changes == 0 else f"{git_changes} changes"
        status_badge = '<span class="badge badge-success">clean</span>' if git_changes == 0 else f'<span class="badge badge-warning">{git_changes} changes</span>'
        
        git_html = f'''    <div class="table-wrap">
      <table>
        <tr><th>Репозиторий</th><th>Ветка</th><th>Синхронизация</th><th>Путь</th></tr>
        <tr>
          <td><strong>openclaw-workspace</strong></td>
          <td><span class="badge badge-info">{workspace_branch}</span></td>
          <td>{status_badge}</td>
          <td><span class="path">{WORKSPACE}</span></td>
        </tr>
      </table>
    </div>'''
        html = re.sub(
            r'(<div class="section">\s*<h2>🌐 Git статус</h2>\s*<div class="table-wrap">\s*<table>).*?(\s*</table>\s*</div>)',
            git_html,
            html,
            flags=re.DOTALL
        )
    except:
        pass

    with open(DASHBOARD_FILE, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Dashboard updated: {ts}")
    print(f"  Projects: {proj_count}")
    print(f"  Skills: {skill_count}")
    print(f"  Git changes: {git_changes}")
    print(f"  Memory files: {mem_count}")

if __name__ == "__main__":
    import re
    main()
