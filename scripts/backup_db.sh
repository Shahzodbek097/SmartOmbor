#!/usr/bin/env bash

set -Eeuo pipefail
umask 077

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_DIR"

BACKUP_DIR="${SMARTOMBAR_BACKUP_DIR:-/var/backups/smartombor}"

mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"

COMPOSE=(
    docker compose
    -f compose.yaml
    -f compose.prod.yaml
)

TIMESTAMP="$(date -u +'%Y%m%d_%H%M%S_UTC')"

DB_BACKUP="$BACKUP_DIR/smartombor_$TIMESTAMP.dump"
DB_TEMP="$DB_BACKUP.tmp"

MEDIA_BACKUP="$BACKUP_DIR/smartombor_media_$TIMESTAMP.tar.gz"
MEDIA_TEMP="$MEDIA_BACKUP.tmp"

cleanup() {
    rm -f "$DB_TEMP" "$MEDIA_TEMP"
}

trap cleanup EXIT

# 1. PostgreSQL tekshirish
echo "PostgreSQL tekshirilmoqda..."

"${COMPOSE[@]}" exec -T db pg_isready

# 2. Database backup
echo "PostgreSQL backup olinmoqda..."

"${COMPOSE[@]}" exec -T db sh -c \
    'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' \
    > "$DB_TEMP"

if [[ ! -s "$DB_TEMP" ]]; then
    echo "XATO: Database backup bo'sh!"
    exit 1
fi

# 3. Media fayllar backup
echo "Media fayllar backup olinmoqda..."

"${COMPOSE[@]}" exec -T web python -c \
    'import sys,tarfile; a=tarfile.open(fileobj=sys.stdout.buffer, mode="w|gz"); a.add("/app/media", arcname="media"); a.close()' \
    > "$MEDIA_TEMP"

if [[ ! -s "$MEDIA_TEMP" ]]; then
    echo "XATO: Media backup bo'sh!"
    exit 1
fi

# 4. Media arxivini tekshirish
gzip -t "$MEDIA_TEMP"

# 5. Tayyor backup fayllarini saqlash
mv "$DB_TEMP" "$DB_BACKUP"
mv "$MEDIA_TEMP" "$MEDIA_BACKUP"

chmod 600 "$DB_BACKUP" "$MEDIA_BACKUP"

echo "Ikkala backup muvaffaqiyatli yaratildi!"
echo "Database: $DB_BACKUP"
echo "Media: $MEDIA_BACKUP"

# 6. 7 kundan eski backup fayllarini tozalash
find "$BACKUP_DIR" \
    -maxdepth 1 \
    -type f \
    \( -name 'smartombor_*.dump' -o -name 'smartombor_media_*.tar.gz' \) \
    -mtime +7 \
    -print \
    -delete

echo "Backup jarayoni yakunlandi!"
