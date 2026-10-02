$ErrorActionPreference = "Continue"

Write-Host "=== Paladar Inka IA - Verificacion de entorno ==="

function Show-Version {
    param(
        [string]$Name,
        [scriptblock]$Command
    )
    try {
        $value = & $Command 2>&1
        Write-Host ("{0}: {1}" -f $Name, ($value -join " "))
    }
    catch {
        Write-Host ("{0}: NO DISPONIBLE" -f $Name)
    }
}

Show-Version "Git" { git --version }
Show-Version "Python" { python --version }
Show-Version "Node.js" { node --version }
Show-Version "npm" { npm --version }
Show-Version "PostgreSQL" { psql --version }

Write-Host ""
Write-Host "=== Configuracion Git del integrante ==="
Write-Host ("user.name: {0}" -f (git config --global user.name))
Write-Host ("user.email: {0}" -f (git config --global user.email))
Write-Host ("init.defaultBranch: {0}" -f (git config --global init.defaultBranch))

Write-Host ""
Write-Host "=== Repositorio actual ==="
git status --short --branch
git remote -v

Write-Host ""
Write-Host "Verificacion finalizada."
