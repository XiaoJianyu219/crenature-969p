<#
.SYNOPSIS
  Register the scheduled task that the Raspberry Pi starts over SSH.

.DESCRIPTION
  A program launched directly through SSH runs in a non-interactive session
  and its window never reaches the screen. Running it as a scheduled task
  with an interactive logon puts the full-screen window on the desktop of
  the logged-in user instead.

  MultipleInstances = IgnoreNew: while an animation is still playing, new
  triggers are ignored instead of stacking windows.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File windows\register_task.ps1
  powershell -ExecutionPolicy Bypass -File windows\register_task.ps1 -TaskName crenature -AtLogOn
#>
param(
    [string]$TaskName = "crenature",
    [string]$User = "$env:USERDOMAIN\$env:USERNAME",
    [switch]$AtLogOn  # also play once when the user logs on
)

$bat = Join-Path $PSScriptRoot "run_crenature.bat"
if (-not (Test-Path $bat)) { throw "not found: $bat" }

$action = New-ScheduledTaskAction -Execute $bat -WorkingDirectory (Split-Path $PSScriptRoot -Parent)
$principal = New-ScheduledTaskPrincipal -UserId $User -LogonType Interactive
$settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 10)

$params = @{
    TaskName  = $TaskName
    Action    = $action
    Principal = $principal
    Settings  = $settings
    Force     = $true
}
if ($AtLogOn) { $params.Trigger = New-ScheduledTaskTrigger -AtLogOn -User $User }

Register-ScheduledTask @params | Out-Null
Write-Host "Registered task '$TaskName' for $User."
Write-Host "Test it locally with:  schtasks /run /tn `"$TaskName`""
