param(
    [string]$Issue = "Inspect the current NEXUS failure and recommend a bounded repair.",
    [switch]$CallModel,
    [switch]$AutoYesForTests
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Write-NG {
    param([string]$Message)
    Write-Host ("[NEXUS-REFLECT] {0}" -f $Message)
}

function Show-ReportSummary {
    $report = Join-Path $Root "reports\nexus_nn_router_report_latest.json"
    if (Test-Path -LiteralPath $report -PathType Leaf) {
        $json = Get-Content -LiteralPath $report -Raw | ConvertFrom-Json
        Write-NG ("role={0} call_model={1}" -f $json.target_role, ($json.model_responses.Count -gt 0))
        foreach ($response in @($json.model_responses)) {
            Write-Host ""
            Write-Host ("--- {0} / {1} / ok={2} ---" -f $response.role, $response.model, $response.ok)
            $text = [string]($response.response)
            if ([string]::IsNullOrWhiteSpace($text)) { $text = [string]($response.error) }
            if ($text.Length -gt 1200) { $text = $text.Substring(0, 1200) + " ..." }
            Write-Host $text
        }
    }
}

Write-NG "Preparing DEEP recommendation packet."
$args = @("-ExecutionPolicy", "Bypass", "-File", ".\scripts\nexus.ps1", "deep", "-Tag", $Issue)
if ($CallModel.IsPresent) {
    $args += "-CallModel"
}

powershell @args
if ($LASTEXITCODE -ne 0) {
    throw "NEXUS DEEP recommendation failed."
}

Show-ReportSummary

Write-Host ""
Write-Host "NEXUS recommendation boundary:"
Write-Host "model = recommendation only"
Write-Host "repair = human-authorized only"
Write-Host ""

if ($AutoYesForTests.IsPresent) {
    Write-NG "AutoYesForTests selected; no repair action is executed by this harness."
    exit 0
}

$answer = Read-Host "Apply the bounded repair section that the current script already contains? [y/N]"
if ($answer -eq "Y" -or $answer -eq "y") {
    Write-NG "Human approved. Continue with the caller's bounded repair section."
    exit 0
}

Write-NG "Human declined. Stop before mutation."
exit 2
