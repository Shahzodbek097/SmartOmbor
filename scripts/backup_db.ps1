
$ErrorActionPreference = "Stop"

# Loyiha papkasi
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

# Backup papkasi
$BackupDirectory = Join-Path $ProjectRoot "backups"

if (!(Test-Path $BackupDirectory)) {
    New-Item -ItemType Directory -Path $BackupDirectory | Out-Null
}

# Fayl nomi
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupName = "smartombor_$Timestamp.dump"

$ContainerPath = "/tmp/smartombor_backup.dump"
$LocalPath = Join-Path $BackupDirectory $BackupName

try {
    Write-Host "PostgreSQL tekshirilmoqda..." -ForegroundColor Cyan

    docker compose exec -T db pg_isready

    if ($LASTEXITCODE -ne 0) {
        throw "PostgreSQL ishlamayapti!"
    }

    Write-Host "Backup yaratilmoqda..." -ForegroundColor Cyan

    docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc -f /tmp/smartombor_backup.dump'

    if ($LASTEXITCODE -ne 0) {
        throw "Backup yaratishda xatolik!"
    }

    docker compose cp db:/tmp/smartombor_backup.dump $LocalPath

    if ($LASTEXITCODE -ne 0) {
        throw "Backup nusxasini ko'chirishda xatolik!"
    }

    $BackupFile = Get-Item $LocalPath

    if ($BackupFile.Length -eq 0) {
        throw "Backup fayli bo'sh!"
    }

    Write-Host "Backup muvaffaqiyatli yaratildi!" -ForegroundColor Green

    # 7 kundan eski backup'larni o'chirish
    $CutoffDate = (Get-Date).AddDays(-7)

    $OldBackups = Get-ChildItem `
        -Path $BackupDirectory `
        -Filter "smartombor_*.dump" `
        -File |
        Where-Object {
            $_.LastWriteTime -lt $CutoffDate
        }

    foreach ($file in $OldBackups) {
        Remove-Item $file.FullName -Force
        Write-Host "Eski backup o'chirildi: $($file.Name)"
    }

    Write-Host "Fayl: $($BackupFile.FullName)"
    Write-Host "Hajmi: $([math]::Round($BackupFile.Length / 1MB, 2)) MB"
}
finally {
    docker compose exec -T db rm -f $ContainerPath 2>$null
}
