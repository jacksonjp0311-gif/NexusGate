param(
  [Parameter(Mandatory=$true)][string]$Command,
  [string]$Name = "reflective-step",
  [int]$MaxRetries = 2
)

$ErrorActionPreference = "Stop"

function Invoke-NexusLocalCommand {
  param([string]$Cmd,[string]$Step)
  $log = Join-Path $env:TEMP ("nexus_reflective_local_" + ($Step -replace '[^a-zA-Z0-9_-]', '_') + ".log")
  & cmd.exe /d /s /c ($Cmd + ' > "' + $log + '" 2>&1')
  $code = $LASTEXITCODE
  return [pscustomobject]@{ ExitCode = $code; LogPath = $log; Command = $Cmd }
}

function Get-NexusSelfHealCommand {
  param([string]$Cmd,[string]$LogPath)
  $text = ""
  if (Test-Path -LiteralPath $LogPath) { $text = Get-Content -LiteralPath $LogPath -Raw -ErrorAction SilentlyContinue }

  $moduleName = ""
  if ($Cmd -match '^python\s+-m\s+unittest\s+tests\.([A-Za-z0-9_]+)$') {
    $moduleName = $Matches[1]
  }

  $isImportWound = (($text -match 'Failed to import test module') -or ($text -match 'No module named') -or ($text -match 'ModuleNotFoundError'))

  if (($moduleName -ne "") -and $isImportWound) {
    return ("python -m unittest discover -s tests -p " + $moduleName + ".py")
  }

  return ""
}

$current = $Command
for ($attempt = 1; $attempt -le $MaxRetries; $attempt++) {
  $result = Invoke-NexusLocalCommand -Cmd $current -Step ($Name + "_attempt_" + $attempt)
  if ($result.ExitCode -eq 0) {
    Write-Host "REFLECTIVE LOCAL LOOP PASS"
    Write-Host ("- command: " + $current)
    Write-Host ("- log: " + $result.LogPath)
    exit 0
  }

  $heal = Get-NexusSelfHealCommand -Cmd $current -LogPath $result.LogPath
  if (($heal -ne "") -and ($attempt -lt $MaxRetries)) {
    Write-Host "REFLECTIVE SELF-HEAL"
    Write-Host ("- from: " + $current)
    Write-Host ("- to: " + $heal)
    $current = $heal
  } else {
    Write-Host "REFLECTIVE LOCAL LOOP BLOCKED"
    Write-Host ("- command: " + $current)
    Write-Host ("- exit_code: " + $result.ExitCode)
    Write-Host ("- log: " + $result.LogPath)
    exit $result.ExitCode
  }
}
