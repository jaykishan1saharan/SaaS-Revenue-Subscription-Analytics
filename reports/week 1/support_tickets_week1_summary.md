# Support Tickets — Week 1 Summary

## 1. Dataset Overview

**Source File:** `ravenstack_support_tickets.csv`  
**Database Table:** `support_tickets`  
**Primary Key:** `ticket_id`  
**Total Records:** 2,000  
**Total Columns:** 9

The Support Tickets dataset contains customer support activity, including ticket submission and closure timestamps, resolution duration, priority, first response time, customer satisfaction, and escalation status.

---

## 2. Columns

| Column | Description |
|---|---|
| ticket_id | Unique support ticket identifier |
| account_id | Related customer account |
| submitted_at | Ticket submission timestamp |
| closed_at | Ticket closure timestamp |
| resolution_time_hours | Time taken to resolve the ticket |
| priority | Ticket priority category |
| first_response_time_minutes | Time taken for the first response |
| satisfaction_score | Customer satisfaction score |
| escalation_flag | Indicates whether the ticket was escalated |

---

## 3. Data Quality Review

| Validation | Result |
|---|---:|
| Total records | 2,000 |
| Total columns | 9 |
| Missing satisfaction_score | 825 |
| Missing satisfaction percentage | 41.25% |
| Exact duplicate rows | 0 |
| Unique ticket IDs | 2,000 |
| Duplicate ticket IDs | 0 |
| Observed resolution time | 1–72 hours |
| Observed first response time | 1–180 minutes |
| Observed satisfaction score | 3–5 |
| Tickets closed before submission | 0 |

The observed numeric ranges describe the available dataset and should not be treated as formal service-level targets.

---

## 4. Missing Value Review

The `satisfaction_score` column contains 825 missing values.

These missing values should remain NULL unless a documented business rule requires a specific treatment.

A missing satisfaction score should not be interpreted as a zero rating or as customer dissatisfaction.

---

## 5. Database Loading and Relationships

The `support_tickets` table was successfully loaded into Supabase PostgreSQL.

| Validation | Result |
|---|---|
| Database rows | 2,000 |
| Primary key | `ticket_id` |
| Primary key duplicates | 0 |
| Foreign key | `account_id` |
| Referenced table | `accounts` |
| Orphan account references | 0 |
| Invalid ticket chronology | 0 |

**Relationship:** Each support ticket belongs to an account through `account_id`.

---

## 6. Analytical Importance

The Support Tickets table can support:

- Average ticket resolution time.
- First response time analysis.
- Ticket priority distribution.
- Customer satisfaction analysis.
- Escalation rate analysis.
- Support workload trends.
- Support performance by customer segment.
- Relationship between support activity and churn.

---

## 7. Week 1 Completion Status

| Task | Status |
|---|---|
| Dataset inspection | Completed |
| Data-quality audit | Completed |
| Missing-value review | Completed |
| Primary key identification | Completed |
| Supabase table creation | Completed |
| Data loading | Completed |
| Primary key validation | Passed |
| Foreign key validation | Passed |
| Ticket chronology validation | Passed |
| Week 1 summary documentation | Prepared |

---

## 8. Week 2 Recommendations

1. Analyze ticket volume by priority.
2. Calculate average and median resolution time.
3. Analyze first response time.
4. Calculate escalation percentage.
5. Analyze satisfaction scores where available.
6. Compare support performance across account segments.
7. Explore relationships between support activity and customer churn.

---

**Dataset Owner:** Lav Kumar  
**Final Review and Documentation Coordination:** Jaykishan  
**Project:** SaaS Revenue & Subscription Analytics  
**Status:** Week 1 dataset review documented