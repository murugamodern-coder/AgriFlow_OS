#!/usr/bin/env bash
# Obtain Let's Encrypt certs for staging.agriflow.local (requires real DNS → host).
# Usage: sudo ./certbot_staging.sh staging.agriflow.yourdomain.org
set -eu

DOMAIN="${1:?Usage: certbot_staging.sh <domain>}"
CERT_DIR="$(cd "$(dirname "$0")/../docker/nginx/certs" && pwd)"

sudo certbot certonly --standalone -d "$DOMAIN" --agree-tos -m ops@agriflow.local --non-interactive

sudo cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$CERT_DIR/fullchain.pem"
sudo cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$CERT_DIR/privkey.pem"
echo "Certs copied to $CERT_DIR — restart nginx compose"
