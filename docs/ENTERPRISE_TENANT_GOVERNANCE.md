# Enterprise Tenant Governance

## Model

AgriFlow enterprise scale uses **one Frappe site per customer** (tenant). Governance is tracked on each site via:

| Record | Purpose |
|--------|---------|
| **Tenant Ops Record** | Registry: `tenant_key`, segment, SLA tier, status |
| **Customer Onboarding** | Provisioning wizard progress |
| **GA Release Signoff** | Release governance (Phase 22) |

Cross-tenant operations are performed **per site** by visiting each site's `/enterprise_ops_console` or calling APIs with an Administrator session on that site.

## Segments

| Segment | SLA tier default | Use case |
|---------|------------------|----------|
| `pilot` | standard | Evaluation |
| `ga` | standard | Production rollout |
| `enterprise` | enterprise | Premium support |

## APIs

- `enterprise.register_tenant_api` — register tenant on current site  
- `enterprise.enterprise_onboarding_pack_api` — template + onboarding + tenant  
- `enterprise.cross_tenant_governance_api` — site-level governance snapshot  
- `enterprise.export_enterprise_audit` — compliance export  

## Automation (scheduler)

See `scripts/phase23_hooks_snippet.py`:

- **Daily:** `phase23_automation.execute`  
- **Weekly:** `phase23_retention.execute`  

## Retention defaults

| Data | Default retention |
|------|-----------------|
| Pilot Device Telemetry | 90 days |
| Sync Mutation Log | 180 days |
| Push Delivery Log | 60 days |

Configure via site config: `agriflow_telemetry_retention_days`, etc.
