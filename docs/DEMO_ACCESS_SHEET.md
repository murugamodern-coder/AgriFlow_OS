# Demo Access Credentials Sheet
**Print this for client demo session**

---

## 🌐 Web Access

**URL:** http://172.28.181.245:8000  
(For local demo. Production URL after deployment)

**Login:** Administrator  
**Password:** admin123  

⚠️ Change password before client gets access

---

## 📱 Mobile App Access

**Server URL (Settings):** http://172.28.181.245:8000

**Test Logins:**
| Role | Username | Password |
|------|----------|----------|
| Owner | Administrator | admin123 |
| Office Manager | (create) | - |
| Field Staff | (create) | - |
| Service Tech | (create) | - |

---

## 📊 Demo Data Highlights

- **Farmers:** 165 (with Tamil names)
- **Projects:** 55 (across 12 workflow stages)
- **Items:** 18 (Drip, Filter, Valves, etc.)
- **Print formats:** 2 (Cash & Carry thermal, Project A4)

**Sample farmer to demo:**
- FR-00211 onwards (latest seeded batch)

**Sample projects:**
- FP-2026-00261 [material_dispatched]
- FP-2026-00262 [quotation_generated]
- FP-2026-00271 [subsidy_released]

---

## 🔧 Demo Troubleshooting

### Login fails:
1. Check WSL running: `wsl --status`
2. Restart bench: `cd /home/muruga/workspace/frappe-bench && ./env/bin/bench restart`
3. Check ping: `curl http://127.0.0.1:8000/api/method/ping` → should return pong

### Mobile app shows offline:
- Check phone connected to same WiFi as laptop
- Verify server URL in app settings

### PDF won't generate:
- WeasyPrint configured in site_config.json
- Restart bench if first attempt fails

---

## 📞 Quick Contacts (Edit Before Demo)

- **Developer:** [Your name + WhatsApp]
- **Support:** [WhatsApp number]
- **Demo lead:** [Your name]