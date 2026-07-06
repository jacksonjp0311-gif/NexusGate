Write-Output "Mutation demo payload."
Write-Output "This payload is intentionally not executed by the mock runner."
Set-Content -Path ".\should_not_run.txt" -Value "If this exists, mock runner boundaries failed."
