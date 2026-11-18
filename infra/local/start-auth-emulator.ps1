# Starts the Firebase Auth Emulator for local development and keeps its accounts between runs.
# Usage (from nexora_main): powershell -ExecutionPolicy Bypass -File infra/local/start-auth-emulator.ps1
$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..\..')
$data = '.emulator-data'
$cliArgs = @('-y', 'firebase-tools@13.35.1', 'emulators:start', '--only', 'auth', '--project', 'demo-nexora',
             "--export-on-exit=$data")
if (Test-Path (Join-Path $data 'firebase-export-metadata.json')) { $cliArgs += "--import=$data" }
npx @cliArgs
