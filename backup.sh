#!/usr/bin/env bash
# backup.sh — Smart backup script for OpenClaw workspace
# Usage: ./backup.sh [message]

set -e

WORKSPACE="/root/.openclaw/workspace"
COMMIT_MSG="${1:-"Auto backup: $(date '+%Y-%m-%d %H:%M')"}"

cd "$WORKSPACE"

echo "🔍 Checking git status..."

# Check if there are changes
if git diff --quiet && git diff --cached --quiet; then
    echo "✅ Nothing to backup. All clean."
    exit 0
fi

echo "📦 Staging changes..."

# Add only tracked + new files, respecting .gitignore
git add -A

echo "💾 Committing: $COMMIT_MSG"
git commit -m "$COMMIT_MSG" || true

echo "📤 Pushing to remote..."
REMOTE="workspace"
BRANCH=$(git branch --show-current)

# Проверяем, есть ли remote 'workspace', иначе используем 'origin'
if ! git remote | grep -q "^workspace$"; then
    REMOTE="origin"
fi

git push "$REMOTE" "$BRANCH" 2>/dev/null || {
    echo "❌ Push failed!"
    echo "   Возможные причины:"
    echo "   1. GitHub PAT (token) истёк или не имеет прав repo"
    echo "   2. Нет сети"
    echo "   3. Remote URL неправильный"
    echo ""
    echo "   Для проверки: git remote -v"
    echo "   Для ручного push: git push workspace main"
    exit 1
}

echo "✅ Backup complete: $(git log -1 --format='%h %s')"
echo "📊 Repo size: $(du -sh .git | cut -f1)"
