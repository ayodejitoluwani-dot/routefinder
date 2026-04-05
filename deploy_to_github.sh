#!/bin/bash
# GitHub deployment script for Route Finder

echo "=== Route Finder - GitHub Deployment ==="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Install from: https://git-scm.com/"
    exit 1
fi

echo "✅ Git is installed"

# Check if already in git repo
if [ ! -d .git ]; then
    echo "❌ Not a git repository. Run 'git init' first."
    exit 1
fi

echo "✅ Git repository initialized"

# Prompt for GitHub username
read -p "Enter your GitHub username: " github_username

# Repository name
repo_name="routefinder"
read -p "Repository name (default: $repo_name): " input_name
if [ ! -z "$input_name" ]; then
    repo_name="$input_name"
fi

# Check if repo exists on GitHub
echo ""
echo "Before pushing, you need to:"
echo "1. Go to https://github.com/new"
echo "2. Name it: $repo_name"
echo "3. Choose Public or Private"
echo "4. Do NOT check any initialization options"
echo "5. Click 'Create repository'"
echo ""
read -p "Press Enter after you've created the repository..."

# Add remote
echo ""
echo "Adding remote..."
git remote add origin "https://github.com/$github_username/$repo_name.git" 2>/dev/null || echo "Remote 'origin' already exists"

# Push to GitHub
echo "Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo "🔗 Your repository: https://github.com/$github_username/$repo_name"
else
    echo ""
    echo "❌ Push failed. Make sure:"
    echo "   - You created the repository on GitHub"
    echo "   - You have proper authentication set up"
    echo ""
    echo "Authentication options:"
    echo "  1. Use a personal access token (PAT):"
    echo "     https://github.com/settings/tokens"
    echo "  2. Set up SSH keys:"
    echo "     https://docs.github.com/en/authentication/connecting-to-github-with-ssh"
    echo ""
    echo "Or install GitHub CLI:"
    echo "  brew install gh"
    echo "  gh auth login"
    echo "  gh repo create $repo_name --source=. --push"
fi
