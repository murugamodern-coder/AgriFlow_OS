# Customer Go-Live Checklist

Per-customer checklist before marking **Customer Onboarding** status `live`.

## Provisioning

- [ ] Dedicated Frappe site created (one site per customer)
- [ ] TLS certificate installed
- [ ] JWT + secrets configured (`agriflow_auth_mode=jwt`)

## Onboarding

- [ ] `start_onboarding` completed all wizard steps
- [ ] `ga.customer_readiness` score ≥ **80** (green band)
- [ ] Role template applied (Field Staff, Store Keeper, etc.)
- [ ] Demo or production seed executed

## Field readiness

- [ ] Officer accounts created and User Permissions scoped
- [ ] APK installed on all pilot devices (min version enforced)
- [ ] Wi‑Fi full sync completed on each device
- [ ] Field training session completed (see OPERATIONAL_HANDOFF.md)

## Operations handoff

- [ ] `/ga_ops_console` access for customer ops contact
- [ ] Support assignment owner defined (`assigned_to` on tickets)
- [ ] SLA baseline captured (first week metrics)
- [ ] Status set to `live` on Customer Onboarding
