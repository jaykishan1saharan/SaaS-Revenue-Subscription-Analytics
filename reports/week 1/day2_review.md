# Day 2 — EDA and Data Quality Audit Review

**Project:** SaaS Revenue & Subscription Analytics  
**Dataset:** RavenStack Synthetic SaaS Dataset  
**Prepared by:** Jaykishan  
**Phase:** Week 1 — Day 2

## 1. Objective

The objective of Day 2 was to perform exploratory data
analysis and a data quality audit across all five RavenStack
datasets.

The audit focused on understanding dataset structures,
identifying missing values, checking duplicate records,
validating candidate identifiers and investigating
relationships between datasets.

The purpose was to understand the quality and reliability
of the source data before beginning the cleaning process.

## 2. Datasets Audited

The following five datasets were successfully profiled:

1. ravenstack_accounts.csv
2. ravenstack_churn_events.csv
3. ravenstack_feature_usage.csv
4. ravenstack_subscriptions.csv
5. ravenstack_support_tickets.csv

## 3. Dataset Summary

| Dataset | Rows | Columns | Duplicate Rows | Missing Cells |
|---|---:|---:|---:|---:|
| Accounts | 500 | 10 | 0 | 0 |
| Churn Events | 600 | 9 | 0 | 148 |
| Feature Usage | 25,000 | 8 | 0 | 0 |
| Subscriptions | 5,000 | 14 | 0 | 4,514 |
| Support Tickets | 2,000 | 9 | 0 | 825 |
| Total | 33,100 | 50 | 0 | 5,487 |

## 4. Major Audit Observations

### 4.1 Missing Values

Missing values were identified in three datasets:

- Churn Events: 148 missing feedback_text values.
- Subscriptions: 4,514 missing end_date values.
- Support Tickets: 825 missing satisfaction_score values.

The missing subscription end dates were further analyzed
using churn_flag and is_trial.

All subscriptions with churn_flag = False had missing
end dates, while all subscriptions with churn_flag = True
had populated end dates.

This suggests that missing end dates may represent
ongoing subscriptions. Business definitions must be
confirmed before making any decision.

### 4.2 Duplicate Records

No completely duplicated rows were identified
in any of the five datasets.

However, Feature Usage contains 21 repeated usage_id
values affecting 42 records.

The repeated identifiers require investigation because
usage_id cannot currently be considered a unique key.

### 4.3 Candidate Identifier Validation

The following candidate identifiers were checked:

- accounts.account_id
- churn_events.churn_event_id
- feature_usage.usage_id
- subscriptions.subscription_id
- support_tickets.ticket_id

All candidate identifiers had zero null values.

All candidate IDs except feature_usage.usage_id
were unique across their respective datasets.

### 4.4 Referential Integrity

The following relationships were tested:

- Subscriptions to Accounts
- Churn Events to Accounts
- Support Tickets to Accounts
- Feature Usage to Subscriptions

No unmatched references were identified.

This supports the proposed relationships between
the datasets.

### 4.5 Date and Revenue Validation

Date chronology and revenue consistency require
additional review.

The MRR and ARR mismatch count and final timestamp
validation results have not yet been confirmed.

These checks must be completed before the audit
is considered fully validated.

## 5. Key Findings

1. All five datasets were successfully located and profiled.
2. The combined datasets contain 33,100 records.
3. No completely duplicated rows were found.
4. Three datasets contain missing values.
5. Feature Usage contains repeated usage identifiers.
6. All tested foreign-key references matched successfully.
7. Candidate identifiers were validated for nulls and uniqueness.
8. Subscription lifecycle definitions require confirmation.
9. Revenue and timestamp checks require final verification.

## 6. Data Integrity and Audit Principles

The following principles were maintained:

- Raw CSV files were preserved without modification.
- No records were deleted.
- No missing values were filled.
- No unsupported business assumptions were introduced.
- Candidate relationships were tested against actual records.
- Findings were documented for further review.

## 7. Deliverables

The following Day 2 documentation was prepared:

- data_quality_issue_register.md
- day2_review.md
- day2_final_findings.md
- Dataset-level audit summary CSV
- Column-level audit profile CSV
- Candidate ID validation CSV
- Referential integrity validation CSV
- Subscription end-date analysis CSV

## 8. Pending Investigations

The following checks remain open:

1. Investigate the 21 repeated usage_id values.
2. Confirm the meaning of missing subscription end dates.
3. Investigate missing churn feedback.
4. Investigate missing ticket satisfaction scores.
5. Confirm MRR and ARR consistency.
6. Validate ticket timestamp chronology.
7. Validate subscription date chronology.
8. Obtain and review the individual audit findings from all team members.

## 9. Day 2 Conclusion

The initial exploratory data analysis and data quality
audit successfully covered all five RavenStack datasets.

The audit identified missing values, repeated candidate
identifiers and potential lifecycle-related data issues.

The tested cross-dataset references showed no unmatched
records, providing a useful foundation for the next
stages of the project.

The findings have been documented without modifying
the original source datasets.

Day 2 documentation is prepared, with the remaining
validation checks and team-member reviews tracked
as outstanding items.

**Prepared by:** Jaykishan  
**Project:** SaaS Revenue & Subscription Analytics
