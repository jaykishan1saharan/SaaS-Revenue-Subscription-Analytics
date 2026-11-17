# SaaS Revenue & Subscription Analytics

An end-to-end data analytics project focused on understanding SaaS revenue performance, subscription trends, customer churn, product usage, and customer support operations.

The project uses the RavenStack dataset, Python-based data preparation, SQL analysis, and a Supabase PostgreSQL database to develop meaningful business insights.

---

## Project Objectives

The main objectives are to:

- Analyze Monthly Recurring Revenue (MRR) and Annual Recurring Revenue (ARR).
- Understand subscription growth and plan-tier distribution.
- Identify customer churn and revenue churn patterns.
- Analyze new subscriptions, upgrades, downgrades, cancellations, and reactivations.
- Understand customer retention.
- Explore product feature usage and adoption.
- Evaluate customer support performance.
- Develop data-driven business recommendations.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data preparation and analysis |
| Pandas | Data manipulation |
| NumPy | Numerical operations |
| Matplotlib / Seaborn | Data visualization |
| SQL | Data exploration and business analysis |
| Supabase PostgreSQL | Relational database |
| Git & GitHub | Version control and team collaboration |
| Jupyter Notebook | Exploratory data analysis |

---

## Dataset Overview

The project uses five RavenStack datasets.

| Dataset | Description | Records |
|---|---|---:|
| Accounts | Customer and account information | 500 |
| Subscriptions | Subscription plans and revenue fields | 5,000 |
| Churn Events | Customer churn and reactivation events | 600 |
| Feature Usage | Product feature usage records | 25,000 |
| Support Tickets | Customer support activity | 2,000 |
| **Total** | | **33,100** |

### Source Files

- `ravenstack_accounts.csv`
- `ravenstack_subscriptions.csv`
- `ravenstack_churn_events.csv`
- `ravenstack_feature_usage.csv`
- `ravenstack_support_tickets.csv`

**Data handling:** Raw and temporary datasets are excluded from Git tracking. Place the source CSV files in `data/raw/` locally when working with the project. Do not commit private credentials or database connection strings.

---

## Project Structure

```text
SaaS-Revenue-Subscription-Analytics/
│
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
│
├── notebooks/
│
├── sql/
│   └── 03_initial_exploration.sql
│
├── src/
│
├── reports/
│   ├── figures/
│   ├── accounts_load_validation.md
│   ├── churn_feature_usage_load_validation.md
│   ├── subscriptions_load_validation.md
│   ├── support_tickets_load_validation.md
│   └── week1_summary.md
│
├── dashboard/
│
├── presentation/
│
├── docs/
│   ├── cleaning_decision_log.md
│   ├── data_dictionary.md
│   ├── database_load_log.md
│   └── week2_handover.md
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Database

The project uses **Supabase PostgreSQL** as its central relational database.

### Database Tables

| Table | Primary Key | Relationship |
|---|---|---|
| accounts | account_id | Parent table |
| subscriptions | subscription_id | References accounts |
| churn_events | churn_event_id | References accounts |
| feature_usage | usage_record_id | References subscriptions |
| support_tickets | ticket_id | References accounts |

The `feature_usage` table uses a generated database identifier, `usage_record_id`, as its primary key because the original source `usage_id` contains repeated values.

### Database Relationships

- One account can have multiple subscriptions.
- One account can have multiple churn events.
- One account can have multiple support tickets.
- One subscription can have multiple feature usage records.

---

## Week 1 — Completed Work

Week 1 focused on establishing the project foundation.

- GitHub repository and folder structure setup.
- Dataset inventory and initial data-quality audit.
- Missing-value and identifier analysis.
- Cleaning decision log and data dictionary preparation.
- Supabase PostgreSQL schema creation.
- Loading all five datasets into Supabase.
- Primary key and foreign key validation.
- Dataset-specific load-validation reports.
- Initial SQL exploration script preparation.
- Week 1 summary and Week 2 handover documentation.

### Database Load Validation

| Validation | Result |
|---|---:|
| Tables loaded | 5 / 5 |
| Total rows loaded | 33,100 |
| Primary key checks passed | 5 / 5 |
| Foreign key checks passed | 4 / 4 |
| Orphan records | 0 |
| Exact duplicate source rows | 0 |

### Known Data Quality Considerations

| Dataset | Column | Missing Values |
|---|---|---:|
| Churn Events | feedback_text | 148 |
| Subscriptions | end_date | 4,514 |
| Support Tickets | satisfaction_score | 825 |

Missing values are retained until their business meaning and appropriate treatment are confirmed.

---

## Week 2 — Planned Work

Week 2 will focus on SQL-based business analysis and SaaS KPI development.

Planned analysis includes:

1. Initial SQL exploration.
2. MRR and ARR analysis.
3. Customer churn and revenue churn.
4. Customer retention and reactivation.
5. Subscription upgrades and downgrades.
6. Plan-tier and customer segmentation.
7. Product feature usage and adoption.
8. Support ticket performance.
9. Initial business findings and recommendations.

KPI formulas and business rules will be documented before final calculations are accepted.

---

## Team

This is a collaborative team project.

| Team Member | Primary Responsibility |
|---|---|
| Jaykishan | Team Lead, database coordination, final review and documentation |
| Yash | Accounts analysis |
| Madhupriya | Churn Events and Feature Usage |
| Meghana | Subscription analysis |
| Lav Kumar | Support Tickets and relationship mapping |

---

## GitHub Collaboration Workflow

The team follows a branch-based Git workflow:

1. Each member works on their personal branch.
2. Members commit and push their changes to their own branches.
3. Members create pull requests targeting `main`.
4. The team lead reviews the changes.
5. Approved pull requests are merged into `main`.

This keeps the main branch organized and makes team contributions easier to review.

---

## Getting Started

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd SaaS-Revenue-Subscription-Analytics
```

Replace the placeholder with the actual GitHub repository URL.

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it in Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Add the Dataset Files

Place the five RavenStack CSV files inside:

```text
data/raw/
```

These files are excluded from Git tracking.

### 5. Configure Database Access

Use your Supabase PostgreSQL connection details through environment variables or your local `.env` configuration.

Never commit `.env` or expose database passwords in source code, notebooks, screenshots, or SQL files.

### 6. Run SQL Analysis

Open the SQL files in the `sql/` directory and execute them using the Supabase SQL Editor or your configured PostgreSQL client.

---

## Documentation

Additional project documentation is available in:

- `docs/cleaning_decision_log.md` — data-cleaning decisions.
- `docs/data_dictionary.md` — dataset columns and definitions.
- `docs/database_load_log.md` — database loading and validation record.
- `docs/week2_handover.md` — Week 2 priorities and pending work.
- `reports/week1_summary.md` — Week 1 completion summary.
- Dataset-specific validation reports in `reports/`.

---

## Project Status

**Current phase:** Week 1 foundation completed; Week 2 analytical development planned.

The database foundation and initial relational validations are complete. Initial exploration queries still need to be executed and their findings documented before business analysis is finalized.

---

## Future Scope

- Develop interactive SaaS analytics dashboards.
- Build customer retention and churn visualizations.
- Analyze recurring revenue trends.
- Identify customer segments and product adoption patterns.
- Present actionable business recommendations.

---

**Project:** SaaS Revenue & Subscription Analytics  
**Database:** Supabase PostgreSQL  
