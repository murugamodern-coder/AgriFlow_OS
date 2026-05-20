#!/usr/bin/env bash
# Install daily DB backup + weekly bench backup cron.
set -eu

REPO="${AGRIFLOW_REPO:-$(cd "$(dirname "$0")/../.." && pwd)}"
CRON_USER="${CRON_USER:-$(whoami)}"
MARKER="# agriflow-backup"

(crontab -l 2>/dev/null | grep -v "$MARKER" || true; cat <<EOF
0 2 * * * $REPO/infra/scripts/backup_daily.sh >> /var/log/agriflow-backup.log 2>&1 $MARKER
0 3 * * 0 cd ${BENCH_PATH:-$HOME/workspace/frappe-bench} && bench --site \$(grep FRAPPE_SITE $REPO/infra/docker/.env.staging | cut -d= -f2) backup --with-files >> /var/log/agriflow-backup.log 2>&1 $MARKER
EOF
) | crontab -u "$CRON_USER" -
echo "Cron installed for $CRON_USER"
