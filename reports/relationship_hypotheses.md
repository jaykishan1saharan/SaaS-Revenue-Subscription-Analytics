# Relationship Hypotheses and Validation Report

## 1. Objective

Identify candidate primary keys, foreign keys, one-to-many relationships and referential-integrity issues across the five RavenStack datasets.

## 2. Dataset Inventory

| Dataset | Rows | Columns | Candidate ID |
|---|---:|---:|---|
| Accounts | 500 | 10 | account_id |
| Subscriptions | 5,000 | 14 | subscription_id |
| Churn Events | 600 | 9 | churn_event_id |
| Feature Usage | 25,000 | 8 | usage_id |
| Support Tickets | 2,000 | 9 | ticket_id |

## 3. Primary Key Validation

| Table | Total Rows | Unique IDs | Duplicate IDs | Missing IDs |
|---|---:|---:|---:|---:|
| Accounts | 500 | 500 | 0 | 0 |
| Subscriptions | 5,000 | 5,000 | 0 | 0 |
| Churn Events | 600 | 600 | 0 | 0 |
| Feature Usage | 25,000 | 24,979 | 21 | 0 |
| Support Tickets | 2,000 | 2,000 | 0 | 0 |

Finding:

The usage_id field has 21 duplicated values. Inspection shows that repeated IDs are associated with different subscriptions and usage records.

Decision: Do not enforce usage_id as a primary key without resolving the duplicate identifier issue.

## 4. Foreign Key Validation

| Proposed Relationship | Child Records | Matched | Unmatched |
|---|---:|---:|---:|
| accounts to subscriptions | 5,000 | 5,000 | 0 |
| accounts to churn_events | 600 | 600 | 0 |
| accounts to support_tickets | 2,000 | 2,000 | 0 |
| subscriptions to feature_usage | 25,000 | 25,000 | 0 |

All proposed foreign-key relationships achieved 100% matching in the inspected data.

No orphan references were identified.

## 5. Observed Relationship Cardinality

### Subscriptions per Account
- Accounts represented: 500
- Average subscriptions: 10
- Minimum: 2
- Maximum: 19

### Churn Events per Account
- Accounts represented: 352
- Average events: approximately 1.70
- Maximum: 5

### Feature Usage per Subscription
- Subscriptions represented: 4,967
- Average records: approximately 5.03
- Maximum: 16

### Support Tickets per Account
- Accounts represented: 492
- Average tickets: approximately 4.07
- Maximum: 11

## 6. Relationship Hypotheses

| Parent | Child | Relationship | Validation |
|---|---|---|---|
| accounts | subscriptions | One-to-many | Validated |
| accounts | churn_events | One-to-many | Validated |
| accounts | support_tickets | One-to-many | Validated |
| subscriptions | feature_usage | One-to-many | Validated |

These are observed dataset relationships. The database constraints will be defined in the PostgreSQL implementation stage.

## 7. Additional Data Quality Findings

| Table | Issue | Observation |
|---|---|---|
| churn_events | Missing feedback_text | 148 records |
| subscriptions | Missing end_date | 4,514 records |
| support_tickets | Missing satisfaction_score | 825 records |
| feature_usage | Duplicate usage_id | 21 duplicated identifiers |

These findings are recorded for future quality-audit and cleaning tasks.

## 8. Dataset Source and Attribution

Dataset: RavenStack Synthetic SaaS Dataset (Multi-Table)

Author: River @ Rivalytics

Source information and licence are documented in data/raw/README.md.

The dataset is synthetic and contains no personal information. Its README describes an MIT-like permissive licence for educational and portfolio use, with attribution required.

## 9. Limitations and Assumptions

1. There is no separate plans dataset.
2. Invoice and payment datasets are not supplied.
3. Plan information is represented through plan_tier fields.
4. The feature_usage primary key remains unresolved.
5. Multiple churn events may represent reactivation and subsequent churn.
6. Missing values must be interpreted according to business context rather than automatically removed.

## 10. Conclusion

Five source tables containing 33,100 records were inspected.

Four foreign-key relationships were successfully validated with zero unmatched records.

Four candidate primary keys are unique. The feature_usage usage_id field contains 21 duplicated identifiers and requires further investigation.

The proposed relationship structure is suitable as the foundation for the next database-design stage, subject to final team review.
