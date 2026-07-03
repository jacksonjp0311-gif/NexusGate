# NEXUS GATE Hermes-style PowerShell TUI
# Interactive console operator surface: chat-like prompt, selectable lanes, colored output,
# feedback logging, packet creation, debugging, self-healing, and AI handoff export.

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
    [ordered]@{ key="9"; name="pack";         tab="RELEASE";     desc="Compile pack manifest/bundle" }
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

function Header {
    Clear-Host
    Write-Host ""
    Write-Host "  ╔════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor DarkCyan
    Write-Host "  ║ NEXUS GATE :: HERMES-STYLE POWERSHELL TUI                                ║" -ForegroundColor Cyan
    Write-Host "  ║ Governed transfer shell | human feedback | AI feedback | self-healing     ║" -ForegroundColor Cyan
    Write-Host "  ╚════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor DarkCyan
    Write-Host ""
    $ctx = Get-LatestContext
    if ($ctx) {
        Write-Host ("  Health: {0} | Pressure: {1} | Dominant: {2}" -f $ctx.health.health_score, $ctx.health.evidence_pressure, $ctx.health.dominant_pressure_source) -ForegroundColor Green
        Write-Host ("  Next: {0}" -f $ctx.next_action) -ForegroundColor Yellow
    } else {
        Write-Host "  AI context missing. Run /interface or /evolve." -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "  Tabs: [HUMAN] [AI] [DEBUG] [SELF-HEAL] [EVIDENCE] [GRAPH] [RUNTIME] [REFLECT]" -ForegroundColor Gray
    Write-Host ""
}

function Show-Menu {
    Header
    Write-Host "  Process Lane Dropdown" -ForegroundColor White
    Write-Host "  ---------------------" -ForegroundColor DarkGray
    foreach ($lane in $Global:Lanes) {
        Write-Host ("  {0}. [{1}] {2,-12} - {3}" -f $lane.key, $lane.tab, $lane.name, $lane.desc) -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "  Chat commands:" -ForegroundColor White
    Write-Host "    /run <lane>       Run a lane, e.g. /run evolve" -ForegroundColor Gray
    Write-Host "    /note <text>      Append human/AI feedback note to FEEDBACK_LOG.md" -ForegroundColor Gray
    Write-Host "    /packet <summary> Create governed operation packet template" -ForegroundColor Gray
    Write-Host "    /debug            Show latest failure/debug tail" -ForegroundColor Gray
    Write-Host "    /ai               Print AI handoff block for copy/paste" -ForegroundColor Gray
    Write-Host "    /copy             Export AI handoff and copy it to clipboard" -ForegroundColor Gray
    Write-Host "    /snapshot         Write/open HTML TUI snapshot" -ForegroundColor Gray
    Write-Host "    /electron         Show Electron port contract" -ForegroundColor Gray
    Write-Host "    /graph            Show governed interconnect console" -ForegroundColor Gray
    Write-Host "    /domains          Show domain interconnection routes" -ForegroundColor Gray
    Write-Host "    /open-log         Open docs/feedback/FEEDBACK_LOG.md" -ForegroundColor Gray
    Write-Host "    /open-context     Open state/ai_feedback_context_latest.json" -ForegroundColor Gray
    Write-Host "    /menu             Redraw this menu" -ForegroundColor Gray
    Write-Host "    /exit             Close shell" -ForegroundColor Gray
    Write-Host ""
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
    $lines.Add("Read surfaces:")
    $lines.Add("  state/ai_feedback_context_latest.json")
    $lines.Add("  docs/feedback/FEEDBACK_LOG.md")
    $lines.Add("  reports/nexus_feedback_interface_report_latest.json")
    $lines.Add("  reports/nexus_self_healing_report_latest.json")
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
    body { font-family: Consolas, monospace; background: #111827; color: #e5e7eb; margin: 32px; }
    h1 { color: #67e8f9; }
    code, pre { background: #020617; color: #d1fae5; padding: 12px; display: block; }
    section { border-top: 1px solid #334155; margin-top: 24px; padding-top: 16px; }
    .metric { margin: 8px 0; }
    .grid { display: grid; grid-template-columns: repeat(4, minmax(120px, 1fr)); gap: 12px; }
    .tile { background: #020617; border: 1px solid #334155; padding: 12px; }
    .label { color: #94a3b8; font-size: 12px; }
    .value { color: #d1fae5; font-size: 18px; margin-top: 4px; }
    li { margin: 6px 0; }
  </style>
</head>
<body>
  <h1>NEXUS GATE TUI Snapshot</h1>
  <section>
    <div class="grid">
      <div class="tile"><div class="label">Health</div><div class="value">$health</div></div>
      <div class="tile"><div class="label">Pressure</div><div class="value">$pressure</div></div>
      <div class="tile"><div class="label">Graph</div><div class="value">$graphStatus</div></div>
      <div class="tile"><div class="label">Nodes / Edges</div><div class="value">$nodeCount / $edgeCount</div></div>
    </div>
    <div class="metric">Dominant pressure: $dominant</div>
    <div class="metric">Graph version: $graphVersion</div>
    <div class="metric">Next action: $next</div>
  </section>
  <section>
    <h2>Interconnect Checks</h2>
    <ul>
      $checkRows
    </ul>
  </section>
  <section>
    <h2>Placeholder Evidence</h2>
    <ul>
      $placeholderRows
    </ul>
  </section>
  <section>
  <h2>Launch</h2>
  <pre>.\scripts\nexus.ps1 tui
.\scripts\nexus.ps1 ui</pre>
  </section>
  <section>
  <h2>Bridge Surfaces</h2>
  <pre>state/ai_feedback_context_latest.json
docs/feedback/FEEDBACK_LOG.md
docs/feedback/operator_packets/*.json
reports/nexus_feedback_interface_report_latest.json
reports/nexus_self_healing_report_latest.json
reports/tui/nexus_tui_ai_handoff_latest.txt
reports/tui/nexus_tui_snapshot_latest.html</pre>
  </section>
  <section>
  <h2>Boundary</h2>
  <p>The operator surface may make governed actions visible and selectable. It may not become the operator, self-authorize, mutate graph state, or bypass gates.</p>
  </section>
</body>
</html>
"@
    $html | Out-File -FilePath $path -Encoding utf8
    Invoke-Item $path
    Say "Snapshot written/opened: reports\tui\nexus_tui_snapshot_latest.html" "OK"
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
    Write-Host "  reports/tui/nexus_tui_ai_handoff_latest.txt"
    Write-Host "  reports/tui/nexus_tui_snapshot_latest.html"
    Write-Host "Blocked: arbitrary shell commands, external API writes, secret access, self-authorization, memory promotion without evidence."
    Write-Host "===== NEXUS ELECTRON PORT CONTRACT END =====" -ForegroundColor Cyan
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
    if ($line -eq "/electron") { Show-ElectronContract; return $true }
    if ($line -eq "/graph" -or $line -eq "/interconnect") { Show-InterconnectConsole; return $true }
    if ($line -eq "/domains") { Show-DomainRoutes; return $true }
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
