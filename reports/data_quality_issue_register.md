# Data Quality Issue Register

**Project:** SaaS Revenue & Subscription Analytics  
**Dataset Source:** RavenStack Synthetic SaaS Dataset  
**Phase:** Week 1 — Day 2  
**Owner:** Jaykishan (Team Lead)

## 1. Purpose

This document consolidates the data quality issues identified
during the exploratory data analysis and data quality audit
of the five RavenStack datasets.

The objective is to identify missing values, duplicate
identifiers, unusual values and potential data integrity
problems before beginning the cleaning phase.

No raw dataset has been modified.

## 2. Consolidated Issue Register

| Issue ID | Dataset | Column | Finding | Severity | Status |
|---|---|---|---|---|---|
| DQ-001 | Churn Events | feedback_text | 148 missing values (24.67%) | Medium | Open |
| DQ-002 | Subscriptions | end_date | 4,514 missing values (90.28%) | High | Under Review |
| DQ-003 | Feature Usage | usage_id | 21 repeated ID values affecting 42 records | High | Under Review |
| DQ-004 | Support Tickets | satisfaction_score | 825 missing values (41.25%) | Medium | Open |
| DQ-005 | Subscriptions | mrr_amount / arr_amount | Revenue consistency requires business-rule validation | Medium | Pending Verification |
| DQ-006 | Support Tickets | submitted_at / closed_at | Timestamp chronology requires validation | Medium | Pending Verification |
| DQ-007 | Subscriptions | start_date / end_date | Date chronology requires validation | Medium | Pending Verification |

## 3. Detailed Findings

### DQ-001: Missing Churn Feedback

Dataset: ravenstack_churn_events.csv

Column: feedback_text

- Total records: 600
- Missing records: 148
- Missing percentage: 24.67%

Observation:
Some churn events do not contain customer feedback.

Potential impact:
Text-based churn reason and customer feedback analysis
may be limited.

Recommended investigation:
Determine whether customer feedback is optional or mandatory.
Do not automatically replace missing feedback with text.

### DQ-002: Missing Subscription End Dates

Dataset: ravenstack_subscriptions.csv

Column: end_date

- Total records: 5,000
- Missing records: 4,514
- Missing percentage: 90.28%

Observation:
All 4,514 missing end dates belong to records where
churn_flag is False.

Breakdown:
- Non-trial, not churned: 3,814 missing end dates.
- Trial, not churned: 700 missing end dates.
- Non-trial, churned: 408 with end dates.
- Trial, churned: 78 with end dates.

Potential impact:
Subscription duration and lifecycle analysis may be affected.

Recommended investigation:
Confirm whether missing end dates represent ongoing
subscriptions or another lifecycle condition.

### DQ-003: Repeated Feature Usage IDs

Dataset: ravenstack_feature_usage.csv

Column: usage_id

- Total records: 25,000
- Unique IDs: 24,979
- Repeated ID values: 21
- Rows affected by repeated IDs: 42

Observation:
Some usage records share the same usage identifier.

Potential impact:
The usage_id column cannot currently be treated as
a unique primary key.

Recommended investigation:
Inspect the repeated ID records and determine whether
they are source identifier collisions or legitimate records.

Do not delete these records without evidence.

### DQ-004: Missing Support Ticket Satisfaction Scores

Dataset: ravenstack_support_tickets.csv

Column: satisfaction_score

- Total records: 2,000
- Missing records: 825
- Missing percentage: 41.25%

Observation:
A substantial number of support tickets do not contain
a satisfaction rating.

Potential impact:
Customer satisfaction analysis may be affected.

Recommended investigation:
Check whether satisfaction scores are optional or
depend on ticket closure and customer feedback.

### DQ-005: Revenue Consistency

Dataset: ravenstack_subscriptions.csv

Columns: mrr_amount, arr_amount

Observation:
MRR and ARR values are available, but their consistency
must be verified against the dataset's billing definitions.

Recommended investigation:
Verify whether ARR equals twelve times MRR for all
applicable subscription records.

The mismatch count has not yet been confirmed.

### DQ-006: Support Ticket Timestamp Validation

Dataset: ravenstack_support_tickets.csv

Columns: submitted_at, closed_at

Observation:
Timestamp chronology requires validation.

Recommended investigation:
Check for invalid dates and closed timestamps earlier
than submitted timestamps.

Final validation results are pending.

### DQ-007: Subscription Date Validation

Dataset: ravenstack_subscriptions.csv

Columns: start_date, end_date

Observation:
Subscription date chronology requires validation.

Recommended investigation:
Check invalid start dates and end dates earlier
than their corresponding start dates.

Final validation results are pending.

## 4. Referential Integrity Results

| Relationship | Records Checked | Unmatched References |
|---|---:|---:|
| Subscriptions.account_id → Accounts.account_id | 5,000 | 0 |
| Churn Events.account_id → Accounts.account_id | 600 | 0 |
| Support Tickets.account_id → Accounts.account_id | 2,000 | 0 |
| Feature Usage.subscription_id → Subscriptions.subscription_id | 25,000 | 0 |

All tested references matched successfully.

## 5. Candidate Identifier Validation

| Dataset | Candidate ID | Total Records | Unique IDs | Null IDs |
|---|---|---:|---:|---:|
| Accounts | account_id | 500 | 500 | 0 |
| Churn Events | churn_event_id | 600 | 600 | 0 |
| Feature Usage | usage_id | 25,000 | 24,979 | 0 |
| Subscriptions | subscription_id | 5,000 | 5,000 | 0 |
| Support Tickets | ticket_id | 2,000 | 2,000 | 0 |

All candidate identifiers except usage_id satisfy the
observed uniqueness and non-null checks.

## 6. Severity Definitions

- Critical: Prevents reliable analysis or data loading.
- High: Significant issue affecting data integrity or key identification.
- Medium: May affect specific metrics or analytical conclusions.
- Low: Minor issue with limited analytical impact.

## 7. Review Rules

1. Every issue must be supported by evidence.
2. No raw data should be modified.
3. Missing values must not be automatically filled.
4. Repeated identifiers must be investigated before removal.
5. Proposed cleaning rules require approval.
6. All decisions must be documented.

## 8. Current Status

The initial profiling and relationship checks are complete.

The remaining findings require further investigation and
business-rule confirmation before cleaning decisions
are approved.

**Prepared by:** Jaykishan  
**Phase:** Week 1 — Day 2
