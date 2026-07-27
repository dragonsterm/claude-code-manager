# Build ClaudeCodeManager.exe (onedir). Run from the project root.
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
# Clear stale PyInstaller Tcl paths inherited from a launched onefile app.
Remove-Item Env:TCL_LIBRARY,Env:TK_LIBRARY -ErrorAction SilentlyContinue

$py = 'C:\Users\mahar\AppData\Local\Programs\Python\Python313\python.exe'
if (-not (Test-Path $py)) { $py = (Get-Command python).Source }

Write-Host '== clean ==' -ForegroundColor Cyan
foreach ($d in @('build', 'dist')) {
    if (Test-Path $d) { Remove-Item $d -Recurse -Force }
}

Write-Host '== tests ==' -ForegroundColor Cyan
& $py tests\run_tests.py
if ($LASTEXITCODE -ne 0) { throw 'unit tests failed' }
& $py tests\smoke_ui.py
if ($LASTEXITCODE -ne 0) { throw 'ui smoke failed' }

Write-Host '== build ==' -ForegroundColor Cyan
& $py -m PyInstaller ClaudeCodeManager.spec --noconfirm --clean
if ($LASTEXITCODE -ne 0) { throw 'pyinstaller failed' }

# Code signing: uncomment once an Authenticode cert is available. Unsigned
# builds trigger the SmartScreen "unknown publisher" prompt (see SECURITY.md).
# & signtool sign /fd sha256 /tr http://timestamp.digicert.com /td sha256 `
#     /a dist\ClaudeCodeManager\ClaudeCodeManager.exe

Write-Host '== hashes ==' -ForegroundColor Cyan
Get-ChildItem dist\ClaudeCodeManager.exe |
    Get-FileHash -Algorithm SHA256 |
    ForEach-Object { "$($_.Hash)  $(Split-Path $_.Path -Leaf)" } |
    Out-File dist\SHA256SUMS.txt -Encoding utf8

Get-Content dist\SHA256SUMS.txt
Write-Host "`nBuilt: dist\ClaudeCodeManager.exe" -ForegroundColor Green
