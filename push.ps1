# Usage: .\push.ps1 "your commit message"

param (
    [Parameter(Mandatory=$true, Position=0)]
    [string]$CommitMessage
)

Write-Host "📦 Staging all changes..." -ForegroundColor Cyan
git add .

Write-Host "📝 Committing: '$CommitMessage'..." -ForegroundColor Yellow
git commit -m "$CommitMessage"

Write-Host "🚀 Pushing to remote..." -ForegroundColor Green
git push origin main

Write-Host "✅ Successfully pushed to remote repository!" -ForegroundColor Cyan
