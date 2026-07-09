
# PETRI 005I PRESET CARD MIRROR
function Show-PetriPresetCardMirror {
    $Mirror = Join-Path $PSScriptRoot "reports\bio\preset_card_mirror.txt"
    Write-Host ""
    Write-Host "  PRESET CARD MIRROR" -ForegroundColor Cyan
    Write-Host "  ------------------" -ForegroundColor Cyan
    if (Test-Path $Mirror) {
        Get-Content $Mirror | Select-Object -First 18 | ForEach-Object { Write-Host ("  " + $_) }
    } else {
        Write-Host "  mirror not generated yet"
    }
    Write-Host ""
}

# PETRI 004O ENTRY CARD MIRROR WRAPPER
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Core = Join-Path $Root "ORGANISM_GATE_CORE_004O.ps1"

function Show-PetriCardMirror {
    $presetPath = Join-Path $Root "config\preset_cards.json"
    $organismPath = Join-Path $Root "config\organisms.json"
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "        ORGANISM GATE CARD MIRROR  //  PRESET-AWARE" -ForegroundColor Cyan
    Write-Host "================================================================" -ForegroundColor Cyan
    if ((Test-Path $presetPath) -and (Test-Path $organismPath)) {
        try {
            $presetCfg = Get-Content $presetPath -Raw | ConvertFrom-Json
            $orgCfg = Get-Content $organismPath -Raw | ConvertFrom-Json
            Write-Host "registry schema: $($presetCfg.schema)" -ForegroundColor DarkCyan
            Write-Host "organisms:" -ForegroundColor Yellow
            foreach ($o in $orgCfg.organisms) {
                $state = if ($o.enabled) { "ON " } else { "OFF" }
                Write-Host ("  [{0}] {1} // {2}" -f $state, $o.label, $o.dataset.primary) -ForegroundColor White
            }
            Write-Host ""
            Write-Host "presets:" -ForegroundColor Yellow
            foreach ($p in $presetCfg.presets.PSObject.Properties) {
                $v = $p.Value
                $metrics = ($v.sections.metric_cards -join ", ")
                $interventions = ($v.sections.intervention_cards -join ", ")
                Write-Host ("  > {0}" -f $v.label) -ForegroundColor Green
                Write-Host ("    metrics: {0}" -f $metrics) -ForegroundColor DarkGray
                Write-Host ("    cards:   {0}" -f $interventions) -ForegroundColor DarkGray
            }
            Write-Host ""
            Write-Host "mirror rule: add cards to config/preset_cards.json and both entry + Electron adapt." -ForegroundColor Cyan
        } catch {
            Write-Host "Card mirror read failed: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "Card mirror pending: config/preset_cards.json or config/organisms.json missing." -ForegroundColor Yellow
    }
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""
}

Show-PetriCardMirror
if (Test-Path $Core) {
    & $Core
} else {
    Write-Host "Missing core menu: $Core" -ForegroundColor Red
}

# PETRI 004P ENTRY CARD MIRROR
#
#   ---------------- CARD MIRROR ----------------
#   PETRI 004P ENTRY CARD MIRROR
#   Presets: microbial competition | antibiotic selection | tissue interaction | drug response | antibody binding
#   Organism Cards: registry sourced; selected cards drive dish membership
#   Metric Cards: stacked metrics + charts + emergent conditions
#   Data Gates: ChEMBL / EUCAST / CLSI / RCSB / BacDive / BioCyc / SGD provenance required for real-data mode
#   Claim Boundary: simulation only; no clinical/wet-lab/biosafety claims
#   ---------------------------------------------
#
