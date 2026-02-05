# preprocess_clean.ps1
# Purges unit test output from preprocess_test.py

$ScriptDir = [string]$PSScriptRoot

$TargetDirs = @(
    (Join-Path -Path $ScriptDir -ChildPath "input\data")
    (Join-Path -Path $ScriptDir -ChildPath "output\data")
    (Join-Path -Path $ScriptDir -ChildPath "output\img")
)

Write-Host "Cleaning up preprocess_test.py unit test output."
Write-Host "ScriptDir = $ScriptDir"
Write-Host "ScriptDir type = $($ScriptDir.GetType().FullName)"

foreach ($dir in $TargetDirs) {
    if (Test-Path -LiteralPath $dir) {
        Write-Host "Cleaning $dir"
        Get-ChildItem -LiteralPath $dir -File -Force | Remove-Item -Force
    }
    else {
        Write-Host "Directory not found. Skipping $dir"
    }
}

Write-Host "Cleanup completed."
