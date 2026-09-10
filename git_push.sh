#!/bin/bash

# Usage: ./git_push.sh "your commit message"

if [ -z "$1" ]; then
    echo "❌ Error: Please provide a commit message."
    echo "Usage: ./git_push.sh \"your commit message\""
    exit 1
fi

COMMIT_MSG="$1"

echo "📦 Staging all changes..."
git add .

echo "📝 Committing: \"$COMMIT_MSG\"..."
git commit -m "$COMMIT_MSG"

echo "🚀 Pushing to remote..."
git push origin main

echo "✅ Successfully pushed to remote repository!"
