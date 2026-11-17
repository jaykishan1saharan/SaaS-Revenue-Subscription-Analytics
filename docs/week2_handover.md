# Week 2 Handover — SaaS Revenue & Subscription Analytics

## 1. Purpose

This document hands over the completed Week 1 project foundation and defines the priorities, pending checks, and expected deliverables for Week 2.

Week 2 will focus on SQL-based business analysis, SaaS KPI development, and preparing reliable analytical datasets.

---

## 2. Current Project Status

### Completed Foundation

- GitHub repository and team branch workflow established.
- Five RavenStack datasets audited.
- Cleaning decision log and data dictionary prepared.
- Five PostgreSQL tables created in Supabase.
- All five datasets loaded successfully.
- Total records loaded: 33,100.
- Five primary keys verified.
- Four foreign key relationships verified.
- No orphan records found.
- Dataset-specific load-validation reports prepared.
- Initial exploration SQL prepared.

### Database Tables

| Table | Records |
|---|---:|
| accounts | 500 |
| subscriptions | 5,000 |
| churn_events | 600 |
| feature_usage | 25,000 |
| support_tickets | 2,000 |

---

## 3. Pending Items Before KPI Sign-Off

The following decisions must be confirmed before final KPI calculations.

### 3.1 Subscription End Dates

There are 4,514 missing values in `subscriptions.end_date`.

Possible interpretation: the subscription may still be ongoing.

**Action:** Review this interpretation with the team. Do not replace NULL end dates with the current date without an approved business rule.

### 3.2 Active Subscription Definition

**Action:** Agree on the exact rule for identifying an active subscription.

The rule should consider:

- Subscription start date.
- Subscription end date.
- Trial status.
- Churn status.
- Reporting date.

### 3.3 MRR Calculation

**Action:** Define how subscription revenue will be normalized.

The team must consider:

- Monthly billing.
- Annual billing.
- Subscription seats.
- Discounts or refunds, if available.
- Active versus historical subscriptions.

The dataset has an MRR field, but the team should still document how it will be interpreted and aggregated.

### 3.4 Churn Calculation

**Action:** Agree on the churn definition and denominator.

The analysis should distinguish between:

- Customer churn.
- Revenue churn.
- Cancellation.
- Reactivation.
- New subscriptions.
- Upgrades and downgrades.

Do not treat every churn event as a unique churned customer without checking account history and reactivation records.

### 3.5 Missing Values

Continue preserving missing values unless an approved analytical rule requires otherwise.

| Table | Column | Missing Values |
|---|---|---:|
| churn_events | feedback_text | 148 |
| subscriptions | end_date | 4,514 |
| support_tickets | satisfaction_score | 825 |

---

## 4. Week 2 Work Plan

### Task 1 — Initial SQL Exploration

**File:** `sql/03_initial_exploration.sql`

- Execute the prepared queries in Supabase.
- Inspect account and subscription distributions.
- Explore plan tiers and billing frequencies.
- Review revenue-related fields.
- Explore churn reasons and refund amounts.
- Analyze feature usage patterns.
- Review support ticket performance.
- Record important findings in a report.

**Expected output:** Initial SQL exploration findings.

### Task 2 — SaaS KPI Definitions

Document the formula, business meaning, required fields, and assumptions for each KPI.

Suggested KPIs:

| KPI | Purpose |
|---|---|
| Monthly Recurring Revenue (MRR) | Measure normalized recurring revenue |
| Annual Recurring Revenue (ARR) | Measure annualized recurring revenue |
| Customer Churn Rate | Measure customer loss |
| Revenue Churn Rate | Measure recurring revenue lost |
| Customer Retention Rate | Measure customer retention |
| Average Revenue Per Account (ARPA) | Measure average account revenue |
| Upgrade Rate | Measure subscription upgrades |
| Downgrade Rate | Measure subscription downgrades |
| Reactivation Rate | Measure returning customers |
| Feature Adoption | Measure product feature usage |
| Support Resolution Time | Measure support efficiency |

**Expected output:** Documented KPI definitions and assumptions.

### Task 3 — SQL Business Analysis

Develop SQL queries for:

- Revenue and subscription analysis.
- Customer and plan-tier analysis.
- Churn and retention analysis.
- Upgrade, downgrade, and reactivation analysis.
- Feature usage analysis.
- Support ticket analysis.

**Expected output:** Organized SQL analysis scripts and query results.

### Task 4 — Findings and Documentation

- Record important observations.
- Identify patterns and potential business problems.
- Document assumptions and limitations.
- Keep all analytical results reproducible through SQL.

**Expected output:** Initial business analysis report.

---

## 5. Suggested Team Responsibilities

The following is a suggested Week 2 ownership plan. The team lead should confirm assignments with everyone before work begins.

| Team Member | Suggested Responsibility |
|---|---|
| Yash | Account segmentation and customer analysis |
| Jaykishan | Team coordination, final review, revenue KPI definitions, documentation consolidation |
| Madhupriya | Churn, retention, and reactivation analysis |
| Meghana | Subscription, MRR, ARR, upgrade, and downgrade analysis |
| Lav Kumar | Feature usage and support ticket analysis |

All members should share their SQL scripts, query outputs, findings, and assumptions through their personal branches and pull requests.

---

## 6. GitHub Workflow

Each member should:

1. Fetch the latest repository changes.
2. Switch to their own branch.
3. Merge or rebase the latest `main` changes.
4. Complete assigned work.
5. Commit and push changes to their personal branch.
6. Create a pull request to `main`.
7. Request review before merging.

The team lead will review SQL logic, naming consistency, documentation, and whether assumptions are clearly recorded.

---

## 7. Expected Week 2 Deliverables

Suggested deliverables:

- Executed initial exploration SQL and recorded findings.
- KPI definition and formula documentation.
- SQL business analysis scripts.
- Revenue and subscription analysis.
- Churn and retention analysis.
- Feature usage and support analysis.
- Initial business findings report.
- Updated README and project documentation where required.

---

## 8. Important Working Rules

- Do not modify raw source datasets.
- Do not commit `.env` files or database credentials.
- Do not replace missing values without documented justification.
- Do not assume NULL subscription end dates mean cancellation.
- Do not finalize MRR or churn formulas until business rules are agreed upon.
- Use consistent SQL formatting and meaningful aliases.
- Keep SQL queries reproducible.
- Document assumptions beside the relevant KPI or query.
- Review all pull requests before merging into `main`.

---

## 9. Handover Summary

Week 1 established the project's data foundation and verified the initial database load.

Week 2 begins the transition from data preparation to business analysis.

The main priority is to produce accurate, clearly documented SaaS KPIs and analytical findings using the validated Supabase database.

**Prepared by:** Jaykishan  
**Project:** SaaS Revenue & Subscription Analytics