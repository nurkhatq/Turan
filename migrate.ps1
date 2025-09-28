# PowerShell Migration Helper Script
# Usage: .\migrate.ps1 revision --autogenerate -m "Migration message"
#        .\migrate.ps1 upgrade head

param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Arguments
)

if ($Arguments.Count -eq 0) {
    Write-Host "🔧 Alembic Migration Helper for Windows/Docker" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Green
    Write-Host "  .\migrate.ps1 revision --autogenerate -m `"Migration message`""
    Write-Host "  .\migrate.ps1 upgrade head"
    Write-Host "  .\migrate.ps1 downgrade -1"
    Write-Host "  .\migrate.ps1 current"
    Write-Host "  .\migrate.ps1 history"
    Write-Host ""
    Write-Host "This script runs Alembic commands inside Docker to avoid Windows connection issues." -ForegroundColor Yellow
    exit
}

# Convert arguments to string and pass to Python script
$ArgsString = $Arguments -join " "
python migrate.py $ArgsString
