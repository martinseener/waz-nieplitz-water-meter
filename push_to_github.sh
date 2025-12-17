#!/bin/bash
# Push WAZ Nieplitz Water Meter add-on to GitHub

set -e

echo "=================================================="
echo "Push to GitHub Repository"
echo "=================================================="
echo ""

REPO_URL="git@github.com:martinseener/waz-nieplitz-water-meter.git"
CURRENT_DIR=$(pwd)

# Check if we're in the right directory
if [ ! -f "config.json" ] || [ ! -f "run.py" ]; then
    echo "ERROR: Please run this script from the waz-nieplitz-water-meter directory"
    exit 1
fi

echo "Repository: $REPO_URL"
echo "Current directory: $CURRENT_DIR"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    echo "✓ Git initialized"
else
    echo "✓ Git already initialized"
fi

# Check if remote exists
if ! git remote | grep -q "origin"; then
    echo "Adding GitHub remote..."
    git remote add origin "$REPO_URL"
    echo "✓ Remote added"
else
    echo "✓ Remote already exists"
    # Update remote URL in case it changed
    git remote set-url origin "$REPO_URL"
fi

# Show what will be committed
echo ""
echo "Files to be committed:"
echo "====================="
git status --short 2>/dev/null || echo "(Git status unavailable - new repository)"

echo ""
echo "Files that will be INCLUDED:"
echo "  ✓ Core add-on files (config.json, run.py, Dockerfile, etc.)"
echo "  ✓ Documentation (*.md files)"
echo "  ✓ Test scripts (test_addon.py, run_tests.sh)"
echo "  ✓ Repository metadata (repository.json, LICENSE)"
echo ""
echo "Files that will be EXCLUDED (via .gitignore):"
echo "  ✗ Test data (test_data/, *.html)"
echo "  ✗ Runtime data (historical_readings.json, manual_fetch)"
echo "  ✗ IDE files (.vscode/, .idea/)"
echo "  ✗ Python cache (__pycache__/, *.pyc)"
echo ""

read -p "Continue with commit and push? [y/N]: " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

# Stage all files (respecting .gitignore)
echo ""
echo "Staging files..."
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "No changes to commit. Repository is up to date."
    echo ""
    echo "Checking if we need to push..."
    if git rev-parse --abbrev-ref --symbolic-full-name @{u} > /dev/null 2>&1; then
        # Upstream exists, check if we're ahead
        if [ "$(git rev-list --count @{u}..HEAD)" -eq 0 ]; then
            echo "Everything is up to date!"
            exit 0
        fi
    fi
else
    # Commit the changes
    echo "Creating commit..."
    read -p "Commit message [Initial commit of WAZ Nieplitz Water Meter add-on]: " commit_msg
    commit_msg=${commit_msg:-"Initial commit of WAZ Nieplitz Water Meter add-on"}

    git commit -m "$commit_msg"
    echo "✓ Changes committed"
fi

# Push to GitHub
echo ""
echo "Pushing to GitHub..."
if git rev-parse --abbrev-ref --symbolic-full-name @{u} > /dev/null 2>&1; then
    # Upstream exists, just push
    git push
else
    # First push, set upstream
    git push -u origin main 2>/dev/null || git push -u origin master 2>/dev/null || {
        echo ""
        echo "Note: Trying to determine default branch..."
        # Get current branch name
        BRANCH=$(git rev-parse --abbrev-ref HEAD)
        echo "Current branch: $BRANCH"
        git push -u origin "$BRANCH"
    }
fi

echo ""
echo "=================================================="
echo "✓ Successfully pushed to GitHub!"
echo "=================================================="
echo ""
echo "Repository URL: https://github.com/martinseener/waz-nieplitz-water-meter"
echo ""
echo "Next steps:"
echo "  1. Visit your repository on GitHub"
echo "  2. Add a description and topics"
echo "  3. (Optional) Add screenshots to docs/images/"
echo "  4. Add the repository to Home Assistant:"
echo ""
echo "     Settings → Add-ons → ⋮ → Repositories"
echo "     Add: https://github.com/martinseener/waz-nieplitz-water-meter"
echo ""
echo "See GITHUB_INSTALL.md for complete instructions."
echo ""
