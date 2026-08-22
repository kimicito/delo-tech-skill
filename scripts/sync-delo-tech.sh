#!/bin/bash
# Синхронизация skills/delo-tech/ → github.com/kimicito/delo-tech-skill
# Использование: ./sync-to-delo-tech-skill.sh

set -e

echo "🔄 Синхронизация delo-tech skill в отдельный репозиторий..."

# Проверяем, что мы в workspace
cd /root/.openclaw/workspace

# Push через subtree
echo "📤 Отправка изменений..."
git subtree push --prefix=skills/delo-tech delo-tech-skill master

echo "✅ Готово! Репозиторий обновлён:"
echo "   https://github.com/kimicito/delo-tech-skill"
