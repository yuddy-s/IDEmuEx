param(
    [string]$Distro = "Ubuntu",
    [Parameter(Mandatory=$true)][string]$WslRepoPath,
    [string]$Destination
)
$ErrorActionPreference = "Stop"
if (-not $WslRepoPath.StartsWith('/')) { throw "WslRepoPath must be an absolute Linux path" }
if (-not $Destination) {
    $desktop = [Environment]::GetFolderPath([Environment+SpecialFolder]::DesktopDirectory)
    if (-not $desktop) { throw "Windows did not report a Desktop directory" }
    $Destination = Join-Path $desktop "IDEmuEx WSL.cmd"
}
$destinationDir = Split-Path -Parent $Destination
if (-not (Test-Path -LiteralPath $destinationDir -PathType Container)) {
    throw "Launcher destination directory does not exist: $destinationDir"
}
$escapedRepo = $WslRepoPath.Replace('"', '""')
$escapedDistro = $Distro.Replace('"', '""')
$body = @"
@echo off
setlocal
start "IDEmuEx browser" powershell.exe -NoProfile -WindowStyle Hidden -Command "for (`$i=0; `$i -lt 120; `$i++) { try { Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8765/api/state -TimeoutSec 1 ^| Out-Null; Start-Process http://127.0.0.1:8765/; exit } catch { Start-Sleep -Milliseconds 500 } }"
wsl.exe -d "$escapedDistro" --cd "$escapedRepo" -- python3 -m idemu gui --no-browser
endlocal
"@
[IO.File]::WriteAllText($Destination, $body, [Text.UTF8Encoding]::new($false))
Write-Host "Launcher installed at $Destination"
