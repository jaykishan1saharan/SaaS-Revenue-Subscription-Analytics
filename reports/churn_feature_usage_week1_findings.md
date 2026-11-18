# Churn and Feature Engagement — Week 1 Findings

**Project:** SaaS Revenue & Subscription Analytics  
**Scope:** Churn-event and feature-usage findings, and feasibility of churn and feature-adoption KPIs.  
**Sources:** `data/raw/ravenstack_churn_events.csv`, `data/raw/ravenstack_feature_usage.csv`, `data/raw/ravenstack_accounts.csv`, and `data/raw/ravenstack_subscriptions.csv`.

## Executive summary

The datasets are structurally usable for descriptive event and usage summaries, and all tested account/subscription references resolve. They are **not yet sufficient for defensible churn rates or subscription-lifecycle-based feature adoption KPIs**. Churn events do not by themselves define a churned-customer denominator or a consistent lifecycle; most feature-usage dates fall before the start date of their linked subscription. Clarify the event/date semantics and KPI definitions before publishing rate-based or active-customer metrics.

## Churn findings

- The source contains **600 unique churn-event records** across **352 accounts**. These are event counts, not 600 distinct customers or necessarily 600 first-time churns.
- **61 events (10.17%)** are marked as reactivations. Accounts can have multiple events (up to five); one account has two different event IDs on the same day. Confirm the event grain and lifecycle sequence before counting unique churns.
- The recorded reason counts are: `features` 114, `support` 104, `budget` 104, `unknown` 95, `competitor` 92, and `pricing` 91. Treat these as distributions of event records; `unknown` is not a substantive reason category.
- There are **148 missing feedback values (24.67%)**. Preserve them as missing and report feedback coverage alongside any feedback-based breakdown.
- Event counts are uneven by year: 73 in 2023 and 527 in 2024. The source covers 2023-01-25 through 2024-12-31, but exposure and source completeness by period are not established. Do not interpret raw counts as a rising churn rate.
- All 600 `account_id` references match accounts. No event predates the associated account signup date. However, 277 accounts with events (465 event rows) have `accounts.churn_flag=False`; the flag's as-of date and relationship to historical events/reactivations are undefined.
- Refund amounts range from $0.00 to $392.92. The currency and refund timing/aggregation rules should be confirmed before treating refunds as churn-related financial loss.

## Feature engagement findings

- The source contains **25,000 complete usage rows** over 2023-01-01 through 2024-12-31, covering all 40 observed feature labels and every calendar day in the period.
- Aggregate source measures are **250,525 usage_count**, **76,055,072 seconds** of recorded duration, and **14,107 errors**. These are recorded totals, not unique users, sessions, or adoption rates.
- The largest features by summed `usage_count` are `feature_32` (6,686), `feature_15` (6,621), `feature_6` (6,546), `feature_20` (6,541), and `feature_34` (6,536). Names are generic, and counts per feature are close; confirm the measure's unit and feature definitions before using these as product priorities.
- **4,967 of 5,000 subscriptions** have usage rows; 33 have no observed usage. This is a valid coverage observation, not proof that those subscriptions had no product engagement.
- `usage_id` is not unique: 21 IDs repeat, affecting 42 rows. There are also three repeated `(subscription_id, usage_date, feature_name)` combinations, affecting six rows. No exact duplicate rows were found. Keep the surrogate database key and do not deduplicate on these source fields without a confirmed grain.
- The critical limitation is temporal: **19,142 rows (76.57%) precede the linked subscription's `start_date`**, affecting 4,783 subscriptions; **290 rows (1.16%)** follow a populated `end_date`. If usage dates are event dates and subscription dates define eligibility, lifecycle attribution is unreliable until explained. The current audit establishes the mismatch, not which date is wrong.
- All 25,000 usage references resolve to a subscription, and all subscriptions resolve to an account. Referential integrity passes but does not resolve the temporal mismatch.
- Every one of the 40 feature labels appears with both values of `is_beta_feature`. Confirm whether beta status is time-varying before comparing beta and non-beta adoption. Also confirm the meaning of `error_count`; 17 rows have more errors than usage_count.

## KPI feasibility assessment

| KPI | Feasibility now | Assessment |
|---|---|---|
| Churn-event count by reason, date, reactivation flag, or refund amount | **Feasible with caveats** | Suitable as event-level descriptive reporting. State the date coverage and missing-feedback rate; do not label event counts as customer churn or a churn rate. |
| Churned accounts / churn-event accounts | **Conditional** | Can count unique accounts with at least one recorded event (352 of 500), but not a period churn rate: repeated events/reactivations and account flag timing are unresolved. |
| Logo/customer churn rate by period | **Not yet** | Requires a defined churn event and period-end or at-risk account denominator, consistent cohort/exposure dates, and rules for reactivation and multiple events. |
| Subscription churn rate | **Not yet** | Requires validated subscription status and effective start/end dates, a clear treatment for NULL end dates, and an eligible subscription denominator for each period. |
| Revenue churn / MRR churn | **Not yet for this scope** | Requires validated churn-effective dates, a defined revenue basis and currency, and the subscription-level recurring revenue snapshot immediately before churn. Event refunds are not a substitute for lost recurring revenue. |
| Reactivation rate | **Conditional** | The 61 flagged events can be counted, but a rate needs a defined eligible population, event ordering, and a rule for what qualifies as a reactivation. |
| Total usage volume, duration, errors, or feature ranking | **Feasible with caveats** | Descriptive source-level aggregations can be produced. Label counts as recorded measures, document the observation grain, and avoid user-level interpretations. |
| Feature adoption by feature (distinct accounts/subscriptions using a feature) | **Conditional / not decision-grade** | Subscription IDs can be mapped to accounts, but usage dates conflict with linked subscription periods, and there is no user ID. Any adoption metric needs a validated date rule, explicit unit (account or subscription), and active/eligible denominator. |
| Adoption or engagement rate among active subscriptions/accounts | **Not yet** | Requires lifecycle-correct usage attribution plus an as-of active population and a definition of “adopted” (e.g., at least one qualifying use in a stated window). |
| Beta feature adoption comparison | **Not yet** | Requires confirmed time semantics for the beta flag and comparable eligible populations and exposure windows. |
| Feature usage versus churn | **Not yet** | Requires resolved usage/subscription dates, churn-effective timing, a pre-churn observation window, and appropriate account/subscription grain to avoid leakage and double counting. |

## Recommended next steps

1. Confirm what `usage_date`, `start_date`, and `end_date` represent and investigate the before-start and after-end cases. Do not silently filter or reassign records.
2. Define churn at account and subscription level, including event timing, repeated events, reactivation, and the meaning/as-of date of each `churn_flag`.
3. Agree on each rate's numerator, denominator, cohort, observation window, and treatment of accounts/subscriptions entering or leaving during the period.
4. Confirm the usage observation grain, repeated-ID behavior, feature labels, beta-flag timing, and units for usage and errors.
5. Once rules are approved, recompute lifecycle-valid engagement and churn metrics and retain denominator/coverage counts with each KPI.

## Overall conclusion

Week 1 supports reliable structural checks and cautious descriptive summaries: the churn and usage datasets loaded at their expected sizes, identifiers and references were reviewed, and no orphan account/subscription links were found. Churn rates, lifecycle-based adoption rates.

**Related documentation:** [Churn and feature usage quality findings](./churn_feature_usage_quality_findings.md), [churn and feature usage load validation](./churn_feature_usage_load_validation.md), and [churn and feature usage week 1 summary](./churn_feature_usage_week1_summary.md).
