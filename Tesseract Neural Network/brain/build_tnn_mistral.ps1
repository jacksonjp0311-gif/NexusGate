param(
  [string]$ModelName = "tnn-mistral:latest"
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Modelfile = Join-Path $Root "brain\Modelfile.tnn-mistral"

Write-Host "TNN Mistral adapter build"
Write-Host "- model: $ModelName"
Write-Host "- modelfile: $Modelfile"

ollama --version | Out-Host
ollama create $ModelName -f $Modelfile
if ($LASTEXITCODE -ne 0) {
  throw "ollama create failed"
}

Write-Host "TNN Mistral adapter ready: $ModelName"
