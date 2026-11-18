# Day 2 — Final Audit Findings and Evidence

**Project:** SaaS Revenue & Subscription Analytics  
**Owner:** Jaykishan  
**Phase:** Week 1 — Day 2

## 1. Audit Scope

Five RavenStack CSV datasets were audited.

Total records: 33,100  
Total columns: 50  
Completely duplicated rows: 0  
Total missing cells: 5,487

## 2. Audit Evidence Files

| File | Description |
|---|---|
| dataset_audit_summary.csv | Dataset dimensions, missing cells and duplicate rows |
| column_audit_profile.csv | Column-level missing values, unique values and data types |
| candidate_id_validation.csv | Candidate ID uniqueness and null checks |
| reference_integrity_checks.csv | Cross-dataset reference validation |
| subscription_end_date_by_status.csv | Missing end-date analysis by churn and trial flags |

## 3. Candidate Identifier Results

| Dataset | Identifier | Result |
|---|---|---|
| Accounts | account_id | 500 unique IDs |
| Churn Events | churn_event_id | 600 unique IDs |
| Feature Usage | usage_id | 21 repeated ID values |
| Subscriptions | subscription_id | 5,000 unique IDs |
| Support Tickets | ticket_id | 2,000 unique IDs |

Feature Usage requires further identifier investigation.

## 4. Referential Integrity Evidence

| Source Dataset | Reference Column | Target Dataset | Unmatched |
|---|---|---|---:|
| Subscriptions | account_id | Accounts | 0 |
| Churn Events | account_id | Accounts | 0 |
| Support Tickets | account_id | Accounts | 0 |
| Feature Usage | subscription_id | Subscriptions | 0 |

All four tested relationships had zero unmatched references.

## 5. Missing Value Evidence

| Dataset | Column | Missing Records |
|---|---|---:|
| Churn Events | feedback_text | 148 |
| Subscriptions | end_date | 4,514 |
| Support Tickets | satisfaction_score | 825 |

These values require business interpretation before cleaning.

## 6. Subscription End-Date Evidence

| Churn Flag | Trial Flag | Records | Missing End Dates |
|---|---|---:|---:|
| False | False | 3,814 | 3,814 |
| False | True | 700 | 700 |
| True | False | 408 | 0 |
| True | True | 78 | 0 |

The missing end dates are associated with subscriptions
where churn_flag is False.

This is an observation, not yet a confirmed data error.

## 7. Pending Evidence

The following reports or checks require final verification:

- Detailed inspection of repeated usage IDs.
- MRR and ARR consistency results.
- Invalid subscription date results.
- Invalid support ticket timestamp results.
- Invalid churn event date results.
- Individual team-member audit findings.

## 8. Data Preservation Statement

All audit operations were performed on read-only
representations of the source CSV datasets.

No raw records were intentionally modified, deleted
or overwritten during Day 2.

## 9. Audit Status

Initial profiling: Completed  
Candidate ID screening: Completed  
Reference integrity checks: Completed  
Missing value investigation: Completed initially  
Date chronology validation: Pending final verification  
Revenue consistency validation: Pending final verification  
Team review: Pending individual member sign-off

**Prepared by:** Jaykishan  