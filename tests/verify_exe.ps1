# Post-build acceptance check. Launches the packaged exe from a foreign CWD.
$ErrorActionPreference = 'Stop'
$exe = Join-Path $PSScriptRoot '..\dist\ClaudeCodeManager.exe' | Resolve-Path

Write-Host '== version resource =='
$vi = (Get-Item $exe).VersionInfo
'{0} | {1} | {2} | {3}' -f $vi.ProductName, $vi.FileVersion, $vi.CompanyName, $vi.OriginalFilename

Write-Host '== launch from C:\ =='
Push-Location 'C:\'
$p = Start-Process -FilePath $exe -PassThru
Start-Sleep -Seconds 6
Pop-Location

if ($p.HasExited) { throw "exe exited early with code $($p.ExitCode)" }
Write-Host "running: PID $($p.Id)"

# no console window attached to a --windowed build
$title = $p.MainWindowTitle
Write-Host "window title: '$title'"

Stop-Process -Id $p.Id -Force
Write-Host '== config location =='
$cfg = Join-Path $env:APPDATA 'ClaudeCodeManager\config.json'
if (Test-Path $cfg) { Write-Host "config: $cfg"; Get-Content $cfg -Raw }
else { Write-Host "config not yet written (expected until a project is picked): $cfg" }
Write-Host 'EXE VERIFY OK'
