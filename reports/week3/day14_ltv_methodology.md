# Week 3 Day 14 — LTV Methodology and Feasibility

## Decision

**Do not publish a numeric lifetime value (LTV) estimate from the current supplied data.** The processed file `data/processed/week3/customer_revenue_ltv_inputs.csv` contains observed account-level revenue and tenure inputs, while `ltv_estimate` remains NULL and `ltv_status` records why no estimate is published.

## Supported calculations

- Monthly ARPC = total customer-level recurring MRR in a month / distinct active paid accounts in that month.
- Observed customer revenue = sum of that account's month-end customer MRR over the observed period.
- Observed active months = number of month-end snapshots in which the account had eligible paid MRR.
- Observed tenure = inclusive calendar months between first and last active month.

All revenue amounts are **source amount units**; currency is unconfirmed. `mrr_amount` is used directly for both monthly and annual billing-frequency rows, consistent with the Week 2 validation that ARR equals 12 × MRR.

## Why LTV is unavailable

1. The available history is finite (24 reporting months in the reviewed Week 2 output), not a verified full customer lifetime.
2. Churn flags do not contain event timestamps; churn-event rows are not a reliable, unique customer-loss timeline without further event review.
3. No validated survival curve, stable churn assumption, or forecast horizon has been approved.
4. The source does not establish whether all accounts were observed from acquisition through final churn.
5. A short observed revenue sum is historical revenue, not realized lifetime value.

## Formula only if a future estimate is approved

A simple steady-state model could be `LTV = monthly ARPC × gross margin % / monthly customer churn rate`. This requires a validated monthly customer churn rate, gross margin, stable population assumptions, and a defensible observation window. None of those inputs is fully approved here, so this formula is documented but **not evaluated**. A cohort/survival model would be preferable when event chronology and follow-up support it.

## CAC feasibility

CAC = attributable acquisition spend / new customers acquired. The provided source tables contain `referral_source` but no marketing expenditure, campaign cost, or verified multi-touch attribution. Therefore CAC is **not calculable**. Referral source must not be treated as spend or attribution proof.

## Plan and source limitations

- Plan for cohort reporting is the plan on the first qualifying paid subscription; later plan changes do not reassign cohort.
- Plan-wise month-end MRR is attributed to each eligible subscription's `plan_tier`; concurrent subscriptions can make distinct plan customer counts non-additive.
- Active subscription rule uses inclusive `end_date >= month_end` provisionally; Week 2 records that end-date semantics remain unconfirmed.
- Do not add currency symbols or imply INR/USD.

## Required before estimating LTV

Approve churn event chronology and month-end end-date semantics; obtain sufficient customer follow-up; validate gross margin; decide the model horizon and discounting; then back-test a cohort or survival-based estimate.
