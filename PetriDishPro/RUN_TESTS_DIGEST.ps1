# PETRI 004W STRICT CONTRACT MARKER
# Static contract literal: -Strict
# Runtime meaning: pass -Strict to return the unit-test exit code instead of always returning 0 after digest emission.
param(
    [switch]$Strict
)

$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Repo

$Reports = Join-Path $Repo "reports\bio"
New-Item -ItemType Directory -Force -Path $Reports | Out-Null

$Stdout = Join-Path $Reports "unit_stdout_latest.txt"
$Stderr = Join-Path $Reports "unit_stderr_latest.txt"
$OutJson = Join-Path $Reports "failure_digest_latest.json"
$OutMd = Join-Path $Reports "failure_digest_latest.md"

Write-Host "[PETRI DIGEST] Running unit tests with compressed failure output..." -ForegroundColor Cyan

# CMD redirection seal:
# Python unittest writes progress/failure text to stderr by design.
# Running through cmd.exe keeps stderr redirected to the raw log and prevents
# PowerShell from turning it into a terminating NativeCommandError.
$cmdLine = 'python -m unittest discover -s tests 1> "' + $Stdout + '" 2> "' + $Stderr + '"'
& cmd.exe /d /c $cmdLine
$Code = $LASTEXITCODE

& python ".\tools\petri_failure_digest.py" --stdout $Stdout --stderr $Stderr --out-json $OutJson --out-md $OutMd --print

Write-Host "[PETRI DIGEST] Raw stdout: $Stdout" -ForegroundColor DarkGray
Write-Host "[PETRI DIGEST] Raw stderr: $Stderr" -ForegroundColor DarkGray
Write-Host "[PETRI DIGEST] Digest md:  $OutMd" -ForegroundColor DarkGray
Write-Host "[PETRI DIGEST] Digest json:$OutJson" -ForegroundColor DarkGray

if ($Strict -and $Code -ne 0) {
    exit $Code
}
exit 0
