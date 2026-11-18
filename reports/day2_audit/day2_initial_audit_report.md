# Day 2 — Initial Data Quality Audit

**Project:** SaaS Revenue & Subscription Analytics

**Owner:** Jaykishan (Team Lead)

## Dataset-level summary

| dataset                        |   rows |   columns |   duplicate_rows |   total_missing_cells |
|:-------------------------------|-------:|----------:|-----------------:|----------------------:|
| ravenstack_accounts.csv        |    500 |        10 |                0 |                     0 |
| ravenstack_churn_events.csv    |    600 |         9 |                0 |                   148 |
| ravenstack_feature_usage.csv   |  25000 |         8 |                0 |                     0 |
| ravenstack_subscriptions.csv   |   5000 |        14 |                0 |                  4514 |
| ravenstack_support_tickets.csv |   2000 |         9 |                0 |                   825 |

## Audit notes

- Raw CSV files were read without modification.
- Duplicate rows and missing values were counted.
- Columns containing 'id' were screened as possible identifiers only.
- Date-like columns were screened for parsing failures.
- No cleaning or deletion was performed.
- Candidate keys and relationships require further validation.
