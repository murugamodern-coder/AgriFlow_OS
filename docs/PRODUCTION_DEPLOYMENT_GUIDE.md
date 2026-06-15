# AgriFlow OS - Production Deployment Guide

## 🎯 Target Server Specs

### Option 1: Hetzner CX21 (Recommended)
- 2 vCPU, 4 GB RAM, 40 GB SSD
- €5.83/month (~₹525/month)
- Location: Helsinki/Nuremberg/Frankfurt

### Option 2: DigitalOcean Droplet
- 2 vCPU, 4 GB RAM, 80 GB SSD
- $24/month (~₹2,000/month)
- Location: Bangalore (lowest latency for India)

### Option 3: AWS Lightsail
- 2 vCPU, 4 GB RAM, 80 GB SSD
- $20/month (~₹1,700/month)
- Region: Mumbai

**Recommended:** DigitalOcean Bangalore for India clients

---

## 📋 Pre-Deployment Checklist

- [ ] Domain name registered (e.g., agriflow.in)
- [ ] DNS A record pointing to server IP
- [ ] SSH key pair generated locally
- [ ] GitHub repo cleaned (no secrets committed)
- [ ] Local backup of dev.agriflow.local DB
- [ ] All 8 commits pushed to GitHub
- [ ] Production credentials documented securely (1Password/Bitwarden)

---

## 🔧 Server Setup Steps (Ubuntu 22.04 LTS)

### 1. Initial Server Hardening

```bash
# SSH as root
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Create non-root user
adduser agriflow
usermod -aG sudo agriflow

# Copy SSH keys
rsync --archive --chown=agriflow:agriflow ~/.ssh /home/agriflow

# Disable root SSH
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart sshd

# Firewall
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw enable
```

### 2. Install Dependencies

```bash
# Switch to agriflow user
su - agriflow

# Install required packages
sudo apt install -y python3-dev python3-pip python3-venv \
    mariadb-server redis-server nginx supervisor git \
    build-essential wkhtmltopdf libpango1.0-0 libpangoft2-1.0-0 \
    nodejs npm yarn

# Verify versions
python3 --version  # Should be 3.10+
node --version     # Should be 18+
mariadb --version  # 10.6+
```

### 3. MariaDB Configuration

```bash
sudo mysql_secure_installation

# Edit MariaDB config
sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf
```

Add under `[mysqld]`:
```ini
character-set-client-handshake = FALSE
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
innodb_file_format = barracuda
innodb_file_per_table = 1
innodb_large_prefix = 1
```

Restart:
```bash
sudo systemctl restart mariadb
```

### 4. Install Frappe Bench

```bash
sudo pip3 install frappe-bench
bench init --frappe-branch version-15 frappe-bench
cd frappe-bench
```

### 5. Create Production Site

```bash
bench new-site agriflow.yourcompany.com \
    --mariadb-root-password YOUR_DB_ROOT_PASSWORD \
    --admin-password YOUR_ADMIN_PASSWORD

# Install ERPNext
bench get-app --branch version-15 erpnext
bench --site agriflow.yourcompany.com install-app erpnext

# Install Agriflow
bench get-app https://github.com/murugamodern-coder/AgriFlow_OS.git --branch stabilization-v1
bench --site agriflow.yourcompany.com install-app agriflow
```

### 6. Configure Production Mode

```bash
bench setup production agriflow
sudo systemctl restart nginx
sudo systemctl restart supervisor
```

### 7. SSL Certificate (Let's Encrypt)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d agriflow.yourcompany.com

# Auto-renew test
sudo certbot renew --dry-run
```

### 8. Verify Deployment

```bash
# Check services
sudo systemctl status nginx
sudo systemctl status supervisor
sudo systemctl status mariadb
sudo systemctl status redis-server

# Test endpoint
curl https://agriflow.yourcompany.com/api/method/ping
# Expected: {"message":"pong"}
```

---

## 💾 Data Migration from Dev to Production

### Backup Dev Site
```bash
# On WSL (local)
cd ~/workspace/frappe-bench
./env/bin/bench --site dev.agriflow.local backup --with-files
# Backups stored in: sites/dev.agriflow.local/private/backups/
```

### Transfer to Production
```bash
# Copy backups to production server
scp sites/dev.agriflow.local/private/backups/* \
    agriflow@your-server-ip:/home/agriflow/frappe-bench/sites/

# On production server
cd /home/agriflow/frappe-bench
bench --site agriflow.yourcompany.com restore \
    /path/to/database-backup.sql.gz \
    --with-public-files /path/to/files-public.tar \
    --with-private-files /path/to/files-private.tar
```

---

## 🔒 Security Hardening

### Application Level
- Change Administrator password immediately
- Create role-specific users (no shared accounts)
- Enable 2FA for admin accounts
- Review user permissions monthly

### Server Level
- fail2ban: `sudo apt install fail2ban`
- Automatic security updates: `sudo dpkg-reconfigure -plow unattended-upgrades`
- Disable unused services

### Database Level
- Regular automated backups (see backup section)
- Encrypted backups
- Off-site backup storage

---

## 📊 Monitoring Setup

### Basic Monitoring
```bash
# Install htop, iotop
sudo apt install -y htop iotop ncdu

# Frappe error logs
tail -f ~/frappe-bench/logs/web.error.log
tail -f ~/frappe-bench/logs/worker.error.log
```

### Optional: UptimeRobot (Free)
- Monitor: https://agriflow.yourcompany.com/api/method/ping
- Alert email/SMS when down
- 5-minute checks

---

## 🔄 Automated Daily Backups

Create file `/home/agriflow/backup_agriflow.sh`:

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/home/agriflow/backups
mkdir -p $BACKUP_DIR

cd /home/agriflow/frappe-bench
./env/bin/bench --site agriflow.yourcompany.com backup --with-files

# Move latest backup
mv sites/agriflow.yourcompany.com/private/backups/*.sql.gz $BACKUP_DIR/db_$DATE.sql.gz 2>/dev/null
mv sites/agriflow.yourcompany.com/private/backups/*public-files*.tar $BACKUP_DIR/public_$DATE.tar 2>/dev/null
mv sites/agriflow.yourcompany.com/private/backups/*private-files*.tar $BACKUP_DIR/private_$DATE.tar 2>/dev/null

# Keep only last 7 days
find $BACKUP_DIR -mtime +7 -delete

# Optional: Upload to S3/Backblaze B2
# aws s3 sync $BACKUP_DIR s3://agriflow-backups/
```

Schedule with cron:
```bash
chmod +x /home/agriflow/backup_agriflow.sh
crontab -e
# Add: 0 2 * * * /home/agriflow/backup_agriflow.sh
```

---

## 📱 Mobile App Update for Production

Update `mobile/agriflow_mobile/lib/core/network/api_config.dart`:

```dart
class ApiConfig {
  static const String baseUrl = 'https://agriflow.yourcompany.com';
  // For dev: 'http://172.28.181.245:8000'
}
```

Build production APK:
```bash
cd mobile/agriflow_mobile
flutter build apk --release
# APK at: build/app/outputs/flutter-apk/app-release.apk
```

---

## 🚨 Rollback Plan

If production deployment fails:

1. **DB issue:** Restore from latest backup
```bash
   bench --site agriflow.yourcompany.com restore /path/to/backup.sql.gz
```

2. **Code issue:** Revert to last working commit
```bash
   cd apps/agriflow
   git checkout <last-working-commit>
   bench --site agriflow.yourcompany.com migrate
   bench restart
```

3. **Full failure:** Spin up new server from snapshot

---

## 💰 Monthly Cost Breakdown

| Item | Cost (₹) |
|------|---------|
| Server (DO Bangalore 4GB) | 2,000 |
| Domain (.in) | 100 |
| Backup storage (Backblaze B2) | 200 |
| Email service (Zoho) | 250 |
| WhatsApp Business API (Phase 2) | 500 |
| Contingency | 950 |
| **Total** | **~₹4,000/month** |

**Lower than initial ₹5,000 estimate** ✅

---

## 🎯 Go-Live Day Plan

### Morning (Pre-launch)
- [ ] Final backup of dev DB
- [ ] DNS propagation check
- [ ] SSL certificate valid
- [ ] Test all critical paths

### Launch (10 AM)
- [ ] Deploy code
- [ ] Run migrations
- [ ] Restore production data
- [ ] Smoke test 10 paths

### Post-Launch (Same Day)
- [ ] Train 1 user (dealer/owner)
- [ ] Create 1 real farmer record
- [ ] Generate 1 real invoice
- [ ] Verify mobile app works

### Week 1 Monitoring
- [ ] Daily health checks
- [ ] User feedback collection
- [ ] Performance monitoring
- [ ] Bug triage queue

---

## 📞 Support Plan

### Phase 1 (First Month) — White Glove
- Daily WhatsApp check-ins
- Phone support 9 AM - 9 PM
- Same-day bug fixes
- Weekly review meeting

### Phase 2 (Month 2-3) — Standard
- Phone support 10 AM - 7 PM
- 48-hour bug fix SLA
- Bi-weekly review

### Phase 3 (Month 4+) — Maintenance
- WhatsApp support
- Weekly review
- Quarterly feature roadmap

---

## 🎓 Staff Training Plan

### Day 1: Office Staff (4 hours)
**Morning:**
- Login + dashboard overview
- Farmer registration (hands-on)
- Project lifecycle understanding

**Afternoon:**
- Cash & Carry POS
- Project Sale with subsidy
- PDF generation + sharing

### Day 2: Field Staff (3 hours)
**Morning:**
- Mobile app installation
- Field data entry
- Photo upload

**Afternoon:**
- Workflow transitions
- Officer contact management
- Service visit completion

### Day 3: Owner/Dealer (2 hours)
- Profit dashboard
- Reports interpretation
- User management
- System administration basics

---

## ✅ Production Readiness Checklist

### Code
- [ ] All commits pushed to GitHub main branch
- [ ] No hardcoded credentials in code
- [ ] Environment variables documented
- [ ] Test coverage > 30%

### Infrastructure
- [ ] Server provisioned
- [ ] Domain + SSL configured
- [ ] Firewall rules set
- [ ] Backup cron job working

### Data
- [ ] Dev → Prod migration tested
- [ ] Demo data NOT migrated (start fresh)
- [ ] Real client data plan documented

### Documentation
- [ ] Admin guide created
- [ ] Staff training materials ready
- [ ] Troubleshooting FAQ
- [ ] Contact directory

### Monitoring
- [ ] Uptime monitoring active
- [ ] Error alerts configured
- [ ] Disk space monitoring
- [ ] Log rotation set

### Business
- [ ] SLA agreement signed
- [ ] Payment plan confirmed
- [ ] Support contact established
- [ ] Phase 2 roadmap shared