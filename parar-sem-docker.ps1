# Encerra o backend e o frontend iniciados por .\iniciar-sem-docker.ps1.
# Os dados continuam salvos em database\ e imports\ — nada é apagado.
# Uso: .\parar-sem-docker.ps1

$RootDir = $PSScriptRoot
$RunDir = Join-Path $RootDir ".run"

function Parar($nome, $arquivoPid) {
    $caminho = Join-Path $RunDir $arquivoPid
    if (Test-Path $caminho) {
        $procId = Get-Content $caminho
        $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
        if ($proc) {
            # Mata também eventuais processos-filho — sem isso, o servidor
            # pode continuar ocupando a porta mesmo após "encerrar" o pai.
            Get-CimInstance Win32_Process -Filter "ParentProcessId = $procId" -ErrorAction SilentlyContinue |
                ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
            Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
            Write-Host "==> $nome encerrado (pid $procId)."
        } else {
            Write-Host "==> $nome já não estava em execução."
        }
        Remove-Item $caminho -ErrorAction SilentlyContinue
    } else {
        Write-Host "==> $nome não estava em execução (nenhum processo iniciado por .\iniciar-sem-docker.ps1 encontrado)."
    }
}

Parar "Backend" "backend.pid"
Parar "Frontend" "frontend.pid"

Write-Host ""
Write-Host "Aplicação encerrada. Seus dados continuam salvos em database\ e imports\." -ForegroundColor Green
Write-Host "  Para iniciar de novo, rode: .\iniciar-sem-docker.ps1"
