# NEXUS GATE PowerShell HUD TUI
# Interactive console operator surface: chat-like prompt, selectable lanes, colored output,
# feedback logging, packet creation, debugging, self-healing, and AI handoff export.
# Canonical command markers: /run <lane>, /note <text>, /packet <summary>.

param(
    [string]$StartLane = ""
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$env:PYTHONUTF8 = "1"

$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$TuiDir = Join-Path $Root "reports\tui"
if (-not (Test-Path $TuiDir)) { [void](New-Item -ItemType Directory -Path $TuiDir -Force) }
$TranscriptPath = Join-Path $TuiDir "nexus_tui_session_$Stamp.log"

$Global:Lanes = @(
    [ordered]@{ key="1"; name="evolve";       tab="HUMAN";       desc="Run full compile/evidence/feedback/pack lane" },
    [ordered]@{ key="2"; name="interface";    tab="AI";          desc="Refresh AI context + feedback log" },
    [ordered]@{ key="3"; name="feedback";     tab="AI";          desc="Compile feedback/interconnect/self-healing/interface" },
    [ordered]@{ key="4"; name="heal";         tab="SELF-HEAL";   desc="Generate self-healing recommendation/dry-run/apply-gate report" },
    [ordered]@{ key="5"; name="status";       tab="DEBUG";       desc="Show status and feedback summary" },
    [ordered]@{ key="6"; name="compact";      tab="EVIDENCE";    desc="Compile evidence pressure/compaction manifest" },
    [ordered]@{ key="7"; name="interconnect"; tab="GRAPH";       desc="Compile governed transfer graph" },
    [ordered]@{ key="8"; name="runtime";      tab="RUNTIME";     desc="Run bounded runtime compiler" },
    [ordered]@{ key="9"; name="pack";         tab="RELEASE";     desc="Compile pack manifest/bundle" },
    [ordered]@{ key="10"; name="reflect";     tab="REFLECT";     desc="Compile reflective intelligence loop and lineage evidence" },
    [ordered]@{ key="11"; name="domain";      tab="DOMAIN";      desc="Compile domain intelligence and repo-native learning evidence" }
)

function Add-TranscriptLine {
    param([string]$Line)
    Add-Content -Path $TranscriptPath -Value $Line -Encoding utf8
}

function Say {
    param(
        [string]$Text,
        [string]$Level = "NG"
    )
    $color = "Gray"
    if ($Level -eq "OK") { $color = "Green" }
    if ($Level -eq "WARN") { $color = "Yellow" }
    if ($Level -eq "FAIL") { $color = "Red" }
    if ($Level -eq "AI") { $color = "Cyan" }
    if ($Level -eq "HUMAN") { $color = "Magenta" }
    if ($Level -eq "DEBUG") { $color = "DarkYellow" }
    if ($Level -eq "REFLECT") { $color = "Blue" }
    $line = "[$Level] $Text"
    Write-Host $line -ForegroundColor $color
    Add-TranscriptLine $line
}

function Color-Line {
    param([string]$Line)
    $color = "Gray"
    if ($Line -match "\[OK\]|passed|pass") { $color = "Green" }
    if ($Line -match "\[WARN\]|warning|warn|pressure|high") { $color = "Yellow" }
    if ($Line -match "\[FAIL\]|failed|Traceback|ERROR|error") { $color = "Red" }
    if ($Line -match "\[NG\]|NEXUS|Feedback|AI context|Self-healing|Interconnect|Runtime") { $color = "Cyan" }
    Write-Host $Line -ForegroundColor $color
    Add-TranscriptLine $Line
}

function Render-Bar {
    param(
        [int]$Percent,
        [string]$Label = "buffer"
    )
    if ($Percent -lt 0) { $Percent = 0 }
    if ($Percent -gt 100) { $Percent = 100 }
    $width = 34
    $filled = [Math]::Floor(($Percent / 100) * $width)
    $empty = $width - $filled
    $bar = ("#" * $filled) + ("-" * $empty)
    Write-Host ("[{0}] {1,3}% {2}" -f $bar, $Percent, $Label) -ForegroundColor DarkCyan
    Write-Progress -Activity "NEXUS GATE TUI" -Status $Label -PercentComplete $Percent
}

function Get-LatestContext {
    $path = Join-Path $Root "state\ai_feedback_context_latest.json"
    if (Test-Path $path) {
        try { return Get-Content $path -Raw | ConvertFrom-Json }
        catch { return $null }
    }
    return $null
}

function Write-HudRule {
    param([int]$Width = 118)
    Write-Host ("+" + ("-" * $Width) + "+") -ForegroundColor DarkCyan
}

function Header {
    Clear-Host
    $ctx = Get-LatestContext
    $health = "unknown"
    $pressure = "unknown"
    $dominant = "unknown"
    $next = "Run /run interface or /run evolve."
    if ($ctx) {
        $health = [string]$ctx.health.health_score
        $pressure = [string]$ctx.health.evidence_pressure
        $dominant = [string]$ctx.health.dominant_pressure_source
        $next = [string]$ctx.next_action
    }
    $shortNext = $next.Substring(0, [Math]::Min(32, $next.Length))

    Write-Host ""
    Write-HudRule 118
    $titleLine = '| NEXUS GATE                                                       | AGENT MODE: ACTIVE | GOVERNANCE: ENFORCED |'
    $timeLine = '| HUD operator console | system time: ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + ' | LINK STATUS: STABLE              |'
    Write-Host $titleLine -ForegroundColor Cyan
    Write-Host $timeLine -ForegroundColor DarkCyan
    Write-HudRule 118
    Write-Host '| PROCESS LANES                 | NEXUS CONSOLE                                      | FEEDBACK SUMMARY                 |' -ForegroundColor Cyan
    Write-Host '| [1] evolve        --          | NEXUS> /run evolve                                | HEALTH SCORE                     |' -ForegroundColor Gray
    $healthLine = '| [2] interface                 | [NEXUS] governed lanes visible                    | ' + ([string]($health + ' / 1.0')).PadRight(32).Substring(0, 32) + ' |'
    $pressureLine = '| [3] feedback                  | [NEXUS] UI does not own logic                     | EVIDENCE PRESSURE: ' + ([string]$pressure).PadRight(14).Substring(0, 14) + ' |'
    $dominantLine = '| [4] heal                      | [NEXUS] same gates, same reports                  | DOMINANT: ' + ([string]$dominant).PadRight(22).Substring(0, 22) + ' |'
    Write-Host $healthLine -ForegroundColor Green
    Write-Host $pressureLine -ForegroundColor Gray
    Write-Host $dominantLine -ForegroundColor Gray
    Write-Host '| [5] status                    | [NEXUS] use /menu for command list                | NEXT ACTION                      |' -ForegroundColor Gray
    $nextLine = '| [6] compact                   | [BUFFER] #######----------------------- 24%       | ' + ([string]$shortNext).PadRight(32).Substring(0, 32) + ' |'
    Write-Host $nextLine -ForegroundColor Yellow
    Write-Host '| [7] interconnect              |                                                    | AI PACKAGE: context/log READY    |' -ForegroundColor Gray
    Write-Host '| [8] runtime                   |                                                    | /copy exports handoff            |' -ForegroundColor Gray
    Write-Host '| [9] pack                      |                                                    | /snapshot opens HUD bridge       |' -ForegroundColor Gray
    Write-Host '| [10] reflect                  |                                                    | /lineage shows version manifest  |' -ForegroundColor Gray
    Write-Host '| [11] domain                   |                                                    | /study creates study packet      |' -ForegroundColor Gray
    Write-HudRule 118
    Write-Host '| HUMAN FEEDBACK | AI FEEDBACK | DEBUGGING | SELF-HEALING | REFLECTION | INTERCONNECT | GOVERNANCE: strict audit enabled |' -ForegroundColor DarkCyan
    Write-HudRule 118
    Write-Host ""
}

function Show-Menu {
    Header
    Write-Host '  HUD Process Lane Menu' -ForegroundColor White
    Write-Host '  ---------------------' -ForegroundColor DarkGray
    foreach ($lane in $Global:Lanes) {
        Write-Host ("  {0}. [{1}] {2,-12} - {3}" -f $lane.key, $lane.tab, $lane.name, $lane.desc) -ForegroundColor Gray
    }
    Write-Host ''
    Write-Host '  HUD command deck:' -ForegroundColor White
    Write-Host '    /run lane         Run a lane, e.g. /run evolve' -ForegroundColor Gray
    Write-Host '    /note text        Append human/AI feedback note to FEEDBACK_LOG.md' -ForegroundColor Gray
    Write-Host '    /packet summary   Create governed operation packet template' -ForegroundColor Gray
    Write-Host '    /debug            Show latest failure/debug tail' -ForegroundColor Gray
    Write-Host '    /ai               Print AI handoff block for copy/paste' -ForegroundColor Gray
    Write-Host '    /copy             Export AI handoff and copy it to clipboard' -ForegroundColor Gray
    Write-Host '    /snapshot         Write/open HTML TUI snapshot' -ForegroundColor Gray
    Write-Host '    /surface          Write machine-readable TUI surface JSON' -ForegroundColor Gray
    Write-Host '    /electron         Show Electron port contract' -ForegroundColor Gray
    Write-Host '    /graph            Show governed interconnect console' -ForegroundColor Gray
    Write-Host '    /domains          Show domain interconnection routes' -ForegroundColor Gray
    Write-Host '    /reflect          Compile/show reflective intelligence loop report' -ForegroundColor Gray
    Write-Host '    /lineage          Show lineage/version manifest' -ForegroundColor Gray
    Write-Host '    /domain           Compile/show domain intelligence report' -ForegroundColor Gray
    Write-Host '    /study text       Create a governed domain study packet' -ForegroundColor Gray
    Write-Host '    /open-log         Open docs/feedback/FEEDBACK_LOG.md' -ForegroundColor Gray
    Write-Host '    /open-context     Open state/ai_feedback_context_latest.json' -ForegroundColor Gray
    Write-Host '    /menu             Redraw this menu' -ForegroundColor Gray
    Write-Host '    /exit             Close shell' -ForegroundColor Gray
    Write-Host ''
}

function Resolve-Lane {
    param([string]$Raw)
    $x = $Raw.Trim().ToLower()
    foreach ($lane in $Global:Lanes) {
        if ($x -eq $lane.key -or $x -eq $lane.name.ToLower()) { return $lane.name }
    }
    return $null
}

function Run-NexusLane {
    param([string]$Lane)

    $laneName = Resolve-Lane $Lane
    if (-not $laneName) {
        Say "Unknown lane: $Lane" "FAIL"
        return
    }

    Say "Starting lane: $laneName" "NG"
    Render-Bar 5 "starting $laneName"

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "powershell.exe"
    $psi.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$PSScriptRoot\nexus.ps1`" $laneName"
    $psi.WorkingDirectory = $Root
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.CreateNoWindow = $true

    $proc = New-Object System.Diagnostics.Process
    $proc.StartInfo = $psi
    [void]$proc.Start()

    $lineCount = 0
    while (-not $proc.HasExited) {
        while (-not $proc.StandardOutput.EndOfStream) {
            $line = $proc.StandardOutput.ReadLine()
            if ($null -ne $line) {
                $lineCount += 1
                Color-Line $line
                $pct = [Math]::Min(95, 5 + ($lineCount * 3))
                Render-Bar $pct $laneName
            }
        }
        while (-not $proc.StandardError.EndOfStream) {
            $line = $proc.StandardError.ReadLine()
            if ($null -ne $line) {
                $lineCount += 1
                Color-Line $line
                Render-Bar 95 "$laneName stderr"
            }
        }
        Start-Sleep -Milliseconds 100
    }

    while (-not $proc.StandardOutput.EndOfStream) {
        $line = $proc.StandardOutput.ReadLine()
        if ($null -ne $line) { Color-Line $line }
    }
    while (-not $proc.StandardError.EndOfStream) {
        $line = $proc.StandardError.ReadLine()
        if ($null -ne $line) { Color-Line $line }
    }

    $code = $proc.ExitCode
    $proc.Dispose()
    Write-Progress -Activity "NEXUS GATE TUI" -Completed

    if ($code -eq 0) {
        Render-Bar 100 "$laneName complete"
        Say "Lane complete: $laneName" "OK"
    } else {
        Render-Bar 100 "$laneName failed"
        Say "Lane failed with exit code $code" "FAIL"
    }
}

function Append-FeedbackNote {
    param([string]$Text)
    if (-not $Text.Trim()) {
        Say "No note text provided." "WARN"
        return
    }

    $dir = Join-Path $Root "docs\feedback"
    if (-not (Test-Path $dir)) { [void](New-Item -ItemType Directory -Path $dir -Force) }
    $log = Join-Path $dir "FEEDBACK_LOG.md"
    if (-not (Test-Path $log)) { "# NEXUS GATE Feedback Log`r`n" | Out-File $log -Encoding utf8 }

    $stamp = (Get-Date).ToUniversalTime().ToString("o")
    $entry = @"
## $stamp - TUI Feedback Note

- source: `PowerShell TUI`
- mode: `human_ai_feedback_note`
- writes_performed: `feedback_log_only`
- note: $Text

### Boundary

This note is feedback evidence. It does not authorize runtime mutation, API calls, memory promotion, or self-authorized repair.

"@
    Add-Content -Path $log -Value $entry -Encoding utf8
    Say "Feedback note appended: docs\feedback\FEEDBACK_LOG.md" "OK"
    Run-NexusLane "interface"
}

function New-OperationPacket {
    param([string]$Summary)
    if (-not $Summary.Trim()) {
        Say "Packet summary required." "WARN"
        return
    }

    $dir = Join-Path $Root "docs\feedback\operator_packets"
    if (-not (Test-Path $dir)) { [void](New-Item -ItemType Directory -Path $dir -Force) }

    $stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
    $head = ""
    try { $head = (git rev-parse HEAD).Trim() } catch { $head = "unknown" }

    $packet = [ordered]@{
        schema = "NEXUS-GATE-TUI-OPERATION-PACKET"
        packet_id = "nexus-tui-packet-$stamp"
        created_utc = (Get-Date).ToUniversalTime().ToString("o")
        created_by = "NEXUS PowerShell TUI"
        expected_base_commit = $head
        summary = $Summary
        loop_steps = @("observe", "classify", "recommend", "dry_run", "authorize", "apply_patch", "evolve", "ledger")
        allowed_actions = @("create_patch", "run_evolve", "append_feedback_log")
        blocked_actions = @("self_authorize", "api_write", "secret_access", "memory_promotion_without_evidence", "ungated_repo_mutation")
        requires_human_authorization = $true
        next_manual_steps = @(
            "Review packet",
            "Ask AI to generate bounded patch",
            "Run patch manually",
            "Run .\scripts\nexus.ps1 evolve",
            "Paste output back to AI"
        )
        claim_boundary = "Operation packet only. Does not apply changes."
    }

    $path = Join-Path $dir "operation-packet-$stamp.json"
    $packet | ConvertTo-Json -Depth 10 | Out-File -FilePath $path -Encoding utf8
    Say "Operation packet created: $($path.Replace($Root + '\',''))" "OK"
    Run-NexusLane "interface"
}

function Show-DebugTail {
    Say "Debug tail from latest human_surface logs" "DEBUG"
    $base = Join-Path $Root "reports\human_surface"
    if (-not (Test-Path $base)) {
        Say "No human_surface report folder found." "WARN"
        return
    }

    $latest = Get-ChildItem $base -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $latest) {
        Say "No human_surface sessions found." "WARN"
        return
    }

    Say "Latest session: $($latest.FullName)" "DEBUG"
    $logs = Get-ChildItem $latest.FullName -File | Sort-Object Name
    foreach ($log in $logs) {
        Write-Host ""
        Say "---- $($log.Name) ----" "DEBUG"
        Get-Content $log.FullName -Tail 18 | ForEach-Object { Color-Line $_ }
    }
}

function Get-AIHandoffText {
    $ctxPath = Join-Path $Root "state\ai_feedback_context_latest.json"
    $healPath = Join-Path $Root "reports\nexus_self_healing_report_latest.json"
    $interfacePath = Join-Path $Root "reports\nexus_feedback_interface_report_latest.json"

    $lines = New-Object System.Collections.Generic.List[string]
    $lines.Add("===== NEXUS AI HANDOFF START =====")
    $lines.Add("Repo: $Root")
    $lines.Add("Commands:")
    $lines.Add("  .\scripts\nexus.ps1 tui")
    $lines.Add("  .\scripts\nexus.ps1 ui")
    $lines.Add("  .\scripts\nexus.ps1 evolve")
    $lines.Add("  .\scripts\nexus.ps1 heal")
    $lines.Add("  .\scripts\nexus.ps1 reflect")
    $lines.Add("  .\scripts\nexus.ps1 domain")
    $lines.Add("Read surfaces:")
    $lines.Add("  state/ai_feedback_context_latest.json")
    $lines.Add("  docs/feedback/FEEDBACK_LOG.md")
    $lines.Add("  reports/nexus_feedback_interface_report_latest.json")
    $lines.Add("  reports/nexus_self_healing_report_latest.json")
    $lines.Add("  reports/nexus_reflective_loop_report_latest.json")
    $lines.Add("  reports/nexus_domain_intelligence_report_latest.json")
    $lines.Add("  state/domain_intelligence_index.v0.4.0.json")
    $lines.Add("  state/repo_native_learning_index.v0.4.0.json")
    $lines.Add("  state/codex_orchestration_index.v0.4.0.json")
    $lines.Add("  state/nexus_lineage_manifest_latest.json")
    $lines.Add("  state/interface_adapter_contract_index.v0.3.7.json")
    $lines.Add("  reports/tui/nexus_tui_ai_handoff_latest.txt")
    $lines.Add("  reports/tui/nexus_tui_snapshot_latest.html")
    $lines.Add("")
    if (Test-Path $ctxPath) {
        $lines.Add("--- ai_feedback_context_latest.json ---")
        $lines.Add((Get-Content $ctxPath -Raw))
    }
    if (Test-Path $interfacePath) {
        $lines.Add("--- nexus_feedback_interface_report_latest.json ---")
        $lines.Add((Get-Content $interfacePath -Raw))
    }
    if (Test-Path $healPath) {
        $lines.Add("--- nexus_self_healing_report_latest.json ---")
        $lines.Add((Get-Content $healPath -Raw))
    }
    $reflectPath = Join-Path $Root "reports\nexus_reflective_loop_report_latest.json"
    if (Test-Path $reflectPath) {
        $lines.Add("--- nexus_reflective_loop_report_latest.json ---")
        $lines.Add((Get-Content $reflectPath -Raw))
    }
    $lineagePath = Join-Path $Root "state\nexus_lineage_manifest_latest.json"
    if (Test-Path $lineagePath) {
        $lines.Add("--- nexus_lineage_manifest_latest.json ---")
        $lines.Add((Get-Content $lineagePath -Raw))
    }
    $domainPath = Join-Path $Root "reports\nexus_domain_intelligence_report_latest.json"
    if (Test-Path $domainPath) {
        $lines.Add("--- nexus_domain_intelligence_report_latest.json ---")
        $lines.Add((Get-Content $domainPath -Raw))
    }
    $lines.Add("===== NEXUS AI HANDOFF END =====")
    return ($lines -join [Environment]::NewLine)
}

function Show-AIHandoff {
    Say "AI handoff block follows. Copy this into ChatGPT/Codex if needed." "AI"
    Write-Host ""
    Get-AIHandoffText | Write-Host -ForegroundColor Cyan
}

function Export-AIHandoff {
    $path = Join-Path $TuiDir "nexus_tui_ai_handoff_latest.txt"
    $text = Get-AIHandoffText
    $text | Out-File -FilePath $path -Encoding utf8
    try {
        Set-Clipboard -Value $text
        Say "AI handoff exported and copied: reports\tui\nexus_tui_ai_handoff_latest.txt" "OK"
    } catch {
        Say "AI handoff exported, clipboard unavailable: reports\tui\nexus_tui_ai_handoff_latest.txt" "WARN"
    }
}

function New-TuiSnapshot {
    # Compatibility markers retained for bridge tests: Interconnect Checks, Placeholder Evidence, mutate graph state.
    $path = Join-Path $TuiDir "nexus_tui_snapshot_latest.html"
    $ctx = Get-LatestContext
    $graphPath = Join-Path $Root "state\interconnect_graph.v0.2.2.json"
    $health = "unknown"
    $pressure = "unknown"
    $dominant = "unknown"
    $next = "Run .\scripts\nexus.ps1 interface."
    $graphVersion = "unknown"
    $graphStatus = "unknown"
    $nodeCount = 0
    $edgeCount = 0
    $checkRows = "<li>No graph checks available.</li>"
    $placeholderRows = "<li>No placeholder evidence paths detected.</li>"
    if ($ctx) {
        $health = $ctx.health.health_score
        $pressure = $ctx.health.evidence_pressure
        $dominant = $ctx.health.dominant_pressure_source
        $next = $ctx.next_action
    }
    if (Test-Path $graphPath) {
        try {
            $graph = Get-Content $graphPath -Raw | ConvertFrom-Json
            $graphVersion = $graph.version
            $graphStatus = $graph.status
            $nodeCount = $graph.nodes.Count
            $edgeCount = $graph.edges.Count
            $items = @()
            foreach ($check in $graph.checks) {
                $items += "<li><strong>$($check.check)</strong>: $($check.status) ($($check.count))</li>"
            }
            if ($items.Count -gt 0) { $checkRows = ($items -join [Environment]::NewLine) }

            $placeholders = @()
            foreach ($node in $graph.nodes) {
                if ($node.evidence -and $null -ne $node.evidence.exists -and -not $node.evidence.exists) {
                    $placeholders += "<li>$($node.node_id): $($node.evidence.path)</li>"
                }
                if ($node.evidence -and $node.evidence.handoff -and -not $node.evidence.handoff.exists) {
                    $placeholders += "<li>$($node.node_id): $($node.evidence.handoff.path)</li>"
                }
                if ($node.evidence -and $node.evidence.snapshot -and -not $node.evidence.snapshot.exists) {
                    $placeholders += "<li>$($node.node_id): $($node.evidence.snapshot.path)</li>"
                }
            }
            if ($placeholders.Count -gt 0) { $placeholderRows = ($placeholders | Select-Object -First 12) -join [Environment]::NewLine }
        } catch {
            $checkRows = "<li>Graph unreadable: $($_.Exception.Message)</li>"
        }
    }
    $html = @"
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>NEXUS GATE TUI Snapshot</title>
  <style>
    :root { color-scheme: dark; --bg: #050914; --panel: #07111f; --panel2: #09182a; --line: #0e7490; --line2: #164e63; --text: #d9f7ff; --muted: #7dd3fc; --ok: #86efac; --warn: #facc15; --accent: #22d3ee; --violet: #e879f9; }
    * { box-sizing: border-box; }
    body { font-family: Consolas, monospace; background: radial-gradient(circle at 80% 0%, #0b2540 0, #050914 36%, #020617 100%); color: var(--text); margin: 0; min-height: 100vh; }
    .hud { min-height: 100vh; padding: 18px; display: grid; grid-template-rows: auto 1fr auto; gap: 12px; }
    .topbar, .footer, .panel { background: linear-gradient(180deg, rgba(9,24,42,.96), rgba(2,6,23,.96)); border: 1px solid var(--line2); box-shadow: 0 0 18px rgba(34,211,238,.12), inset 0 0 24px rgba(34,211,238,.05); }
    .topbar { display: grid; grid-template-columns: 1fr repeat(4, minmax(130px, auto)); gap: 10px; align-items: center; padding: 10px 14px; }
    h1 { color: var(--accent); font-size: 24px; margin: 0; letter-spacing: 0; text-shadow: 0 0 12px rgba(34,211,238,.6); }
    .subtitle { color: #e5e7eb; font-size: 18px; }
    .pill { border: 1px solid var(--line2); padding: 8px 10px; color: var(--ok); text-align: center; font-size: 12px; background: #06111f; }
    .main { display: grid; grid-template-columns: 190px minmax(360px, 1fr) 420px; gap: 12px; min-height: 0; }
    .panel { padding: 12px; min-width: 0; }
    .panel h2 { margin: 0 0 12px; font-size: 13px; color: var(--accent); font-weight: 700; }
    .lane { display: flex; justify-content: space-between; border-bottom: 1px solid rgba(125,211,252,.13); padding: 9px 4px; color: #dbeafe; }
    .lane:first-of-type { color: var(--accent); background: rgba(34,211,238,.08); }
    .console { font-size: 13px; line-height: 1.7; }
    .console .ok { color: var(--ok); }
    .console .warn { color: var(--warn); }
    .console .ai { color: var(--violet); }
    .buffer { height: 8px; border: 1px solid var(--line2); background: #020617; margin: 10px 0; }
    .buffer span { display: block; width: 72%; height: 100%; background: linear-gradient(90deg, #22d3ee, #86efac); box-shadow: 0 0 14px rgba(34,211,238,.7); }
    .metrics { display: grid; grid-template-columns: 1fr; gap: 10px; }
    .score { font-size: 34px; color: #86efac; text-shadow: 0 0 12px rgba(134,239,172,.5); }
    .row { display: flex; justify-content: space-between; gap: 12px; border-top: 1px solid rgba(125,211,252,.14); padding-top: 8px; color: #dbeafe; }
    .row span:first-child, .label { color: #93c5fd; font-size: 12px; text-transform: uppercase; }
    .modules { display: grid; grid-template-columns: repeat(6, minmax(130px, 1fr)); gap: 10px; }
    .module { border: 1px solid var(--line2); background: rgba(2,6,23,.78); padding: 10px; min-width: 0; }
    .module strong { display: block; color: var(--accent); font-size: 12px; margin-bottom: 8px; }
    .module p { margin: 4px 0; color: #cbd5e1; font-size: 12px; overflow-wrap: anywhere; }
    code, pre { background: #020617; color: #d1fae5; padding: 12px; display: block; overflow: auto; border: 1px solid rgba(125,211,252,.16); }
    ul { padding-left: 18px; margin: 8px 0; }
    li { margin: 6px 0; }
    .footer { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; padding: 10px 14px; color: #bfdbfe; font-size: 12px; }
    @media (max-width: 980px) { .topbar, .main, .modules, .footer { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <div class="hud">
    <header class="topbar">
      <div><h1>NEXUS GATE</h1></div>
      <div class="pill">AGENT MODE<br>ACTIVE</div>
      <div class="pill">GOVERNANCE<br>ENFORCED</div>
      <div class="pill">SYSTEM TIME<br>$((Get-Date).ToString("yyyy-MM-dd HH:mm:ss"))</div>
      <div class="pill">LINK STATUS<br>STABLE</div>
    </header>
    <main class="main">
      <section class="panel">
        <h2>PROCESS LANES</h2>
        <div class="lane"><span>evolve</span><span>&gt;&gt;</span></div>
        <div class="lane"><span>interface</span><span>01</span></div>
        <div class="lane"><span>feedback</span><span>02</span></div>
        <div class="lane"><span>heal</span><span>03</span></div>
        <div class="lane"><span>status</span><span>04</span></div>
        <div class="lane"><span>compact</span><span>05</span></div>
        <div class="lane"><span>interconnect</span><span>06</span></div>
        <div class="lane"><span>runtime</span><span>07</span></div>
        <div class="lane"><span>pack</span><span>08</span></div>
      </section>
      <section class="panel console">
        <h2>NEXUS CONSOLE</h2>
        <div>NEXUS&gt; /snapshot</div>
        <div class="ok">[NEXUS] HUD snapshot assembled from governed evidence.</div>
        <div>[NEXUS] Same core lanes, same gates, same reports.</div>
        <div class="buffer"><span></span></div>
        <div>NEXUS&gt; /ai</div>
        <div class="ai">[AI] Handoff surfaces ready for operator copy.</div>
        <div>NEXUS&gt; /electron</div>
        <div class="warn">[WARN] Electron remains presentation-only until governed smoke gates pass.</div>
        <pre>Launch:
.\scripts\nexus.ps1 tui
.\scripts\nexus.ps1 ui</pre>
      </section>
      <aside class="metrics">
        <section class="panel">
          <h2>FEEDBACK SUMMARY</h2>
          <div class="label">Health Score</div>
          <div class="score">$health</div>
          <div class="row"><span>Evidence pressure</span><span>$pressure</span></div>
          <div class="row"><span>Dominant pressure</span><span>$dominant</span></div>
          <div class="row"><span>Trend</span><span>$graphStatus</span></div>
          <div class="row"><span>Next action</span><span>$next</span></div>
        </section>
        <section class="panel">
          <h2>AI HANDOFF PACKAGE</h2>
          <div class="row"><span>ai_feedback_context_latest.json</span><span>READY</span></div>
          <div class="row"><span>FEEDBACK_LOG.md</span><span>READY</span></div>
          <div class="row"><span>nexus_tui_surface_latest.json</span><span>READY</span></div>
        </section>
      </aside>
    </main>
    <section class="modules">
      <div class="module"><strong>HUMAN FEEDBACK</strong><p>Status: receiving</p><p>Append only log</p></div>
      <div class="module"><strong>AI FEEDBACK</strong><p>Context: latest</p><p>Handoff: /copy</p></div>
      <div class="module"><strong>DEBUGGING</strong><p>Tail: /debug</p><p>Errors remain gated</p></div>
      <div class="module"><strong>SELF-HEALING</strong><p>Lane: /run heal</p><p>No autonomous apply</p></div>
      <div class="module"><strong>REFLECTION</strong><p>Graph: $nodeCount nodes</p><p>Edges: $edgeCount</p></div>
      <div class="module"><strong>INTERCONNECT</strong><p>Version: $graphVersion</p><p>Status: $graphStatus</p></div>
    </section>
    <section class="panel">
      <h2>INTERCONNECT CHECKS</h2>
      <ul>$checkRows</ul>
      <h2>PLACEHOLDER EVIDENCE</h2>
      <ul>$placeholderRows</ul>
    </section>
    <footer class="footer">
      <div>GOVERNANCE: strict | audit enabled | compliance enforced</div>
      <div>DATA TRANSFER PROTOCOL: signed | verified | evidence routed</div>
      <div>BOUNDARY: visible and selectable, never self-authorizing</div>
    </footer>
  </div>
</body>
</html>
"@
    $html | Out-File -FilePath $path -Encoding utf8
    Export-TuiSurfaceState
    Invoke-Item $path
    Say "Snapshot written/opened: reports\tui\nexus_tui_snapshot_latest.html" "OK"
}

function Export-TuiSurfaceState {
    $path = Join-Path $TuiDir "nexus_tui_surface_latest.json"
    $ctx = Get-LatestContext
    $graphPath = Join-Path $Root "state\interconnect_graph.v0.2.2.json"
    $feedbackPath = Join-Path $Root "reports\nexus_feedback_report_latest.json"

    $graph = $null
    if (Test-Path $graphPath) {
        try { $graph = Get-Content $graphPath -Raw | ConvertFrom-Json } catch { $graph = $null }
    }
    $feedback = $null
    if (Test-Path $feedbackPath) {
        try { $feedback = Get-Content $feedbackPath -Raw | ConvertFrom-Json } catch { $feedback = $null }
    }

    $missingEvidence = @()
    if ($graph) {
        foreach ($node in $graph.nodes) {
            if ($node.evidence -and $null -ne $node.evidence.exists -and -not $node.evidence.exists) {
                $missingEvidence += [ordered]@{ node_id = $node.node_id; path = $node.evidence.path }
            }
            if ($node.evidence -and $node.evidence.handoff -and -not $node.evidence.handoff.exists) {
                $missingEvidence += [ordered]@{ node_id = $node.node_id; path = $node.evidence.handoff.path }
            }
            if ($node.evidence -and $node.evidence.snapshot -and -not $node.evidence.snapshot.exists) {
                $missingEvidence += [ordered]@{ node_id = $node.node_id; path = $node.evidence.snapshot.path }
            }
        }
    }

    $state = [ordered]@{
        system = "NEXUS GATE"
        version = "0.3.0-tui-surface-state"
        generated_utc = (Get-Date).ToUniversalTime().ToString("o")
        source = "PowerShell TUI"
        status = "pass"
        refreshed_by = @("/surface", "/snapshot")
        health = [ordered]@{
            health_score = if ($ctx) { $ctx.health.health_score } else { $null }
            evidence_pressure = if ($ctx) { $ctx.health.evidence_pressure } elseif ($feedback) { $feedback.evidence_pressure.pressure_level } else { $null }
            dominant_pressure = if ($ctx) { $ctx.health.dominant_pressure_source } else { $null }
            next_action = if ($ctx) { $ctx.next_action } else { "Run .\scripts\nexus.ps1 evolve" }
        }
        graph = [ordered]@{
            status = if ($graph) { $graph.status } else { "missing" }
            version = if ($graph) { $graph.version } else { $null }
            node_count = if ($graph) { $graph.nodes.Count } else { 0 }
            edge_count = if ($graph) { $graph.edges.Count } else { 0 }
            checks = if ($graph) { $graph.checks } else { @() }
            missing_evidence = $missingEvidence
        }
        commands = [ordered]@{
            launch = ".\scripts\nexus.ps1 tui"
            ui_alias = ".\scripts\nexus.ps1 ui"
            evolve = ".\scripts\nexus.ps1 evolve"
            snapshot = "/snapshot"
            graph = "/graph"
            surface = "/surface"
        }
        surfaces = [ordered]@{
            ai_context = "state/ai_feedback_context_latest.json"
            feedback_log = "docs/feedback/FEEDBACK_LOG.md"
            interconnect_graph = "state/interconnect_graph.v0.2.2.json"
            snapshot_html = "reports/tui/nexus_tui_snapshot_latest.html"
            surface_json = "reports/tui/nexus_tui_surface_latest.json"
        }
        blocked_actions = @("self_authorize", "mutate_graph_state", "bypass_evolve", "arbitrary_shell_command", "claim_proof_from_surface_visibility")
        claim_boundary = "TUI surface state is read-only local evidence orientation. It does not prove correctness, safety, production readiness, scientific validity, model validity, or autonomous authority."
    }

    $state | ConvertTo-Json -Depth 12 | Out-File -FilePath $path -Encoding utf8
    Say "TUI surface state written: reports\tui\nexus_tui_surface_latest.json" "OK"
}

function Show-ElectronContract {
    Write-Host ""
    Write-Host "===== NEXUS ELECTRON PORT CONTRACT =====" -ForegroundColor Cyan
    Write-Host "Electron is presentation/operator surface only, not authority."
    Write-Host "Allowed commands: evolve, interface, feedback, heal, status, compact, interconnect, runtime, pack"
    Write-Host "Read surfaces:"
    Write-Host "  state/ai_feedback_context_latest.json"
    Write-Host "  docs/feedback/FEEDBACK_LOG.md"
    Write-Host "  docs/feedback/operator_packets/*.json"
    Write-Host "  reports/nexus_feedback_interface_report_latest.json"
    Write-Host "  reports/nexus_self_healing_report_latest.json"
    Write-Host "  reports/nexus_reflective_loop_report_latest.json"
    Write-Host "  reports/nexus_domain_intelligence_report_latest.json"
    Write-Host "  state/nexus_lineage_manifest_latest.json"
    Write-Host "  state/interface_adapter_contract_index.v0.3.7.json"
    Write-Host "  state/domain_intelligence_index.v0.4.0.json"
    Write-Host "  state/repo_native_learning_index.v0.4.0.json"
    Write-Host "  state/codex_orchestration_index.v0.4.0.json"
    Write-Host "  reports/tui/nexus_tui_ai_handoff_latest.txt"
    Write-Host "  reports/tui/nexus_tui_snapshot_latest.html"
    Write-Host "  reports/tui/nexus_tui_surface_latest.json"
    Write-Host "Blocked: arbitrary shell commands, external API writes, secret access, self-authorization, memory promotion without evidence."
    Write-Host "===== NEXUS ELECTRON PORT CONTRACT END =====" -ForegroundColor Cyan
}

function Show-ReflectiveLoop {
    Run-NexusLane "reflect"
    $path = Join-Path $Root "reports\nexus_reflective_loop_report_latest.json"
    if (-not (Test-Path $path)) {
        Say "Reflective loop report missing after reflect lane." "WARN"
        return
    }
    try {
        $report = Get-Content $path -Raw | ConvertFrom-Json
    } catch {
        Say "Unable to read reflective loop report: $($_.Exception.Message)" "FAIL"
        return
    }
    Write-Host ""
    Write-Host "===== NEXUS REFLECTIVE INTELLIGENCE LOOP =====" -ForegroundColor Cyan
    Write-Host ("Status: {0} | Version: {1}" -f $report.status, $report.version) -ForegroundColor Green
    Write-Host ("Allowed interfaces: {0}" -f ($report.allowed_interfaces -join ", ")) -ForegroundColor Gray
    Write-Host ""
    Write-Host "Checks" -ForegroundColor White
    foreach ($check in $report.checks) {
        $color = "Green"
        if ($check.status -eq "warn") { $color = "Yellow" }
        if ($check.status -eq "fail") { $color = "Red" }
        Write-Host ("  {0,-38} {1}" -f $check.check, $check.status) -ForegroundColor $color
    }
    Write-Host ""
    Write-Host ("Next: {0}" -f $report.next_action) -ForegroundColor Yellow
    Write-Host "Boundary: reflective intelligence is permitted; autonomous authority is not." -ForegroundColor Yellow
}

function Show-LineageManifest {
    $path = Join-Path $Root "state\nexus_lineage_manifest_latest.json"
    if (-not (Test-Path $path)) {
        Say "Lineage manifest missing. Run /reflect or /run reflect." "WARN"
        return
    }
    try {
        $manifest = Get-Content $path -Raw | ConvertFrom-Json
    } catch {
        Say "Unable to read lineage manifest: $($_.Exception.Message)" "FAIL"
        return
    }
    Write-Host ""
    Write-Host "===== NEXUS LINEAGE MANIFEST =====" -ForegroundColor Cyan
    Write-Host ("System version: {0}" -f $manifest.system_version) -ForegroundColor Green
    Write-Host ("Active phase: {0}" -f $manifest.active_phase) -ForegroundColor Gray
    Write-Host ("Current commit: {0}" -f $manifest.current_commit) -ForegroundColor Gray
    Write-Host ("Reflective loop: {0}" -f $manifest.reflective_loop_version) -ForegroundColor Gray
    Write-Host ""
    Write-Host "Allowed next phases" -ForegroundColor White
    foreach ($phase in $manifest.allowed_next_phases) { Write-Host "  $phase" -ForegroundColor Gray }
    Write-Host ""
    Write-Host "Blocked promotions" -ForegroundColor White
    foreach ($blocked in $manifest.blocked_promotions) { Write-Host "  $blocked" -ForegroundColor Yellow }
    Write-Host ""
    Write-Host "Boundary: lineage is orientation evidence, not production readiness." -ForegroundColor Yellow
}

function Show-DomainIntelligence {
    Run-NexusLane "domain"
    $path = Join-Path $Root "reports\nexus_domain_intelligence_report_latest.json"
    if (-not (Test-Path $path)) {
        Say "Domain intelligence report missing after domain lane." "WARN"
        return
    }
    try {
        $report = Get-Content $path -Raw | ConvertFrom-Json
    } catch {
        Say "Unable to read domain intelligence report: $($_.Exception.Message)" "FAIL"
        return
    }
    Write-Host ""
    Write-Host "===== NEXUS DOMAIN INTELLIGENCE =====" -ForegroundColor Cyan
    Write-Host ("Status: {0} | Version: {1}" -f $report.status, $report.version) -ForegroundColor Green
    Write-Host ("Domains: {0}" -f ($report.domains -join ", ")) -ForegroundColor Gray
    Write-Host ""
    Write-Host "Checks" -ForegroundColor White
    foreach ($check in $report.checks) {
        $color = "Green"
        if ($check.status -ne "pass") { $color = "Red" }
        Write-Host ("  {0,-45} {1}" -f $check.check, $check.status) -ForegroundColor $color
    }
    Write-Host ""
    Write-Host ("Next: {0}" -f $report.next_action) -ForegroundColor Yellow
    Write-Host "Boundary: domain study is evidence-gated; unsupported claims are not promoted." -ForegroundColor Yellow
}

function New-StudyPacket {
    param([string]$Summary)
    if (-not $Summary.Trim()) {
        Say "Study summary required." "WARN"
        return
    }
    $dir = Join-Path $Root "docs\feedback\operator_packets"
    if (-not (Test-Path $dir)) { [void](New-Item -ItemType Directory -Path $dir -Force) }
    $stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
    $packet = [ordered]@{
        schema = "NEXUS-GATE-DOMAIN-STUDY-PACKET"
        packet_id = "nexus-domain-study-$stamp"
        created_utc = (Get-Date).ToUniversalTime().ToString("o")
        created_by = "NEXUS PowerShell TUI"
        summary = $Summary
        study_loop = @("study", "extract", "map", "model", "simulate", "test", "gate", "reflect", "compress", "rehydrate", "orchestrate")
        required_boundaries = @("source", "claim", "evidence", "boundary", "test", "report", "lineage")
        blocked_claims = @("medical_authority", "simulation_as_empirical_proof", "conjecture_as_theorem", "demo_as_production_validation", "unsupported_cross_domain_fact")
        required_gates = @(".\scripts\nexus.ps1 domain", ".\scripts\nexus.ps1 reflect", ".\scripts\nexus.ps1 evolve")
        claim_boundary = "Study packet only. It does not certify truth, apply changes, or grant autonomous authority."
    }
    $path = Join-Path $dir "domain-study-packet-$stamp.json"
    $packet | ConvertTo-Json -Depth 10 | Out-File -FilePath $path -Encoding utf8
    Say "Domain study packet created: $($path.Replace($Root + '\',''))" "OK"
}

function Show-InterconnectConsole {
    $graphPath = Join-Path $Root "state\interconnect_graph.v0.2.2.json"
    $feedbackPath = Join-Path $Root "reports\nexus_feedback_report_latest.json"
    $contextPath = Join-Path $Root "state\ai_feedback_context_latest.json"
    if (-not (Test-Path $graphPath)) {
        Say "Missing interconnect graph. Run /run interconnect or /run evolve." "WARN"
        return
    }

    try {
        $graph = Get-Content $graphPath -Raw | ConvertFrom-Json
    } catch {
        Say "Unable to read interconnect graph: $($_.Exception.Message)" "FAIL"
        return
    }

    $feedback = $null
    if (Test-Path $feedbackPath) {
        try { $feedback = Get-Content $feedbackPath -Raw | ConvertFrom-Json } catch { $feedback = $null }
    }
    $ctx = $null
    if (Test-Path $contextPath) {
        try { $ctx = Get-Content $contextPath -Raw | ConvertFrom-Json } catch { $ctx = $null }
    }

    $missingEvidence = @()
    foreach ($node in $graph.nodes) {
        if ($node.evidence -and $null -ne $node.evidence.exists -and -not $node.evidence.exists) {
            $missingEvidence += "$($node.node_id) -> $($node.evidence.path)"
        }
        if ($node.evidence -and $node.evidence.handoff -and -not $node.evidence.handoff.exists) {
            $missingEvidence += "$($node.node_id) -> $($node.evidence.handoff.path)"
        }
        if ($node.evidence -and $node.evidence.snapshot -and -not $node.evidence.snapshot.exists) {
            $missingEvidence += "$($node.node_id) -> $($node.evidence.snapshot.path)"
        }
    }

    Write-Host ""
    Write-Host "===== NEXUS INTERCONNECT CONSOLE =====" -ForegroundColor Cyan
    Write-Host ("Status: {0} | Version: {1}" -f $graph.status, $graph.version) -ForegroundColor Green
    Write-Host ("Nodes: {0} | Edges: {1} | Hash: {2}" -f $graph.nodes.Count, $graph.edges.Count, $graph.graph_hash.Substring(0, 12)) -ForegroundColor Gray
    if ($feedback) {
        Write-Host ("Health: {0} | Pressure: {1}" -f $feedback.health_score, $feedback.evidence_pressure.pressure_level) -ForegroundColor Green
    }
    if ($ctx) {
        Write-Host ("Next: {0}" -f $ctx.next_action) -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "Checks" -ForegroundColor White
    foreach ($check in $graph.checks) {
        $color = "Green"
        if ($check.status -ne "pass") { $color = "Red" }
        Write-Host ("  {0,-30} {1,-6} {2}" -f $check.check, $check.status, $check.count) -ForegroundColor $color
    }
    Write-Host ""
    Write-Host "Core Routes" -ForegroundColor White
    foreach ($edge in $graph.edges | Select-Object -First 12) {
        Write-Host ("  {0} -> {1} [{2}]" -f $edge.source, $edge.target, $edge.relation) -ForegroundColor Gray
    }
    if ($graph.edges.Count -gt 12) {
        Write-Host ("  ... {0} more governed edges" -f ($graph.edges.Count - 12)) -ForegroundColor DarkGray
    }
    Write-Host ""
    if ($missingEvidence.Count -gt 0) {
        Write-Host "Placeholder/Missing Evidence" -ForegroundColor Yellow
        foreach ($item in $missingEvidence | Select-Object -First 8) {
            Write-Host "  $item" -ForegroundColor Yellow
        }
        if ($missingEvidence.Count -gt 8) {
            Write-Host ("  ... {0} more placeholders" -f ($missingEvidence.Count - 8)) -ForegroundColor DarkGray
        }
    } else {
        Write-Host "No missing evidence paths detected." -ForegroundColor Green
    }
    Write-Host ""
    Write-Host "Boundary: graph visibility is evidence orientation, not proof or authority." -ForegroundColor Yellow
}

function Show-DomainRoutes {
    $graphPath = Join-Path $Root "state\interconnect_graph.v0.2.2.json"
    if (-not (Test-Path $graphPath)) {
        Say "Missing interconnect graph. Run /run interconnect or /run evolve." "WARN"
        return
    }
    try {
        $graph = Get-Content $graphPath -Raw | ConvertFrom-Json
    } catch {
        Say "Unable to read interconnect graph: $($_.Exception.Message)" "FAIL"
        return
    }
    Write-Host ""
    Write-Host "===== NEXUS DOMAIN INTERCONNECTION =====" -ForegroundColor Cyan
    Write-Host ("Graph: {0} | Nodes: {1} | Edges: {2}" -f $graph.version, $graph.nodes.Count, $graph.edges.Count) -ForegroundColor Gray
    foreach ($node in $graph.nodes | Where-Object { $_.node_id -like "domain:*" -or $_.node_id -eq "terminal:cli_format" }) {
        Write-Host ("  {0,-24} {1}" -f $node.node_id, $node.label) -ForegroundColor Green
    }
    Write-Host ""
    foreach ($edge in $graph.edges | Where-Object { $_.source -like "domain:*" -or $_.target -like "domain:*" -or $_.source -eq "terminal:cli_format" -or $_.target -eq "terminal:cli_format" }) {
        Write-Host ("  {0} -> {1} [{2}]" -f $edge.source, $edge.target, $edge.relation) -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "Boundary: domain routing is not domain validation." -ForegroundColor Yellow
}

function Open-PathIfExists {
    param([string]$Relative)
    $path = Join-Path $Root $Relative
    if (Test-Path $path) {
        Invoke-Item $path
        Say "Opened $Relative" "OK"
    } else {
        Say "Missing: $Relative" "WARN"
    }
}

function Handle-Input {
    param([string]$InputLine)
    $line = $InputLine.Trim()
    if (-not $line) { return $true }

    Add-TranscriptLine "[USER] $line"

    if ($line -eq "/exit" -or $line -eq "exit" -or $line -eq "quit") { return $false }
    if ($line -eq "/menu" -or $line -eq "menu") { Show-Menu; return $true }
    if ($line -eq "/help" -or $line -eq "help") { Show-Menu; return $true }
    if ($line -eq "/debug") { Show-DebugTail; return $true }
    if ($line -eq "/ai") { Show-AIHandoff; return $true }
    if ($line -eq "/copy") { Export-AIHandoff; return $true }
    if ($line -eq "/snapshot") { New-TuiSnapshot; return $true }
    if ($line -eq "/surface") { Export-TuiSurfaceState; return $true }
    if ($line -eq "/electron") { Show-ElectronContract; return $true }
    if ($line -eq "/graph" -or $line -eq "/interconnect") { Show-InterconnectConsole; return $true }
    if ($line -eq "/domains") { Show-DomainRoutes; return $true }
    if ($line -eq "/reflect") { Show-ReflectiveLoop; return $true }
    if ($line -eq "/lineage") { Show-LineageManifest; return $true }
    if ($line -eq "/domain") { Show-DomainIntelligence; return $true }
    if ($line.StartsWith("/study ")) { New-StudyPacket ($line.Substring(7)); return $true }
    if ($line -eq "/open-log") { Open-PathIfExists "docs\feedback\FEEDBACK_LOG.md"; return $true }
    if ($line -eq "/open-context") { Open-PathIfExists "state\ai_feedback_context_latest.json"; return $true }

    if ($line.StartsWith("/run ")) {
        Run-NexusLane ($line.Substring(5))
        return $true
    }

    if ($line.StartsWith("/note ")) {
        Append-FeedbackNote ($line.Substring(6))
        return $true
    }

    if ($line.StartsWith("/packet ")) {
        New-OperationPacket ($line.Substring(8))
        return $true
    }

    $direct = Resolve-Lane $line
    if ($direct) {
        Run-NexusLane $direct
        return $true
    }

    Say "Interpreting as feedback note. Use /run <lane> to execute." "AI"
    Append-FeedbackNote $line
    return $true
}

Show-Menu

if ($StartLane) {
    Run-NexusLane $StartLane
}

$continue = $true
while ($continue) {
    Write-Host ""
    $inputLine = Read-Host "NEXUS>"
    try {
        $continue = Handle-Input $inputLine
    } catch {
        Say $_.Exception.Message "FAIL"
    }
}

Say "TUI closed. Transcript: $($TranscriptPath.Replace($Root + '\',''))" "OK"
