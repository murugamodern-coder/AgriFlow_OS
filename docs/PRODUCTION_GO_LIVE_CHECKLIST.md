# AgriFlow OS - Go-Live Day Checklist

**Pilot client:** [Client Name]  
**Go-live date:** [DD/MM/YYYY]  
**Person responsible:** [Your Name]

## 1 Week Before Go-Live

- [ ] Server provisioned (DO/Hetzner)
- [ ] Domain DNS configured (A record)
- [ ] SSL certificate installed
- [ ] Frappe + ERPNext + AgriFlow deployed
- [ ] Production site loads at https://agriflow.client.com
- [ ] Admin account created (NOT Administrator)
- [ ] All test data cleared from production
- [ ] Backup cron job tested
- [ ] Mobile app updated to point to production URL

## 3 Days Before Go-Live

- [ ] Demo to client successful
- [ ] Client signed agreement
- [ ] Initial payment received
- [ ] Staff training schedule confirmed
- [ ] Real farmer data import format confirmed

## 1 Day Before Go-Live

- [ ] Final database backup of dev environment
- [ ] All 8+ commits pushed to GitHub
- [ ] Production smoke test (login, create farmer, create invoice)
- [ ] Mobile app APK built and tested
- [ ] Printed user guides ready
- [ ] WhatsApp support group created

## Go-Live Day Morning (9 AM)

- [ ] Server health check (ping, CPU, RAM, disk)
- [ ] Database backup taken
- [ ] Bench restart test successful
- [ ] SSL cert valid > 60 days
- [ ] Mobile app installed on client phone

## Go-Live (10 AM - 12 PM)

- [ ] Onboard owner/dealer (login, dashboard tour)
- [ ] Create FIRST real farmer record together
- [ ] Create FIRST real project together
- [ ] Generate FIRST real invoice together
- [ ] Share invoice PDF via WhatsApp
- [ ] Take screenshot for marketing

## Go-Live Afternoon (2 PM - 5 PM)

- [ ] Office staff training (4 staff members)
- [ ] Field staff mobile app onboarding (2 staff)
- [ ] Service technician dashboard tour (if applicable)
- [ ] Q&A session
- [ ] Document feedback

## Day 1 End (6 PM)

- [ ] Backup taken
- [ ] All users have working logins
- [ ] At least 5 real farmers created
- [ ] At least 2 real invoices created
- [ ] Mobile sync verified
- [ ] WhatsApp support active

## Week 1 Daily Tasks

- [ ] Morning health check (9 AM)
- [ ] Lunch check-in with client (1 PM)
- [ ] Evening backup verification (8 PM)
- [ ] Bug triage from WhatsApp
- [ ] Same-day bug fixes

## Week 1 End Review

- [ ] User count: ___
- [ ] Farmers created: ___
- [ ] Projects created: ___
- [ ] Invoices generated: ___
- [ ] Mobile usage: ___
- [ ] Issues encountered: ___
- [ ] Performance: ___
- [ ] Client satisfaction: ___ / 10

## Month 1 Milestones

- [ ] 50+ farmers in production
- [ ] 20+ active projects
- [ ] 100+ invoices generated
- [ ] 5+ daily users
- [ ] < 1% downtime
- [ ] Zero data loss incidents

## Phase 2 Decision Point

After Month 1:
- [ ] Client renews contract
- [ ] MIMIS Excel sample provided
- [ ] Phase 2 scope agreed
- [ ] Phase 2 timeline agreed
- [ ] Phase 2 payment confirmed

---

## Emergency Contacts

| Role | Name | WhatsApp | Email |
|------|------|----------|-------|
| Developer | You | +91-XXXXX | you@email.com |
| DevOps | You | +91-XXXXX | you@email.com |
| Client Lead | [Client] | +91-XXXXX | client@email.com |
| Server (DO Support) | - | - | support@digitalocean.com |