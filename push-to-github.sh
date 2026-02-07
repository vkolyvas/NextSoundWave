#!/bin/bash

# NextSoundWave GitHub Setup Script
# Run this to create and push to GitHub

set -e

echo "🐙 NextSoundWave GitHub Setup"
echo "============================"

# Check if gh is authenticated
if gh auth status &>/dev/null; then
    echo "✓ GitHub CLI authenticated"
else
    echo "⚠ GitHub CLI not authenticated"
    echo "Please run: gh auth login"
    echo "Or create repository manually at: https://github.com/new"
    echo ""
fi

# Create repository if it doesn't exist
REPO_NAME="nextsoundwave"
read -p "Enter your GitHub username: " GITHUB_USER

if [ -z "$GITHUB_USER" ]; then
    echo "❌ Username required"
    exit 1
fi

# Check if repo exists
if gh repo view "$GITHUB_USER/$REPO_NAME" &>/dev/null; then
    echo "✓ Repository exists: $GITHUB_USER/$REPO_NAME"
else
    echo "Creating repository..."
    gh repo create "$REPO_NAME" \
        --public \
        --description "Self-hosted music streaming with YouTube and ad-free embeds" \
        --source . \
        --push
fi

# Set remote and push
echo ""
echo "🚀 Pushing to GitHub..."
git remote add origin "https://github.com/$GITHUB_USER/$REPO_NAME.git" 2>/dev/null || true
git branch -M main
git push -u origin main

echo ""
echo "✅ Done! Repository: https://github.com/$GITHUB_USER/$REPO_NAME"
