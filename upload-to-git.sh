#!/bin/bash
# Upload Script for VPS to Git Account
# Date: February 10, 2026
# Purpose: Upload all modified files to git account

echo "🚀 INITIALIZING GIT REPOSITORY IN WORKSPACE..."

cd /root/.openclaw/workspace

# Check if already a git repo
if [ -d .git ]; then
    echo "✅ Workspace is already a git repository"
    echo "📦 Adding all modified files..."
    git add .
else
    echo "⚠️  Workspace is NOT a git repository"
    echo "🔄 Initializing as new git repo..."
    git init
    git config user.name "OpenClaw Agent"
    git config user.email "agent@openclaw"
    git config core.autocrlf true
    git config core.eol lf
    git add .
fi

echo "📦 Checking status..."
git status

echo "📝 Creating commit..."
git commit -m "Update: Super Bowl betting system + agent configurations + security hardening
- Date: $(date)
- Changes: All modified files in workspace
- Status: Post-game monitoring mode (48+ hours since Super Bowl)"

echo "✅ Files ready for upload"
echo ""
echo "🔍 Next Steps:"
echo "1. If git remote is configured:"
echo "   git push origin master"
echo "2. If git remote is NOT configured:"
echo "   git remote add origin <your-git-url>"
echo "   git push -u origin master"
echo ""
echo "📊 Modified Files:"
git diff --stat HEAD^1
