#!/bin/bash
# AgriFlow OS - Production Deployment Script
# Run on production server after initial setup

set -e

echo "================================================"
echo "  AgriFlow OS Production Deployment"
echo "================================================"

# Variables
SITE_NAME="agriflow.yourcompany.com"
BENCH_DIR="/home/agriflow/frappe-bench"
REPO_URL="https://github.com/murugamodern-coder/AgriFlow_OS.git"
BRANCH="stabilization-v1"

# Pre-flight check
echo "[1/8] Pre-flight checks..."
if [ ! -d "$BENCH_DIR" ]; then
    echo "❌ Bench directory not found: $BENCH_DIR"
    exit 1
fi

# Pull latest code
echo "[2/8] Pulling latest code..."
cd $BENCH_DIR/apps/agriflow
git fetch origin
git checkout $BRANCH
git pull origin $BRANCH

# Backup before deploy
echo "[3/8] Creating pre-deployment backup..."
cd $BENCH_DIR
./env/bin/bench --site $SITE_NAME backup --with-files

# Install/update dependencies
echo "[4/8] Updating dependencies..."
./env/bin/bench setup requirements

# Migrate
echo "[5/8] Running migrations..."
./env/bin/bench --site $SITE_NAME migrate

# Build assets
echo "[6/8] Building assets..."
./env/bin/bench build --app agriflow

# Clear cache
echo "[7/8] Clearing cache..."
./env/bin/bench --site $SITE_NAME clear-cache
./env/bin/bench --site $SITE_NAME clear-website-cache

# Restart services
echo "[8/8] Restarting services..."
sudo supervisorctl restart agriflow-frappe-web
sudo supervisorctl restart agriflow-frappe-worker
sudo supervisorctl restart agriflow-frappe-schedule
sudo systemctl reload nginx

# Verify
echo "================================================"
echo "✅ Deployment complete!"
echo "Verifying..."
sleep 5
HEALTH=$(curl -s https://$SITE_NAME/api/method/ping | grep -o "pong")
if [ "$HEALTH" = "pong" ]; then
    echo "✅ Health check passed!"
    echo "================================================"
else
    echo "❌ Health check failed!"
    echo "Check logs: tail -f $BENCH_DIR/logs/web.error.log"
    exit 1
fi