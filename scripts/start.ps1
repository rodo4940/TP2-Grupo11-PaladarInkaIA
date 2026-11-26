# Primer inicio en Windows PowerShell 5.1+; usar exclusivamente en entorno local demo.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

function Assert-Docker {
    & docker compose version | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Instala Docker Desktop con Compose v2.' }
    & docker info | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Abre Docker Desktop y habilita el motor Docker.' }
}
function New-Hex([int]$Bytes) {
    $buffer = New-Object byte[] $Bytes
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try { $rng.GetBytes($buffer) } finally { $rng.Dispose() }
    return [BitConverter]::ToString($buffer).Replace('-', '').ToLowerInvariant()
}
Assert-Docker
if (-not (Test-Path '.env')) {
    $source = [IO.File]::ReadAllText((Join-Path $root '.env.example'))
    $source = [regex]::Replace($source, '(?m)^DATABASE_PASSWORD=.*$', ('DATABASE_PASSWORD=' + (New-Hex 24)))
    $source = [regex]::Replace($source, '(?m)^JWT_SECRET=.*$', ('JWT_SECRET=' + (New-Hex 48)))
    $source = [regex]::Replace($source, '(?m)^SEED_ADMIN_PASSWORD=.*$', ('SEED_ADMIN_PASSWORD=' + (New-Hex 18)))
    [IO.File]::WriteAllText((Join-Path $root '.env'), $source, (New-Object System.Text.UTF8Encoding($false)))
    Write-Host 'Creado .env con contraseñas aleatorias. No lo subas a Git.'
} else {
    Write-Host 'Se mantiene .env existente. No se modificarán contraseñas.'
}
if ((Get-Content '.env' -Raw) -match '(?m)^APP_ENV=production\s*$') {
    throw 'Esta instalación es solo de demostración. Prohibido con APP_ENV=production.'
}
Write-Host '[1/4] Levantando Docker Compose...'
& docker compose up --build -d
if ($LASTEXITCODE -ne 0) { throw 'Error al construir o iniciar contenedores.' }
Write-Host '[2/4] Comprobando API y PostgreSQL...'
$ready = $false
for ($i=0; $i -lt 45; $i++) {
    & docker compose exec -T backend python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/ready',timeout=3)" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) { $ready = $true; break }
    Start-Sleep -Seconds 2
}
if (-not $ready) { throw 'API no lista. Ejecuta docker compose logs --tail=100 backend db.' }
Write-Host '[3/4] Instalando usuarios y datos ficticios (idempotente)...'
& docker compose exec -T backend python -m app.seed
if ($LASTEXITCODE -ne 0) { throw 'Falló la carga de datos ficticios.' }
Write-Host '[4/4] Verificando React...'
$ready = $false
for ($i=0; $i -lt 30; $i++) {
    & docker compose exec -T frontend node -e "fetch('http://127.0.0.1:5173').then(r=>{if(!r.ok)process.exit(1)}).catch(()=>process.exit(1))" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) { $ready = $true; break }
    Start-Sleep -Seconds 2
}
if (-not $ready) { throw 'La pantalla React no está disponible. Ejecuta docker compose logs --tail=100 frontend.' }
Write-Host ''
Write-Host 'INSTALACIÓN DEMO COMPLETADA'
Write-Host 'Interfaz: http://localhost:5173'
Write-Host 'Swagger:  http://localhost:8000/docs'
Write-Host 'Usuarios: admin, cajero y cocina'
Write-Host 'Contraseña: revisa SEED_ADMIN_PASSWORD en tu .env local (no compartas ese archivo).'
Write-Host 'Para apagar sin borrar datos: docker compose down'
Write-Host 'AVISO: no equivale a producción ni factura electrónica SUNAT.'