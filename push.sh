#!/bin/bash

# Quick Push Script for NextSoundWave
# Run after setting your GitHub username

GITHUB_USER="YOUR_USERNAME"
REPO_NAME="nextsoundwave"

echo "🔧 Updating remote URL..."
git remote set-url origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"
git remote -v

echo ""
echo "🚀 Renaming branch to main..."
git branch -M main

echo ""
echo "📤 Pushing to GitHub..."
echo "   https://github.com/$GITHUB_USER/$REPO_NAME"
echo ""
read -p "Press Enter to push..."

git push -u origin main

echo ""
echo "✅ Done! Visit: https://github.com/$GITHUB_USER/$REPO_NAME"
