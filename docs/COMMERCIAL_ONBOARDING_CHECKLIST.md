# Commercial customer onboarding checklist

## Pre-sales / provisioning

- [ ] Customer name and blocks confirmed
- [ ] Production hostname + TLS (Let's Encrypt)
- [ ] Site created on bench (`bench new-site`)
- [ ] `agriflow_auth_mode=jwt` + `agriflow_jwt_secret`
- [ ] Redis + MariaDB + MinIO validated

## Onboarding wizard (desk/API)

- [ ] `commercial.start_onboarding` — customer record created
- [ ] Complete steps: site_config → roles → demo_seed → verify → pilot_users → APK → ops_training
- [ ] Status = `ready`

## Automation commands

```bash
bash scripts/phase20_deploy_commercial.sh
bench --site <site> execute agriflow.project_lifecycle.install.phase20_demo_customer.execute
bench --site <site> execute agriflow.project_lifecycle.install.phase20_verify_commercial.execute
```

## Handoff to customer

- [ ] APK URL + min version
- [ ] Officer accounts + block permissions
- [ ] PILOT_SUPPORT_SOP shared with field lead
- [ ] `/commercial_ops_console` access for ops team
