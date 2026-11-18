
## Dataset Overview

This project uses the RavenStack Synthetic SaaS Dataset, a
multi-table dataset created by River @ Rivalytics.

The dataset represents a simulated SaaS business environment and
contains account information, subscription records, customer churn
events, product feature usage, and customer support interactions.

### Source Files

| Dataset | File | Description |
|---|---|---|
| Accounts | `ravenstack_accounts.csv` | Customer account information |
| Churn Events | `ravenstack_churn_events.csv` | Customer churn and cancellation events |
| Feature Usage | `ravenstack_feature_usage.csv` | Product feature usage records |
| Subscriptions | `ravenstack_subscription.csv` | Subscription and recurring revenue information |
| Support Tickets | `ravenstack_support_tickets.csv` | Customer support interactions |

### Dataset Source & Attribution

- **Dataset:** RavenStack Synthetic SaaS Dataset
- **Author:** River @ Rivalytics
- **Data type:** Synthetic
- **Format:** CSV
- **Usage:** Educational and portfolio purposes, subject to the original dataset terms.
- **Credit:** River @ Rivalytics

Original download source: [Insert verified download page URL]

For complete source and licence details, see
[`docs/dataset_source.md`](docs/dataset_source.md).

### Data Handling

- Original files are preserved in `data/raw/`.
- Raw datasets are not modified during cleaning.
- Intermediate and cleaned datasets are stored separately.
- Data-quality issues and transformation decisions are documented.
- Database tables will be created in Supabase PostgreSQL after
  schema and relationship validation.

### Dataset Relationships

The expected logical relationships are:

- Accounts → Subscriptions
- Subscriptions → Feature Usage
- Accounts → Churn Events
- Accounts → Support Tickets

These relationships are hypotheses based on the published dataset
description and must be validated against the actual CSV data.
