#!/usr/bin/env bash
# Obtain Let's Encrypt certs and install for nginx compose.
set -eu

DOMAIN="${STAGING_DOMAIN:?Set STAGING_DOMAIN}"
EMAIL="${CERTBOT_EMAIL:-admin@$DOMAIN}"
DOCKER_DIR="$(cd "$(dirname "$0")/../docker" && pwd)"
CERT_DIR="$DOCKER_DIR/nginx/certs"

mkdir -p "$CERT_DIR" /var/www/certbot

# Stop nginx briefly if using standalone (alternative: webroot with nginx running)
if docker compose -f "$DOCKER_DIR/docker-compose.staging.yml" --env-file "$DOCKER_DIR/.env.staging" ps nginx 2>/dev/null | grep -q Up; then
  docker compose -f "$DOCKER_DIR/docker-compose.staging.yml" --env-file "$DOCKER_DIR/.env.staging" stop nginx || true
fi

certbot certonly --standalone -d "$DOMAIN" --email "$EMAIL" --agree-tos --non-interactive || {
  echo "Certbot failed — use DNS challenge or fix port 80 availability"
  exit 1
}

cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$CERT_DIR/fullchain.pem"
cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$CERT_DIR/privkey.pem"
chmod 644 "$CERT_DIR/fullchain.pem"
chmod 600 "$CERT_DIR/privkey.pem"

# Patch nginx server_name
sed -i "s|server_name .*;|server_name $DOMAIN;|g" "$DOCKER_DIR/nginx/agriflow-staging-vps.conf"

docker compose -f "$DOCKER_DIR/docker-compose.staging.yml" --env-file "$DOCKER_DIR/.env.staging" up -d nginx
echo "TLS ready for https://$DOMAIN"
