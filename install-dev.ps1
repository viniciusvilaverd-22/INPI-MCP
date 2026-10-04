$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

Write-Host 'INPI-MCP DEV bootstrap'

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  throw 'Python nao encontrado no PATH.'
}

if (-not (Test-Path '.venv')) {
  python -m venv .venv
}

$Py = Join-Path $Root '.venv\Scripts\python.exe'
& $Py -m pip install --upgrade pip
& $Py -m pip install -e '.[test,mcp]'
& $Py -m pytest -q

if (Get-Command docker -ErrorAction SilentlyContinue) {
  docker compose up -d --build
  Write-Host 'Docker Compose iniciado.'
} else {
  Write-Warning 'Docker nao encontrado; testes Python foram executados, mas PostgreSQL/API container nao foram iniciados.'
}
