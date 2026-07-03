# NEXUS GATE human-readable operator surface
param(
    [ValidateSet("all", "compile", "runtime", "pack", "status", "gitfix")]
    [string]$Command = "all",
    [switch]$NoGit
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$env:PYTHONUTF8 = "1"

$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$HumanDir = Join-Path $Root "reports\human_surface\$Stamp"
[void](New-Item -ItemType Directory -Path $HumanDir -Force)

function Say {
    param([string]$Message, [string]$Level = "NG")
    Write-Host "[$Level] $Message"
}

function Write-Log {
    param([string]$Name, [string[]]$Lines)
    $Path = Join-Path $HumanDir $Name
    $Lines | Out-File -FilePath $Path -Encoding utf8
    return $Path
}

function Last-Lines {
    param([string[]]$Lines, [int]$Count = 30)
    if (-not $Lines) { return @() }
    if ($Lines.Count -le $Count) { return $Lines }
    return $Lines[($Lines.Count - $Count)..($Lines.Count - 1)]
}

function Invoke-Step {
    param(
        [string]$Name,
        [string]$LogName,
        [scriptblock]$Block
    )
    Say "$Name..." "NG"
    $old = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = & $Block 2>&1
    $code = $LASTEXITCODE
    $ErrorActionPreference = $old
    $logPath = Write-Log -Name $LogName -Lines ($output | ForEach-Object { [string]$_ })

    if ($code -ne 0) {
        Say "$Name failed. Log: $logPath" "FAIL"
        Last-Lines -Lines ($output | ForEach-Object { [string]$_ }) -Count 40 | ForEach-Object { Write-Host $_ }
        exit $code
    }

    Say "$Name passed. Log: $logPath" "OK"
}

function Set-GitQuietLineEndings {
    $gitCmd = Get-Command git -ErrorAction SilentlyContinue
    if ($gitCmd) {
        git config core.autocrlf false | Out-Null
        git config core.safecrlf false | Out-Null
        git config core.eol native | Out-Null
    }
}

function Invoke-GitQuiet {
    param([string[]]$GitArgs)
    $gitCmd = Get-Command git -ErrorAction SilentlyContinue
    if (-not $gitCmd) {
        Say "Git not found. Skipping git operation." "WARN"
        return
    }

    $old = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = & git @GitArgs 2>&1
    $code = $LASTEXITCODE
    $ErrorActionPreference = $old

    $filtered = @()
    foreach ($line in $output) {
        $s = [string]$line
        if ($s -match "CRLF will be replaced by LF") { continue }
        if ($s -match "LF will be replaced by CRLF") { continue }
        if ($s -match "LF will be replaced by LF") { continue }
        $filtered += $s
    }

    if ($filtered.Count -gt 0) {
        $filtered | ForEach-Object { Write-Host $_ }
    }

    if ($code -ne 0) {
        throw "git $($GitArgs -join ' ') failed with exit code $code"
    }
}

function Run-All {
    Say "NEXUS GATE human compile surface" "NG"
    Say "Detailed logs: $HumanDir" "NG"

    Invoke-Step "Python compile" "01_python_compile.log" { python -m compileall nexus_gate tests }
    Invoke-Step "Unit tests" "02_unit_tests.log" { python -m unittest discover -s tests }
    Invoke-Step "NEXUS compiler" "03_nexus_compiler.json" { python -m nexus_gate.compiler --root . --json }
    Invoke-Step "Adapter compiler" "04_adapter_compiler.json" { python -m nexus_gate.adapters.compile --root . --json }
    Invoke-Step "Receptor compiler" "05_receptor_compiler.json" { python -m nexus_gate.receptors.compile --root . --json }
    Invoke-Step "Bridge compiler" "06_bridge_compiler.json" { python -m nexus_gate.bridge.compile --root . --json }
    Invoke-Step "Runtime compiler" "07_runtime_compiler.json" { python -m nexus_gate.bridge.runtime_compiler --root . --json }
    Invoke-Step "Pack compiler" "08_pack_compiler.json" { python -m nexus_gate.build.packer --root . --out dist --json }

    Say "Compiled report files written." "OK"
    Say "Human surface passed." "OK"
}

function Show-Status {
    Say "NEXUS GATE status" "NG"
    foreach ($path in @(
        ".\reports\nexus_compile_report_latest.json",
        ".\reports\nexus_adapter_compile_report_latest.json",
        ".\reports\nexus_receptor_compile_report_latest.json",
        ".\reports\nexus_bridge_compile_report_latest.json",
        ".\reports\nexus_runtime_compile_report_latest.json",
        ".\reports\nexus_bounded_runtime_report_latest.json",
        ".\dist\nexus_gate_pack_manifest_latest.json"
    )) {
        if (Test-Path $path) {
            try {
                $data = Get-Content $path -Raw | ConvertFrom-Json
                $status = $data.status
                if (-not $status) { $status = "present" }
                Say "$path => $status" "OK"
            }
            catch {
                Say "$path => present" "OK"
            }
        }
        if (-not (Test-Path $path)) {
            Say "$path => missing" "WARN"
        }
    }
}

if ($Command -eq "gitfix") {
    Set-GitQuietLineEndings
    Say "Local Git line-ending noise policy applied." "OK"
    exit 0
}

if ($Command -eq "status") {
    Show-Status
    exit 0
}

if ($Command -eq "compile") {
    Invoke-Step "Python compile" "01_python_compile.log" { python -m compileall nexus_gate tests }
    Invoke-Step "Unit tests" "02_unit_tests.log" { python -m unittest discover -s tests }
    Invoke-Step "NEXUS compiler" "03_nexus_compiler.json" { python -m nexus_gate.compiler --root . --json }
    Say "Compile surface passed." "OK"
    exit 0
}

if ($Command -eq "runtime") {
    Invoke-Step "Runtime compiler" "07_runtime_compiler.json" { python -m nexus_gate.bridge.runtime_compiler --root . --json }
    Say "Runtime surface passed." "OK"
    exit 0
}

if ($Command -eq "pack") {
    Invoke-Step "Pack compiler" "08_pack_compiler.json" { python -m nexus_gate.build.packer --root . --out dist --json }
    Say "Pack surface passed." "OK"
    exit 0
}

Run-All

if (-not $NoGit) {
    Set-GitQuietLineEndings
}
