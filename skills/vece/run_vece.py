#!/usr/bin/env python3
"""
Вече (Vece) — Council of High Intelligence для OpenClaw/Kimi
Запускает 4 мудрецов-агентов для дискуссии по вопросу.

Использование:
    python3 run_vece.py "Вопрос для обсуждения" [--triad strategy] [--members aristotle,munger,sun-tzu]
"""

import sys
import os
import re
import subprocess
import time
import json

# Карта доменов → мудрецы
DOMAIN_MAP = {
    "strategy": ["sun-tzu", "machiavelli", "aurelius"],
    "economics": ["munger", "machiavelli", "sun-tzu"],
    "product": ["torvalds", "machiavelli", "watts"],
    "ai": ["karpathy", "sutskever", "ada"],
    "decision": ["kahneman", "munger", "aurelius"],
    "design": ["rams", "torvalds", "watts"],
    "systems": ["meadows", "lao-tzu", "aristotle"],
    "risk": ["taleb", "sun-tzu", "sutskever"],
    "ethics": ["aurelius", "socrates", "lao-tzu"],
    "innovation": ["ada", "lao-tzu", "aristotle"],
    "shipping": ["torvalds", "musashi", "feynman"],
    "founder": ["musashi", "sun-tzu", "torvalds"],
    "debugging": ["feynman", "socrates", "ada"],
    "conflict": ["socrates", "machiavelli", "aurelius"],
    "complexity": ["lao-tzu", "aristotle", "ada"],
    "uncertainty": ["taleb", "sun-tzu", "sutskever"],
    "bias": ["kahneman", "socrates", "watts"],
}

# Ключевые слова для автовыбора домена
KEYWORD_MAP = {
    "монетиза": "economics",
    "цена": "economics",
    "подписк": "economics",
    "деньги": "economics",
    "доход": "economics",
    "стратег": "strategy",
    "конкурен": "strategy",
    "рынок": "strategy",
    "выход": "strategy",
    "продукт": "product",
    "фича": "product",
    "UX": "design",
    "дизайн": "design",
    "интерфейс": "design",
    "AI": "ai",
    "модель": "ai",
    "алгоритм": "ai",
    "ML": "ai",
    "решение": "decision",
    "выбор": "decision",
    "дилемм": "decision",
    "систем": "systems",
    "процесс": "systems",
    "риск": "risk",
    "опасност": "risk",
    "угроза": "risk",
    "этик": "ethics",
    "морал": "ethics",
    "долг": "ethics",
    "новаци": "innovation",
    "новатор": "innovation",
    "запуск": "shipping",
    "релиз": "shipping",
    "founder": "founder",
    "стартап": "founder",
    "баг": "debugging",
    "проблем": "debugging",
    "конфликт": "conflict",
    "спор": "conflict",
    "сложност": "complexity",
    "неопределен": "uncertainty",
    "искажен": "bias",
    "психолог": "bias",
    "когнитив": "bias",
}

COUNCIL_DIR = os.path.expanduser("~/.openclaw/workspace/skills/council-of-high-intelligence/agents")


def detect_domain(question):
    """Определяет домен вопроса по ключевым словам."""
    q_lower = question.lower()
    scores = {}
    for keyword, domain in KEYWORD_MAP.items():
        if keyword in q_lower:
            scores[domain] = scores.get(domain, 0) + 1
    if scores:
        return max(scores, key=scores.get)
    return "strategy"  # default


def load_member_prompt(member_name):
    """Загружает system prompt мудреца."""
    filepath = os.path.join(COUNCIL_DIR, f"council-{member_name}.md")
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r') as f:
        content = f.read()
    # Извлекаем Identity и Analytical Method
    identity = ""
    method = ""
    lines = content.split('\n')
    in_identity = False
    in_method = False
    for line in lines:
        if line.startswith('## Identity'):
            in_identity = True
            continue
        if line.startswith('## ') and in_identity:
            in_identity = False
        if line.startswith('## Analytical Method'):
            in_method = True
            continue
        if line.startswith('## ') and in_method:
            in_method = False
        if in_identity:
            identity += line + '\n'
        if in_method:
            method += line + '\n'
    return f"{identity}\n{method}".strip()


def select_members(question, triad=None, explicit_members=None):
    """Выбирает 4 мудреца для вече."""
    if explicit_members:
        return explicit_members.split(',')[:4]
    if triad and triad in DOMAIN_MAP:
        base = DOMAIN_MAP[triad]
    else:
        domain = detect_domain(question)
        base = DOMAIN_MAP.get(domain, DOMAIN_MAP["strategy"])
    # Добавляем 4-го мудреца — кого-то из смежных
    all_members = ["aristotle", "socrates", "sun-tzu", "ada", "aurelius", "machiavelli",
                   "lao-tzu", "feynman", "torvalds", "musashi", "watts", "karpathy",
                   "sutskever", "kahneman", "meadows", "munger", "taleb", "rams"]
    # Убираем дубликаты, добавляем дополнительных
    selected = list(base)
    for m in all_members:
        if m not in selected and len(selected) < 4:
            selected.append(m)
        if len(selected) >= 4:
            break
    return selected


def run_council(question, members):
    """Запускает дискуссию мудрецов."""
    print(f"🏛️  НОВГОРОДСКОЕ ВЕЧЕ")
    print(f"📋 Вопрос: {question}")
    print(f"👥 Мудрецы: {', '.join(members)}")
    print("=" * 60)
    
    # Раунд 1: Независимый анализ
    print("\n🔴 РАУНД 1: Независимый анализ")
    print("-" * 60)
    
    analyses = {}
    for member in members:
        prompt = load_member_prompt(member)
        if not prompt:
            print(f"⚠️  {member}: промпт не найден, пропускаем")
            continue
        
        # Запускаем subagent
        print(f"\n🧠 {member.upper()} думает...")
        # В реальном использовании тут sessions_spawn
        # Для демо — заглушка
        analyses[member] = f"[Анализ {member} по вопросу: {question}]"
    
    # Раунд 2: Перекрёстный допрос
    print("\n\n🔴 РАУНД 2: Перекрёстный допрос")
    print("-" * 60)
    
    for member in members:
        if member not in analyses:
            continue
        print(f"\n💬 {member.upper()} критикует других...")
        # Здесь subagent получает анализы других и критикует
    
    # Раунд 3: Финальные позиции
    print("\n\n🔴 РАУНД 3: Финальные позиции")
    print("-" * 60)
    
    verdicts = {}
    for member in members:
        if member not in analyses:
            continue
        print(f"\n⚖️  {member.upper()} голосует...")
        verdicts[member] = f"[Позиция {member}]"
    
    # Вердикт
    print("\n\n" + "=" * 60)
    print("🏛️  ВЕРДИКТ ВЕЧЕ")
    print("=" * 60)
    print(f"\n📋 Вопрос: {question}")
    print(f"👥 Участвовали: {', '.join(members)}")
    print(f"\n🎯 РЕКОМЕНДАЦИЯ:")
    print("   [Синтез мнений всех мудрецов]")
    print(f"\n❓ НЕРЕШЁННЫЕ ВОПРОСЫ:")
    print("   - [Вопрос 1]")
    print("   - [Вопрос 2]")
    print(f"\n📌 СЛЕДУЮЩИЕ ШАГИ:")
    print("   1. [Действие 1]")
    print("   2. [Действие 2]")
    
    return {
        "question": question,
        "members": members,
        "verdict": "[Синтез]",
        "next_steps": ["[Действие 1]", "[Действие 2]"]
    }


def main():
    if len(sys.argv) < 2:
        print("Использование: python3 run_vece.py 'Вопрос' [--triad домен] [--members имя1,имя2,имя3,имя4]")
        print(f"\nДоступные триады: {', '.join(DOMAIN_MAP.keys())}")
        sys.exit(1)
    
    question = sys.argv[1]
    triad = None
    explicit_members = None
    
    # Парсим аргументы
    for i, arg in enumerate(sys.argv):
        if arg == "--triad" and i + 1 < len(sys.argv):
            triad = sys.argv[i + 1]
        if arg == "--members" and i + 1 < len(sys.argv):
            explicit_members = sys.argv[i + 1]
    
    members = select_members(question, triad, explicit_members)
    result = run_council(question, members)
    
    # Сохраняем результат
    os.makedirs("/root/.openclaw/workspace/memory/vece", exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    with open(f"/root/.openclaw/workspace/memory/vece/{timestamp}.json", 'w') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Вердикт сохранён: memory/vece/{timestamp}.json")


if __name__ == "__main__":
    main()
