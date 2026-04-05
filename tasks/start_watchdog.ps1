# start_watchdog.ps1 — Start the local LLM Wiki manual drop daemon in the background
# Run: powershell -ExecutionPolicy Bypass -File tasks\start_watchdog.ps1

param(
    [string]$WikiRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$PythonExe = "python"
)

$LogDir = Join-Path $WikiRoot "logs"
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }

$ScriptPath = Join-Path $WikiRoot "tools\watchdog_monitor.py"
$LogPath = Join-Path $LogDir "watchdog.log"

Write-Host "`nStarting LLM Wiki Watchdog Daemon..."
Write-Host "Monitoring: $(Join-Path $WikiRoot "raw\manual") for incoming `.md` drops."

# Execute python script invisibly via Start-Process
Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$PythonExe $ScriptPath >> `"$LogPath`" 2>&1`"" -WindowStyle Hidden -WorkingDirectory $WikiRoot

Write-Host "  [OK] Process is now running in the background."
Write-Host "  Check logs at: $LogPath"
Write-Host "  To stop the daemon, terminate python instances running 'watchdog_monitor.py'.`n"
