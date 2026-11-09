
#!/usr/bin/env bash

set -Eeuo pipefail

# Loyiha joylashgan asosiy papka
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_DIR"

# Docker Compose buyruqlari
COMPOSE=(
    docker compose
    -f compose.yaml
    -f compose.prod.yaml
)

# Backup papkasi
BACKUP_DIR="$PROJECT_DIR/backups"
mkdir -p "$BACKUP_DIR"

# Backup fayli nomi
TIMESTAMP="$(date -u +'%Y%m%d_%H%M%S_UTC')"
BACKUP_FILE="$BACKUP_DIR/smartombor_$TIMESTAMP.dump"
TEMP_FILE="$BACKUP_FILE.tmp"

cleanup() {
    rm -f "$TEMP_FILE"
}

trap cleanup EXIT

echo "PostgreSQL tekshirilmoqda..."

"${COMPOSE[@]}" exec -T db pg_isready

echo "Backup yaratilmoqda..."

"${COMPOSE[@]}" exec -T db sh -c \
    'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' \
    > "$TEMP_FILE"

# Backup bo'sh emasligini tekshirish
if [[ ! -s "$TEMP_FILE" ]]; then
    echo "XATO: Backup fayli bo'sh!"
    exit 1
fi

# Tayyor faylni saqlash
mv "$TEMP_FILE" "$BACKUP_FILE"

echo "Backup muvaffaqiyatli yaratildi!"
echo "Fayl: $BACKUP_FILE"

# 7 kundan eski backup'larni o'chirish
find "$BACKUP_DIR" \
    -maxdepth 1 \
    -type f \
    -name 'smartombor_*.dump' \
    -mtime +7 \
    -print \
    -delete

echo "Backup jarayoni yakunlandi!"
