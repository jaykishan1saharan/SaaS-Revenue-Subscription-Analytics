# Day 6 — Support Ticket Analysis

## Scope

This analysis extends the Week 1 support-ticket audit and Day 4 SQL exploration. It covers monthly ticket volume and escalation, escalation rate by priority, satisfaction by priority and escalation status, and resolution-time distribution.

The analysis was run against the cleaned support-ticket dataset. The runner loaded and verified 2,000 records.

## Findings

### 1. Monthly ticket and escalation trend

- Monthly ticket volume ranged from 59 tickets in February 2023 to 98 in December 2024.
- The monthly escalation rate ranged from 1.20% in January 2023 to 8.64% in May 2024.
- These are descriptive monthly counts and rates; they do not establish the cause of changes.

### 2. Escalation by priority

| Priority | Tickets | Escalated | Escalation rate |
|---|---:|---:|---:|
| Medium | 491 | 25 | 5.09% |
| Low | 485 | 23 | 4.74% |
| High | 510 | 24 | 4.71% |
| Urgent | 514 | 23 | 4.47% |
| **Total** | **2,000** | **95** | **4.75%** |

Medium priority had the highest observed escalation rate. Urgent priority had the largest ticket count, but not the highest escalation rate.

### 3. Satisfaction by priority and escalation

Among tickets with a recorded satisfaction score, average scores ranged from 3.89 to 4.21 across priority/escalation groups. Satisfaction response coverage differed by group, so averages should be interpreted alongside response counts and response rates.

Missing satisfaction scores were not treated as zero.

### 4. Resolution-time distribution

| Resolution time | Tickets | Share |
|---|---:|---:|
| 0–24 hours | 709 | 35.45% |
| 24–48 hours | 616 | 30.80% |
| Over 48 hours | 675 | 33.75% |
| **Total** | **2,000** | **100.00%** |

About one-third of tickets took over 48 hours to resolve. The bands are descriptive and are not presented as formal service-level targets.

## Limitations

- This is descriptive analysis; it does not establish causes or service-level compliance.
- Satisfaction results reflect tickets with recorded responses. Response coverage differs across groups.
- Monthly escalation rates are based on the observed ticket counts and should not be interpreted as causal trends.

## Files

- SQL: `sql/05_support_ticket_day6_analysis.sql`
- Runner: `src/run_support_ticket_day6.py`
