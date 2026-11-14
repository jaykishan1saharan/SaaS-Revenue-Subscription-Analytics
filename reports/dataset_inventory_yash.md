Dataset Inventory — Yash
Inspection date: 2026-11-14
Scope: ravenstack_accounts.csv and the supplied subscription file, ravenstack_subscriptions.csv
Handling: Read-only inspection. No raw CSV file was modified.
Filename note: No plans.csv was present among the supplied files. ravenstack_subscriptions.csv was inspected as the available plan/subscription dataset. The source README lists a singular ravenstack_subscription.csv, while the actual supplied filename is plural (ravenstack_subscriptions.csv); this report uses the actual supplied filename.

1. File-level inventory
Dataset role	Actual supplied file	Rows	Columns	Total cells
Accounts	ravenstack_accounts.csv	500	10	5,000
Plans / subscriptions equivalent	ravenstack_subscriptions.csv	5,000	14	70,000
Combined	2 files	5,500	24 across both files	75,000


Counts exclude the header row and include all data rows. Both files were read successfully as CSVs.
2. Accounts — ravenstack_accounts.csv
- Shape: 500 rows × 10 columns
- Missing cells: 0
- Exact duplicate rows: 0
- Primary ID: account_id — 500 distinct, 0 null, 0 duplicate values
Column	pandas dtype	Non-null	Sample values
account_id	object	500	A-2e4581, A-43a9e3, A-0a282f
account_name	object	500	Company_0, Company_1, Company_2
industry	object	500	EdTech, FinTech, DevTools
country	object	500	US, IN, US
signup_date	object	500	2024-10-16, 2023-08-17, 2024-08-27
referral_source	object	500	partner, other, organic
plan_tier	object	500	Basic, Basic, Basic
seats	int64	500	9, 18, 1
is_trial	bool	500	False, False, False
churn_flag	bool	500	False, True, False


Date coverage
Date column	Parsed values	Missing / unparseable	Earliest	Latest
signup_date	500	0	2023-01-02	2024-12-31


signup_date is stored as object when read directly from the CSV. Its observed values parse successfully as dates in YYYY-MM-DD format.
Observed categorical values
- industry (5): EdTech, FinTech, DevTools, HealthTech, Cybersecurity
- country (7): US, IN, UK, CA, DE, AU, FR
- referral_source (5): partner, other, organic, event, ads
- plan_tier (3): Basic, Enterprise, Pro
- is_trial: False = 403; True = 97
- churn_flag: False = 390; True = 110
- seats: minimum 1; maximum 163
3. Plans / subscriptions — ravenstack_subscriptions.csv
- Shape: 5,000 rows × 14 columns
- Missing cells: 4,514, all in end_date
- Exact duplicate rows: 0
- Primary ID: subscription_id — 5,000 distinct, 0 null, 0 duplicate values
- Account reference: account_id — 500 distinct values across 5,000 rows
Column	pandas dtype	Non-null	Sample values
subscription_id	object	5,000	S-8cec59, S-0f6f44, S-51c0d1
account_id	object	5,000	A-3c1a3f, A-9b9fe9, A-659280
start_date	object	5,000	2023-12-23, 2024-06-11, 2024-11-25
end_date	object	486	2024-04-12, (missing), (missing)
plan_tier	object	5,000	Enterprise, Pro, Enterprise
seats	int64	5,000	14, 17, 62
mrr_amount	int64	5,000	2786, 833, 0
arr_amount	int64	5,000	33432, 9996, 0
is_trial	bool	5,000	False, False, True
upgrade_flag	bool	5,000	False, False, True
downgrade_flag	bool	5,000	False, False, False
churn_flag	bool	5,000	True, False, False
billing_frequency	object	5,000	monthly, monthly, annual
auto_renew_flag	bool	5,000	True, True, False


Date coverage
Date column	Parsed values	Missing / unparseable	Earliest	Latest
start_date	5,000	0	2023-01-09	2024-12-31
end_date	486	4,514	2023-04-05	2024-12-31


Both date columns are stored as object in the raw CSV. All non-null values parse successfully as dates in YYYY-MM-DD format.
Observed categorical values and counts
- plan_tier: Basic, Pro, Enterprise
- billing_frequency: monthly, annual
- is_trial: False = 4,222; True = 778
- upgrade_flag: False = 4,471; True = 529
- downgrade_flag: False = 4,782; True = 218
- churn_flag: False = 4,514; True = 486
- auto_renew_flag: True = 4,005; False = 995
- seats: minimum 1; maximum 189
- mrr_amount: minimum 0; maximum 33,830
- arr_amount: minimum 0; maximum 405,960
The currency or unit for mrr_amount and arr_amount is not specified in the inspected CSV columns, so no currency is assumed.
4. Distinct ID counts and relationship check
File	ID column	Distinct values	Null IDs	Duplicate values
Accounts	account_id	500	0	0
Subscriptions	subscription_id	5,000	0	0
Subscriptions	account_id	500	0	4,500 repeated rows


Relationship validation using the actual ID values:
- Distinct account IDs in accounts: 500
- Distinct account IDs in subscriptions: 500
- Account ID intersection: 500
- Subscription account IDs not found in accounts: 0
- Account IDs with no subscription record: 0
- Subscription rows per account: 10 on average; range 2–19
Interpretation: The supplied subscription records reference all 500 account IDs, and no unmatched account IDs were found. account_id is therefore a viable join key for these two supplied files. The subscription table contains multiple rows per account, so it is not a one-to-one relationship.
5. Data-quality notes and handling recommendations
1. Preserve both original CSVs unchanged; carry out transformations in separate working or cleaned files.
2. Parse signup_date, start_date, and non-null end_date to a date/datetime type in the cleaning layer. Keep the original source files unchanged.
3. Investigate the 4,514 missing end_date values. They may indicate active or open-ended subscriptions, but that meaning is not proven by the missing values alone.
4. Keep subscription_id as the unique subscription-level identifier and account_id as the account-level join key.
5. Confirm the currency/unit for mrr_amount and arr_amount from dataset documentation before interpreting monetary values.
6. Validate business rules (for example, date ordering and consistency between flags and end dates) in a separate quality-check step; this inventory does not alter or correct records.
6. Inspection method
The CSVs were loaded for inspection only. Row/column counts, pandas-inferred dtypes, null counts, exact duplicate-row counts, sample values, date parsing coverage, distinct ID counts, and account-key overlap were calculated from the supplied files. No write operation was performed against either raw CSV.