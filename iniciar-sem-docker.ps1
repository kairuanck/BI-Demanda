# Alternativa a ./iniciar.sh para Windows sem Docker e sem Git (ex.: sem
# perfil de administrador para instalar nenhum dos dois). Só precisa do
# PowerShell, que já vem com o Windows, e de Python 3.12 + Node.js
# instalados (ver PRIMEIRO_USO.md, seção "Alternativa para Windows sem
# administrador").
#
# Uso: abra o PowerShell na pasta do projeto e rode:
#   .\iniciar-sem-docker.ps1
# Se aparecer erro sobre "execução de scripts desabilitada", rode antes
# (uma única vez, não precisa de administrador):
#   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force

$ErrorActionPreference = "Stop"
$RootDir = $PSScriptRoot
Set-Location $RootDir
$RunDir = Join-Path $RootDir ".run"
New-Item -ItemType Directory -Force -Path $RunDir | Out-Null

function Info($msg) { Write-Host "==> $msg" -ForegroundColor Cyan }
function Ok($msg) { Write-Host $msg -ForegroundColor Green }
function Falha($msg) { Write-Host $msg -ForegroundColor Red }

# ------------------------------------------------------------------ checagens

Info "Verificando se o Python está instalado..."
# Aceita 3.12 ou mais novo (o projeto não tem limite superior: pyproject.toml
# declara "requires-python = >=3.12") — versões futuras do Python (3.13, 3.14...)
# não devem ser recusadas só por não serem exatamente "3.12".
$pythonCmd = $null
foreach ($cand in @("python", "py")) {
    $existe = Get-Command $cand -ErrorAction SilentlyContinue
    if ($existe) {
        $versao = (& $cand --version 2>&1 | Out-String)
        if ($versao -match "Python (\d+)\.(\d+)") {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            if ($major -eq 3 -and $minor -ge 12) {
                $pythonCmd = $cand
                break
            }
        }
    }
}
if (-not $pythonCmd) {
    Falha "Não encontrei o Python 3.12 (ou mais novo) instalado."
    Write-Host "Baixe em https://www.python.org/downloads/ (escolha a versão 3.12 ou mais recente)."
    Write-Host "Se você não tem permissão de administrador, use 'Customize installation'"
    Write-Host "e desmarque 'Install for all users' — instala só para o seu usuário."
    exit 1
}

Info "Verificando se o Node.js está instalado..."
if (-not (Get-Command node -ErrorAction SilentlyContinue) -or -not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Falha "Não encontrei o Node.js instalado."
    Write-Host "Baixe a versão 'LTS' em https://nodejs.org/"
    Write-Host "Sem permissão de administrador: baixe o '.zip' (Windows Binary), extraia"
    Write-Host "numa pasta sua (ex.: C:\Users\seu-usuario\node) e adicione essa pasta ao"
    Write-Host "PATH em 'Editar variáveis de ambiente da sua conta' (não precisa de admin)."
    exit 1
}

# ------------------------------------------------------------------ backend

Info "Preparando o backend (pode levar alguns minutos na primeira vez)..."
Set-Location (Join-Path $RootDir "backend")
$venvPython = Join-Path $RootDir "backend\.venv\Scripts\python.exe"

# Um .venv criado num caminho e depois movido/renomeado (comum quando a pasta
# do projeto é extraída de novo ou renomeada manualmente) fica com caminhos
# absolutos quebrados gravados nos executáveis (uvicorn.exe etc.) — o Python
# em si ainda roda, mas os scripts instalados (uvicorn) falham silenciosamente.
# Detecta isso e recria o ambiente do zero em vez de deixar o usuário preso
# num erro sem explicação.
if (Test-Path ".venv") {
    & $venvPython --version *> $null
    if ($LASTEXITCODE -ne 0) {
        Info "Ambiente Python existente parece quebrado (pasta foi movida/renomeada?). Recriando..."
        Remove-Item -Recurse -Force ".venv"
    }
}
if (-not (Test-Path ".venv")) {
    & $pythonCmd -m venv .venv
}
& $venvPython -m pip install --upgrade pip -q
& $venvPython -m pip install -e ".[dev]" -q
if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env" }

Info "Aplicando migrações e dados de referência..."
& $venvPython -m alembic upgrade head
& $venvPython -m app.infrastructure.seeds.seed_ufs
& $venvPython -m app.infrastructure.seeds.seed_tipos_promotor

Info "Iniciando o backend em segundo plano..."
$venvUvicorn = Join-Path $RootDir "backend\.venv\Scripts\uvicorn.exe"
$backendLog = Join-Path $RunDir "backend.log"
$backendErr = Join-Path $RunDir "backend-err.log"
$backendProc = Start-Process -FilePath $venvUvicorn `
    -ArgumentList @("app.main:app", "--host", "0.0.0.0", "--port", "8000") `
    -WorkingDirectory (Join-Path $RootDir "backend") `
    -RedirectStandardOutput $backendLog -RedirectStandardError $backendErr `
    -WindowStyle Hidden -PassThru
$backendProc.Id | Out-File -FilePath (Join-Path $RunDir "backend.pid") -Encoding ascii

$backendOk = $false
for ($i = 0; $i -lt 60; $i++) {
    try {
        $resp = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/health" -UseBasicParsing -TimeoutSec 2
        if ($resp.StatusCode -eq 200) { $backendOk = $true; break }
    } catch {}
    Start-Sleep -Seconds 2
}
if (-not $backendOk) {
    Falha "O backend demorou demais para responder."
    Write-Host "Últimas linhas de log, para diagnóstico:"
    Get-Content $backendLog -Tail 50 -ErrorAction SilentlyContinue
    Get-Content $backendErr -Tail 50 -ErrorAction SilentlyContinue
    exit 1
}

# ------------------------------------------------------------------ frontend

Set-Location (Join-Path $RootDir "frontend")
Info "Preparando o frontend (pode levar alguns minutos na primeira vez)..."
if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env" }

# Instalações de Node.js via ".zip" portátil (comuns em máquinas sem admin,
# ver PRIMEIRO_USO.md) mantêm a marca de "baixado da internet" nos wrappers
# .ps1 (npm.ps1, npx.ps1) depois de extraídos — o PowerShell recusa executá-los
# sem isso, mesmo com a política de execução liberada para o usuário atual.
$npmCmd = Get-Command npm -ErrorAction SilentlyContinue
if ($npmCmd) {
    $nodeDir = Split-Path $npmCmd.Source -Parent
    Get-ChildItem -Path $nodeDir -Filter "*.ps1" -ErrorAction SilentlyContinue |
        Unblock-File -ErrorAction SilentlyContinue
}

if (-not (Test-Path "node_modules")) {
    npm install
}

Info "Iniciando o frontend em segundo plano..."
$viteJs = Join-Path $RootDir "frontend\node_modules\vite\bin\vite.js"
$frontendLog = Join-Path $RunDir "frontend.log"
$frontendErr = Join-Path $RunDir "frontend-err.log"
$frontendProc = Start-Process -FilePath "node" `
    -ArgumentList @("`"$viteJs`"", "--host", "0.0.0.0", "--port", "5173") `
    -WorkingDirectory (Join-Path $RootDir "frontend") `
    -RedirectStandardOutput $frontendLog -RedirectStandardError $frontendErr `
    -WindowStyle Hidden -PassThru
$frontendProc.Id | Out-File -FilePath (Join-Path $RunDir "frontend.pid") -Encoding ascii

$frontendOk = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5173" -UseBasicParsing -TimeoutSec 2
        if ($resp.StatusCode -eq 200) { $frontendOk = $true; break }
    } catch {}
    Start-Sleep -Seconds 2
}
if (-not $frontendOk) {
    Falha "O frontend demorou demais para responder."
    Write-Host "Últimas linhas de log, para diagnóstico:"
    Get-Content $frontendLog -Tail 50 -ErrorAction SilentlyContinue
    Get-Content $frontendErr -Tail 50 -ErrorAction SilentlyContinue
    exit 1
}

Write-Host ""
Ok "Promotores BI está no ar (sem Docker)!"
Write-Host ""
Write-Host "  Acesse no navegador: http://localhost:5173"
Write-Host ""
Write-Host "  Para importar planilhas, entre no menu 'Importações'."
Write-Host "  Para encerrar a aplicação, rode: .\parar-sem-docker.ps1"
