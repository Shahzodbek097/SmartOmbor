#!/usr/bin/env bash

set -Eeuo pipefail
umask 077

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_DIR"

BACKUP_DIR="${SMARTOMBAR_BACKUP_DIR:-/var/backups/smartombor}"

COMPOSE=(
    docker compose
    -f compose.yaml
    -f compose.prod.yaml
)

# Argumentlarni tekshirish
if [[ $# -ne 3 || "$3" != "--confirm" ]]; then
    echo "Foydalanish:"
    echo "bash scripts/restore_db.sh DB.dump MEDIA.tar.gz --confirm"
    exit 1
fi

DB_BACKUP="$1"
MEDIA_BACKUP="$2"

# Backup fayllarini tekshirish
[[ -f "$DB_BACKUP" ]] || {
    echo "XATO: Database backup topilmadi!"
    exit 1
}

[[ -f "$MEDIA_BACKUP" ]] || {
    echo "XATO: Media backup topilmadi!"
    exit 1
}

echo "Backup fayllari tekshirilmoqda..."

gzip -t "$MEDIA_BACKUP"

"${COMPOSE[@]}" exec -T db \
    pg_restore --list < "$DB_BACKUP" > /dev/null

echo "Backup fayllari yaroqli."

echo "DIQQAT: Mavjud ma'lumotlar almashtiriladi!"
read -r -p "Davom etish uchun RESTORE deb yozing: " ANSWER

if [[ "$ANSWER" != "RESTORE" ]]; then
    echo "Tiklash bekor qilindi."
    exit 0
fi

restart_services() {
    "${COMPOSE[@]}" start web celery_worker celery_beat || true
}

trap restart_services EXIT

# Ilova xizmatlarini vaqtincha to'xtatish
echo "Web va Celery xizmatlari to'xtatilmoqda..."

"${COMPOSE[@]}" stop web celery_worker celery_beat

# PostgreSQL bazasini tiklash
echo "Database tiklanmoqda..."

"${COMPOSE[@]}" exec -T db sh -c \
    'pg_restore --clean --if-exists --no-owner --no-privileges --exit-on-error -U "$POSTGRES_USER" -d "$POSTGRES_DB" -' \
    < "$DB_BACKUP"

# Media arxivini tekshirish
echo "Media fayllari tiklanmoqda..."

tar -tzf "$MEDIA_BACKUP" | awk '
{
    if ($0 !~ /^media(\/|$)/ || $0 ~ /(^|\/)\.\.(\/|$)/) {
        print "XATO: Arxiv ichida ruxsat etilmagan yo'l: " $0
        exit 1
    }
}
'

# Media papkasini tiklash
"${COMPOSE[@]}" run --rm --no-deps \
    --entrypoint sh web -c \
    'mkdir -p /app/media && find /app/media -mindepth 1 -maxdepth 1 -exec rm -rf -- {} + && tar -xzf - -C /app' \
    < "$MEDIA_BACKUP"

echo "Database va Media tiklandi."
echo "Xizmatlar qayta ishga tushirilmoqda..."
