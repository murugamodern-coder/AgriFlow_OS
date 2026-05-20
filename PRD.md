# AgriFlow OS
Agriculture Operations Platform
Version: 1.0
Status: Active Development

---

# 1. Project Vision

AgriFlow OS is a workflow-first agriculture operations platform built for irrigation subsidy dealers in Tamil Nadu.

The system manages:

- Farmer lifecycle
- Subsidy workflow
- MIMIS tracking
- Inventory
- Billing
- Field operations
- Service management
- Profit visibility

Core philosophy:

> Nothing gets forgotten.
> Everything gets tracked.
> Profit becomes visible.

---

# 2. Business Context

Client Type:
Single-client irrigation subsidy dealer

Location:
Tiruvannamalai District, Tamil Nadu

Operating Blocks:
12 Blocks

Daily Users:
~15 users

Business Types:
1. Subsidy Projects
2. Cash & Carry Sales
3. Machinery Sales

---

# 3. Core Problems

## P1 — Workflow chaos
No visibility into project stage.

## P2 — Follow-up failure
Staff forgets visits, inspections, documents.

## P3 — Profit blindness
Owner cannot track project profitability.

## P4 — Stock confusion
2 godowns not tracked properly.

## P5 — Officer hierarchy missing
Cannot filter by block, cluster, officer.

## P6 — Service tracking missing
3-year service lifecycle unmanaged.

---

# 4. Product Goals

The platform must:

- Track every farmer project
- Automate follow-ups
- Provide owner visibility
- Support offline-first operations
- Support Tamil-first UI
- Reduce staff confusion
- Scale to future districts

---

# 5. Technology Stack

## Backend
- Frappe Framework v15
- MariaDB 11
- Redis 7

## Mobile
- Flutter 3.24
- Riverpod 2.5
- Hive + Drift
- Dio + Retrofit
- go_router

## Infrastructure
- Docker
- Coolify
- Hetzner
- MinIO
- Evolution API

---

# 6. Architecture Principles

## Workflow-first
Every operation revolves around project stages.

## Offline-first
Field staff must work without internet.

## Timeline-first
Project visibility should be understandable in one screen.

## Tamil-first
Tamil support mandatory.

## Role-based
Each user sees only relevant data.

---

# 7. User Roles

## Owner
Full access.

## Office Manager
Approvals, reports, billing.

## Office Staff
Farmer registration, quotation, documents.

## Field Staff
Survey, farmer visits, follow-ups.

## Installer Team
Installation workflow.

## Service Technician
AMC/service visits.

## Store Keeper
Inventory operations.

---

# 8. Core Entities

## Farmer
Stores farmer identity and land details.

## Farmer Project
Main lifecycle entity.

## Officer
Agriculture/horticulture officers.

## Village
Geographic hierarchy.

## Cluster
Officer-to-village grouping.

## Task
Operational follow-up system.

## Inventory Item
Products and stock.

## Expense Entry
Operational expense tracking.

---

# 9. Farmer Project Lifecycle

The system revolves around a 12-stage workflow.

Stages:

1. Lead Captured
2. Eligibility Check
3. Documents Collected
4. MIMIS Registered
5. Field Survey
6. Quotation Generated
7. Pre-Inspection Approval
8. Work Order Received
9. Material Dispatched
10. Installation Done
11. Post-Inspection Approval
12. Subsidy Released

Rules:
- Sequential transitions only
- No stage skipping
- Auto task generation
- Timeline history mandatory

---

# 10. Geographic Hierarchy

District
→ Block
→ Cluster
→ Officer
→ Village
→ Farmer

Officer transfers every 3 years must preserve historical ownership.

---

# 11. Modules

## M1 — Farmer Registry
Farmer profile, tags, land details.

## M2 — Inventory
2-godown stock management.

## M3 — Billing
Cash & Carry + Project billing.

## M4 — MIMIS Sync
Manual + Excel reconciliation.

## M5 — Project Lifecycle
Timeline workflow engine.

## M6 — Task Engine
Follow-up automation.

## M7 — Service / AMC
3-year maintenance tracking.

## M8 — Officer Network
Hierarchy + expense-safe tracking.

## M9 — Profit Dashboard
Owner business visibility.

---

# 12. Offline Sync Rules

Reads:
- Hive local cache

Writes:
- SyncQueue first
- Server later

Conflict Rules:
- Server wins for master data
- Client wins for new entries
- Last-write wins for updates

---

# 13. UI Principles

Inspired by:
- Linear
- Notion
- Khatabook
- PhonePe

Avoid:
- ERP-style heavy forms
- Multi-tab complexity
- Desktop-era UI patterns

---

# 14. Design Tokens

Primary:
#047857

Accent:
#4F46E5

Background:
#F8FAFC

Fonts:
- Poppins
- Inter
- Noto Sans Tamil

---

# 15. Security

- JWT authentication
- Role-based access
- Audit logs mandatory
- All file uploads validated
- Daily backups

---

# 16. AI Strategy

Phase 1:
NO AI features.

Phase 2:
Operational AI only.

Examples:
- Follow-up prediction
- Stock forecasting
- OCR
- Daily summaries

Avoid:
- Fake chatbot features
- Gimmick AI

---

# 17. Deployment

Production Stack:
- Hetzner VPS
- Docker
- Coolify
- Caddy SSL
- Backblaze backup

---

# 18. Success Metrics

Success means:

- No missed follow-ups
- Faster project completion
- Visible profit tracking
- Lower operational confusion
- Better staff accountability

---

# 19. Future Scope

Possible future expansion:

- SaaS model
- Farmer app
- Supplier management
- AI forecasting
- Multi-district support

---

# 20. Final Principle

AgriFlow OS is not a billing application.

It is an operational memory system for agriculture businesses.

Everything important must be:
- tracked
- visible
- actionable
- auditable