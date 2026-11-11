#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

BACKUP_SCRIPT="$SCRIPT_DIR/backup_db.sh"
BACKUP_DIR="/var/backups/smartombor"
LOG_DIR="/var/log/smartombor"
LOG_FILE="$LOG_DIR/backup.log"
CRON_FILE="/etc/cron.d/smartombor-backup"

# Root huquqini tekshirish
if [[ "$EUID" -ne 0 ]]; then
    echo "XATO: Skriptni sudo orqali ishga tushiring."
    exit 1
fi

# Kerakli fayllarni tekshirish
if [[ ! -f "$BACKUP_SCRIPT" ]]; then
    echo "XATO: backup_db.sh topilmadi!"
    exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
    echo "XATO: Docker o'rnatilmagan!"
    exit 1
fi

if ! command -v cron >/dev/null 2>&1; then
    echo "XATO: cron xizmati o'rnatilmagan!"
    echo "Ubuntu/Debian: apt install cron"
    exit 1
fi

# Backup va log papkalarini tayyorlash
install -d -m 700 "$BACKUP_DIR"
install -d -m 700 "$LOG_DIR"

# Cron jadvalini yaratish
TEMP_FILE="$(mktemp)"
trap 'rm -f "$TEMP_FILE"' EXIT

cat > "$TEMP_FILE" <<EOF
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
CRON_TZ=Asia/Tashkent

0 2 * * * root cd "$PROJECT_DIR" && SMARTOMBAR_BACKUP_DIR="$BACKUP_DIR" /bin/bash "$BACKUP_SCRIPT" >> "$LOG_FILE" 2>&1
EOF

install -o root -g root -m 644 "$TEMP_FILE" "$CRON_FILE"

# Cron xizmatini yoqish
systemctl enable --now cron

echo "SmartOmbor avtomatik backup jadvali o'rnatildi."
echo "Vaqt: Har kuni 02:00 (Asia/Tashkent)"
echo "Backup: $BACKUP_DIR"
echo "Log: $LOG_FILE"
