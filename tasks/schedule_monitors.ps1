# schedule_monitors.ps1 — Register LLM Wiki ingestion jobs in Windows Task Scheduler
# Run once as Administrator: powershell -ExecutionPolicy Bypass -File tasks\schedule_monitors.ps1

param(
    [string]$WikiRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$PythonExe = "python"
)

$LogDir = Join-Path $WikiRoot "logs"
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }

function Register-WikiTask {
    param(
        [string]$TaskName,
        [string]$Script,
        [string]$TriggerSpec,    # e.g. "Daily 07:00" or "Hourly 4"
        [string]$Args = ""
    )
    $action = New-ScheduledTaskAction `
        -Execute $PythonExe `
        -Argument "$Script $Args" `
        -WorkingDirectory $WikiRoot

    $trigger = switch -Wildcard ($TriggerSpec) {
        "Daily *"  {
            $t = $TriggerSpec -replace "Daily ", ""
            New-ScheduledTaskTrigger -Daily -At $t
        }
        "Weekly *" {
            $parts = $TriggerSpec -split " "
            New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At $parts[1]
        }
        "Hourly *" {
            $hours = [int]($TriggerSpec -replace "Hourly ", "")
            New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Hours $hours) `
                -Once -At (Get-Date)
        }
        default { New-ScheduledTaskTrigger -Daily -At "07:00" }
    }

    $settings = New-ScheduledTaskSettingsSet `
        -ExecutionTimeLimit (New-TimeSpan -Hours 1) `
        -StartWhenAvailable `
        -RunOnlyIfNetworkAvailable

    $logFile = Join-Path $LogDir "ingestion.log"
    $fullAction = New-ScheduledTaskAction `
        -Execute "cmd.exe" `
        -Argument "/c `"$PythonExe $Script $Args >> `"$logFile`" 2>&1`"" `
        -WorkingDirectory $WikiRoot

    try {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
        Register-ScheduledTask `
            -TaskName $TaskName `
            -Action $fullAction `
            -Trigger $trigger `
            -Settings $settings `
            -RunLevel Highest `
            -Force | Out-Null
        Write-Host "  [OK] Registered: $TaskName"
    } catch {
        Write-Host "  [ERROR] Failed to register ${TaskName}: $_"
    }
}

Write-Host "`nLLM Wiki — Windows Task Scheduler Setup"
Write-Host "Wiki root: $WikiRoot"
Write-Host "Python:    $PythonExe`n"

# arXiv — daily 07:00
Register-WikiTask "LLMWiki-arXiv"   "tools\arxiv_monitor.py"     "Daily 07:00"

# CVE — every 4 hours
Register-WikiTask "LLMWiki-CVE"     "tools\cve_monitor.py"       "Hourly 4"

# GitHub — daily 08:00
Register-WikiTask "LLMWiki-GitHub"  "tools\github_monitor.py"    "Daily 08:00"

# RSS — daily 09:00
Register-WikiTask "LLMWiki-RSS"     "tools\rss_monitor.py"       "Daily 09:00"

# Curated weekly sources — weekly Monday 06:00
Register-WikiTask "LLMWiki-Curated" "tools\curated_monitor.py"   "Weekly 06:00"

# Lightweight lint — daily 23:00
Register-WikiTask "LLMWiki-Lint"    "tools\lint.py"              "Daily 23:00"

# Deep lint — weekly Sunday 02:00
Register-WikiTask "LLMWiki-DeepLint" "tools\lint.py"             "Weekly 02:00"  "--deep"

# Rebuild index — daily 23:30
Register-WikiTask "LLMWiki-Index"   "tools\index.py"             "Daily 23:30"

# Git auto-commit — every 30 min via a helper script (see below)
$commitScript = Join-Path $WikiRoot "tasks\git_autocommit.ps1"
if (-not (Test-Path (Split-Path $commitScript))) {
    New-Item -ItemType Directory -Path (Split-Path $commitScript) | Out-Null
}
@"
Set-Location '$WikiRoot'
`$ts = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
git add -A
git commit -m "auto: wiki update `$ts" 2>&1 | Out-File -Append '$LogDir\ingestion.log'
"@ | Set-Content $commitScript

$commitAction = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NonInteractive -File `"$commitScript`""
$commitTrigger = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes 30) -Once -At (Get-Date)
Unregister-ScheduledTask -TaskName "LLMWiki-GitCommit" -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName "LLMWiki-GitCommit" -Action $commitAction -Trigger $commitTrigger `
    -Settings (New-ScheduledTaskSettingsSet -StartWhenAvailable) -RunLevel Highest -Force | Out-Null
Write-Host "  [OK] Registered: LLMWiki-GitCommit (every 30 min)"

Write-Host "`nDone. View tasks in Task Scheduler under 'LLMWiki-*'"
Write-Host "To remove all: Get-ScheduledTask -TaskName 'LLMWiki-*' | Unregister-ScheduledTask -Confirm:`$false`n"
