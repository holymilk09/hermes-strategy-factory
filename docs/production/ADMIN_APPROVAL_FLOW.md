# Admin Approval Flow — Strategy Factory

> **Version:** 1.0  
> **Date:** 2026-07-01  
> **Status:** PLANNING — manual approval only, not yet implemented  

---

## 1. Overview

Every edge sheet must pass through a **manual admin review gate** before it becomes visible to subscribers. There is no auto-publish. A human reviews every sheet for stale data, broken setups, forbidden language, and data integrity.

This is not optional. It is the single most important safety control in the production architecture. Automated checks (healthcheck, test suite, freshness gate) run BEFORE the admin sees the sheet, but the final approval is always manual.

---

## 2. State Machine

```
┌─────────────┐
│  GENERATED   │  ← edge sheet created by pipeline (cron)
└──────┬──────┘
       │ admin opens review dashboard
       ▼
┌─────────────┐
│  REVIEWED    │  ← admin has looked at it, left notes
└──────┬──────┘
       │
       ├── admin finds issue ──▶ stays in REVIEWED with notes
       │                         (pipeline re-runs next day, generates new sheet)
       │
       └── admin approves
              │
              ▼
┌─────────────┐
│  APPROVED    │  ← admin clicked "Approve"
└──────┬──────┘
       │ system promotes to published
       ▼
┌─────────────┐
│  PUBLISHED   │  ← visible to subscribers (only one at a time)
└──────┬──────┘
       │
       └── admin finds post-publish issue
              │
              ▼
┌─────────────┐
│ ROLLED_BACK  │  ← previous published sheet is restored
└──────────────┘
```

### 2.1 State Transitions

| From | To | Trigger | Who |
|---|---|---|---|
| — | `generated` | Pipeline cron runs | System |
| `generated` | `reviewed` | Admin opens review | Admin |
| `reviewed` | `approved` | Admin clicks Approve | Admin |
| `approved` | `published` | System promotes (auto) | System |
| `published` | `rolled_back` | Admin clicks Rollback | Admin |
| `rolled_back` | — | Previous `published` restored to `published` | System |

### 2.2 Rules

1. Only ONE sheet can be `published` at a time
2. Only ONE sheet can be `approved` at a time (the latest)
3. Rollback restores the previous `published` sheet — NOT the rolled-back one
4. If the pipeline generates a new sheet while one is `reviewed`, the old one stays `reviewed` and the new one is `generated`
5. `generated` sheets older than 7 days without review are auto-archived (status stays `generated`)

---

## 3. Admin Review Dashboard

### 3.1 What the Admin Sees

```
┌─────────────────────────────────────────────────────────────────┐
│  EDGE SHEET REVIEW — 2026-07-01                                │
│                                                                 │
│  ═══════════════════════════════════════════════════════════    │
│  PRE-FLIGHT CHECKS                                              │
│  ✅ Healthcheck: PASS                                           │
│  ✅ Full test suite: 398/398 pass                               │
│  ✅ Data freshness: 2026-06-30 (current)                        │
│  ✅ No sent_to_broker flags                                     │
│  ✅ No broker_order_id populated                                │
│  ✅ No forbidden words in output                                │
│  ✅ Research-only disclaimer present                            │
│  ═══════════════════════════════════════════════════════════    │
│                                                                 │
│  SHEET PREVIEW                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Market Weather: Market is helping this setup             │   │
│  │ Grade: B                                                 │   │
│  │ Observations: 7 resolved, 0 pending                      │   │
│  │                                                          │   │
│  │ AMD — Waiting for Stronger Proof — score 80              │   │
│  │   "Relative strength ranks remain elevated..."           │   │
│  │   Price area: 434.15 to 461.01                          │   │
│  │   Setup breaks below: 429.68                            │   │
│  │                                                          │   │
│  │ MRVL — Waiting for Pullback — score 80                   │   │
│  │   "Relative strength ranks remain elevated..."           │   │
│  │   Price area: 255.57 to 271.37                          │   │
│  │   Setup breaks below: 252.93                            │   │
│  │                                                          │   │
│  │ ... (5 more cards)                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ADMIN ACTIONS                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Review Notes: [______________________________]            │   │
│  │                                                          │   │
│  │ [Approve]  [Request Changes]  [View Full JSON]           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  APPROVAL HISTORY                                               │
│  2026-06-30 — approved by admin@example.com                     │
│  2026-06-29 — approved by admin@example.com                     │
│  ...                                                            │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Review Checklist

Admin must confirm each item before approving:

| # | Check | Pass Condition |
|---|---|---|
| A1 | Pre-flight checks all green | Healthcheck + tests + freshness + safety |
| A2 | No stale data | `data_freshness` ≤ 5 calendar days |
| A3 | No forbidden language | Scan for "buy", "sell", "watch", "win rate", "performance", "guaranteed" |
| A4 | Disclaimer present | "Research-only" text in every output |
| A5 | Sample-size warning | Visible if n < 30 independent observations |
| A6 | No commercial edge claims | No "profitable", "validated", "high confidence" |
| A7 | Ticker cards all populated | No empty `why_it_looks` or `plain_english` fields |
| A8 | Grade is honest | B or lower — never A unless multi-cohort evidence exists |
| A9 | Setup-break levels consistent | Breaks-below < current price < breaks-above makes sense |
| A10 | No new strategy types leaking | Active lineage matches approved list |

### 3.3 Approval Decision

| Decision | Action |
|---|---|
| **Approve** | Sheet → `approved` → `published`. Subscribers see new sheet. Previous `published` → archived. |
| **Request Changes** | Stays `reviewed`. Notes attached. Pipeline re-runs next day — new sheet may supersede. |
| **Rollback** (post-publish) | Current `published` → `rolled_back`. Previous `published` restored. Audit log entry with reason. |

---

## 4. Audit Trail

Every approval action is logged:

```json
{
  "action": "edge_sheet_approved",
  "actor": "admin@example.com",
  "sheet_date": "2026-07-01",
  "pre_flight_healthcheck": "PASS",
  "pre_flight_tests": "398/398",
  "review_notes": "All checks pass. MRVL setup-broke but scoreboard reflects this honestly.",
  "approved_at": "2026-07-01T10:15:00Z"
}
```

Rollback entries include the reason:

```json
{
  "action": "edge_sheet_rolled_back",
  "actor": "admin@example.com",
  "sheet_date": "2026-07-01",
  "rollback_reason": "SEDG price area calculation looks off — investigating before republish.",
  "rolled_back_at": "2026-07-01T10:30:00Z"
}
```

---

## 5. Emergency Procedures

### 5.1 Immediate Rollback

If a published sheet contains materially wrong data:

1. Admin clicks "Rollback" in dashboard
2. Previous published sheet is restored
3. Subscribers see the restored sheet on next refresh
4. Incident logged in audit trail
5. Root cause investigated before next approval

### 5.2 Pipeline Failure

If the daily pipeline fails (no new edge sheet generated):

1. Previous day's published sheet remains visible
2. Data freshness warning displayed: "Last updated: YYYY-MM-DD"
3. Admin notified (email/webhook)
4. Pipeline retry attempted
5. If retry fails → manual investigation

### 5.3 Data Integrity Breach

If ledger hashes don't match, or duplicate IDs detected:

1. **DO NOT approve any new sheet**
2. Restore from most recent verified backup
3. Re-run pipeline
4. Verify new hashes match expected
5. Only then resume review → approve → publish

---

## 6. Admin Accounts

| Role | Permissions |
|---|---|
| **Super Admin** | Approve, rollback, manage admins, view audit log, run healthcheck |
| **Reviewer** | View pre-flight checks, review sheets, leave notes — cannot approve |
| **System** | Generate sheets, run pipeline, update status — cannot approve |

### 6.1 Admin Authentication

- Supabase Auth with email/password
- 2FA required for Super Admin
- Session timeout: 1 hour idle, 8 hours max
- IP allowlist: only from known admin IPs (optional)

---

## 7. Notification Flow

| Event | Who Gets Notified | Channel |
|---|---|---|
| New sheet generated | Reviewers | Email + dashboard badge |
| Sheet approved | Subscribers (if email delivery on) | Email |
| Sheet rolled back | Subscribers (correction notice) | Email |
| Pipeline failure | Admins | Email + webhook |
| Healthcheck failure | Admins | Email + webhook |
| Data staleness | Admins | Email |

---

## 8. Forbidden Automation

| Action | Can It Be Automated? | Reason |
|---|---|---|
| Publishing an edge sheet | **NO** — manual only | Single most critical safety gate |
| Approving a sheet | **NO** — human review required | Pre-flight checks are automated, decision is not |
| Changing thresholds | **NO** — full research pipeline re-validation required | n=7 is not enough |
| Removing disclaimers | **NO** — compliance requirement | Non-negotiable |
| Modifying ticker card text | **NO** — generated text only | Editorializing = investment advice risk |
| Re-running pipeline on failure | **YES** — retry with exponential backoff | Safe: idempotent, no user-visible effect until approved |