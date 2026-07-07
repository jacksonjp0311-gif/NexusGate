# NEXUS failure compiler helper for generated All-One scripts.

function New-NexusCompiledFailure {
    param(
        [string]$Stage,
        [int]$ExitCode,
        [string]$LogPath,
        [string]$WoundId = "UNCLASSIFIED_WOUND",
        [string]$ReportsDir = ".\reports"
    )

    New-Item -ItemType Directory -Force -Path $ReportsDir | Out-Null

    $raw = @()
    if (Test-Path -LiteralPath $LogPath) {
        $raw = Get-Content -LiteralPath $LogPath -ErrorAction SilentlyContinue
    }

    $patterns = @(
        '^\s*FAIL:',
        '^\s*ERROR:',
        'Traceback',
        'AssertionError',
        'SyntaxError',
        'ParserError',
        'Exception',
        'FAILED',
        'stage\s*:',
        'code\s*:'
    )

    $hits = New-Object System.Collections.Generic.List[string]
    for ($i = 0; $i -lt $raw.Count; $i++) {
        $line = [string]$raw[$i]
        $matched = $false
        foreach ($p in $patterns) {
            if ($line -match $p) { $matched = $true }
        }

        if ($matched) {
            $start = [Math]::Max(0, $i - 1)
            $end = [Math]::Min($raw.Count - 1, $i + 2)
            for ($j = $start; $j -le $end; $j++) {
                $compact = ([string]$raw[$j]) -replace '\s+', ' '
                if ($compact.Length -gt 260) { $compact = $compact.Substring(0,260) + "..." }
                $hits.Add(("{0}: {1}" -f ($j + 1), $compact))
            }
        }
    }

    $unique = @($hits | Select-Object -Unique -First 80)
    $failedTests = @($unique | Where-Object { $_ -match 'FAIL:|ERROR:' })

    $summary = [ordered]@{
        wound_id = $WoundId
        stage = $Stage
        exit_code = $ExitCode
        log_path = $LogPath
        log_line_count = $raw.Count
        failed_tests = $failedTests
        traceback_heads = $unique
        doctor_summary = "Validation failed at $Stage. Generate a close script for this wound only."
        next_close_target = $Stage
        stability_lock = "BLOCKED_UNTIL_CLOSE_SCRIPT_PASSES"
    }

    $jsonPath = Join-Path $ReportsDir "nexus_compiled_failure_latest.json"
    $mdPath = Join-Path $ReportsDir "nexus_compiled_failure_latest.md"
    ($summary | ConvertTo-Json -Depth 6) | Set-Content -LiteralPath $jsonPath -Encoding UTF8

    $md = @()
    $md += "# Nexus Compiled Failure"
    $md += ""
    $md += "- wound_id: $WoundId"
    $md += "- stage: $Stage"
    $md += "- exit_code: $ExitCode"
    $md += "- log_path: $LogPath"
    $md += "- log_line_count: $($raw.Count)"
    $md += "- stability_lock: BLOCKED_UNTIL_CLOSE_SCRIPT_PASSES"
    $md += ""
    $md += "## Traceback Heads"
    foreach ($line in $unique) { $md += "- $line" }
    $md | Set-Content -LiteralPath $mdPath -Encoding UTF8

    return $summary
}

function Write-NexusStabilityLock {
    param(
        [string]$WhatWasDone,
        [string[]]$Verifier,
        [string]$Commit = "",
        [bool]$Pushed = $false,
        [string]$Status = ""
    )

    Write-Host ""
    Write-Host "WHAT WAS DONE"
    Write-Host $WhatWasDone
    Write-Host ""
    Write-Host "VERIFIER"
    foreach ($v in $Verifier) { Write-Host ("- " + $v) }
    Write-Host ""
    Write-Host "STABILITY LOCK"
    Write-Host ("- commit: " + $Commit)
    Write-Host ("- pushed: " + $Pushed)
    Write-Host ("- status: " + $Status)
    Write-Host "- generated residue cleaned unless intentionally committed"
    Write-Host "- no autonomous authority"
}
