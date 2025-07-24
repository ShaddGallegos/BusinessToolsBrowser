#!/bin/bash
# User-configurable variables - modify as needed
USER="${USER}"
USER_EMAIL="${USER}@${COMPANY_DOMAIN:-example.com}"
COMPANY_NAME="${COMPANY_NAME:-Your Company}"
COMPANY_DOMAIN="${COMPANY_DOMAIN:-example.com}"

# User-configurable variables - modify as needed
USER="${USER}"
USER_EMAIL="${USER}@${COMPANY_DOMAIN:-example.com}"
COMPANY_NAME="${COMPANY_NAME:-Your Company}"
COMPANY_DOMAIN="${COMPANY_DOMAIN:-example.com}"

# User-configurable variables - modify as needed
USER="${USER}"
USER_EMAIL="${USER}@${COMPANY_DOMAIN:-example.com}"
COMPANY_NAME="${COMPANY_NAME:-Your Company}"
COMPANY_DOMAIN="${COMPANY_DOMAIN:-example.com}"


# Script: Push_Repository_To_GitHub.sh
# Purpose: Push local Git repository to GitHub with proper error handling
# Exit on error
set -e

echo " Pushing repository to GitHub..."

# Check if we're in a Git repository
if [ ! -d ".git" ]; then
    echo " This is not a Git repository. Please run this script from the root of a Git repository."
    exit 1
fi

# Check if Git is installed
if ! command -v git &> /dev/null; then
    echo " Git is not installed. Please install Git first."
    exit 1
fi

# Check if there are any changes to commit
if [ -n "$(git status --porcelain)" ]; then
    echo " Uncommitted changes found. Adding and committing..."
    git add .
    
    # Prompt for commit message
    read -p "Enter commit message (or press Enter for default): " commit_message
    if [ -z "$commit_message" ]; then
        commit_message="Auto-commit: $(date '+%Y-%m-%d %H:%M:%S')"
    fi
    
    git commit -m "$commit_message"
    echo " Changes committed successfully"
else
    echo " No uncommitted changes found"
fi

# Check if remote origin exists
if ! git remote get-url origin &> /dev/null; then
    echo " No remote origin found. Please add a remote origin first:"
    echo "   git remote add origin https://github.com/username/repository.git"
    exit 1
fi

# Get current branch
current_branch=$(git branch --show-current)
echo " Pushing branch '$current_branch' to origin..."

# Push to GitHub
git push origin "$current_branch"

echo " Repository pushed to GitHub successfully!"
echo " Remote URL: $(git remote get-url origin)"