Data Dictionary — Accounts and Plans / Subscriptions
Inspection date: 2026-11-14
Source files: ravenstack_accounts.csv and ravenstack_subscriptions.csv
Scope note: No separate plans.csv was supplied. The available ravenstack_subscriptions.csv is documented here as the plans/subscriptions equivalent. This dictionary records observed source fields and values; descriptions are based on field names and observed data, not an external business specification.
1. Accounts table
Source: ravenstack_accounts.csv
Grain: One row per account (500 rows).
Primary identifier: account_id (500 distinct, no nulls or duplicates).
Column	Observed source dtype	Nulls	Example value(s)	Description / notes
account_id	object	0	A-2e4581	Account identifier; unique in this file.
account_name	object	0	Company_0	Account/company display name.
industry	object	0	EdTech	Industry category. Observed values: EdTech, FinTech, DevTools, HealthTech, Cybersecurity.
country	object	0	US	Country code/category. Observed values: US, IN, UK, CA, DE, AU, FR.
signup_date	object	0	2024-10-16	Account signup date, represented as an ISO-formatted string in the raw CSV. Coverage: 2023-01-02 through 2024-12-31.
referral_source	object	0	partner	Recorded referral/acquisition source. Observed values: partner, other, organic, event, ads.
plan_tier	object	0	Basic	Plan tier associated with the account record. Observed values: Basic, Enterprise, Pro.
seats	int64	0	9	Seat count recorded for the account; observed range 1–163.
is_trial	bool	0	False	Boolean trial indicator. Observed: 97 True, 403 False.
churn_flag	bool	0	False	Boolean churn indicator. Observed: 110 True, 390 False.


2. Plans / subscriptions table
Source: ravenstack_subscriptions.csv
Grain: One row per subscription record (5,000 rows). Multiple subscription records can belong to one account.
Primary identifier: subscription_id (5,000 distinct, no nulls or duplicates).
Account reference: account_id (500 distinct values, all matched to the accounts table).
Column	Observed source dtype	Nulls	Example value(s)	Description / notes
subscription_id	object	0	S-8cec59	Subscription-record identifier; unique in this file.
account_id	object	0	A-3c1a3f	Account identifier linking a subscription to ravenstack_accounts.csv.
start_date	object	0	2023-12-23	Subscription start date, represented as an ISO-formatted string in the raw CSV. Coverage: 2023-01-09 through 2024-12-31.
end_date	object	4,514	2024-04-12; missing	Subscription end date, represented as an ISO-formatted string when present. 486 populated values; coverage among populated values: 2023-04-05 through 2024-12-31. Missing-value meaning is not established by the CSV alone.
plan_tier	object	0	Enterprise	Plan tier recorded for the subscription. Observed values: Basic, Pro, Enterprise.
seats	int64	0	14	Seat count recorded for the subscription; observed range 1–189.
mrr_amount	int64	0	2786	MRR amount field. Currency/unit is not specified in the inspected file. Observed range 0–33,830.
arr_amount	int64	0	33432	ARR amount field. Currency/unit is not specified in the inspected file. Observed range 0–405,960.
is_trial	bool	0	False	Boolean trial indicator. Observed: 778 True, 4,222 False.
upgrade_flag	bool	0	False	Boolean upgrade indicator. Observed: 529 True, 4,471 False.
downgrade_flag	bool	0	False	Boolean downgrade indicator. Observed: 218 True, 4,782 False.
churn_flag	bool	0	True	Boolean churn indicator. Observed: 486 True, 4,514 False.
billing_frequency	object	0	monthly	Billing-frequency category. Observed values: monthly, annual.
auto_renew_flag	bool	0	True	Boolean auto-renewal indicator. Observed: 4,005 True, 995 False.


3. Keys and relationships
Relationship	Observed validation
accounts.account_id	500 distinct values; unique and non-null.
subscriptions.subscription_id	5,000 distinct values; unique and non-null.
subscriptions.account_id	500 distinct values across 5,000 rows; repeated because accounts have multiple subscription records.
Account-to-subscription match	All 500 distinct subscription account IDs match an account ID in the accounts file.
Unmatched subscription account IDs	0
Accounts without a subscription record	0
Subscription records per account	Average 10; minimum 2; maximum 19.


Join condition: accounts.account_id = subscriptions.account_id

Expected relationship: One account to many subscription records (1:M), based on the observed data.
4. Raw data types versus recommended analytical types
The types below distinguish what pandas inferred from the unmodified CSV from a useful type to apply in a separate analytical/cleaning layer.
Source fields	Raw pandas dtype	Suggested analytical type
account_id, account_name, industry, country, referral_source, plan_tier, subscription_id, billing_frequency	object	string / categorical as appropriate
signup_date, start_date, end_date	object	date or datetime; preserve null end_date values
seats, mrr_amount, arr_amount	int64	integer or suitable numeric type; confirm currency/unit before financial interpretation
is_trial, churn_flag, upgrade_flag, downgrade_flag, auto_renew_flag	bool	boolean


5. Data handling cautions
- This document describes the source as supplied; it does not clean, rename, cast, or otherwise modify the raw files.
- Do not interpret a missing end_date as active status without validating the dataset's business rules.
- Do not assume a currency for mrr_amount or arr_amount; the source fields do not identify one.
- Validate temporal and flag consistency separately before using these fields for churn or revenue analysis.