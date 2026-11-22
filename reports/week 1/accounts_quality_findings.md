\# Accounts Data Quality Findings



\*\*Inspection date:\*\* 2026-11-14  

\*\*Source files:\*\* `ravenstack\_accounts.csv`, `ravenstack\_subscriptions.csv`  

\*\*Scope:\*\* Read-only inspection of the supplied accounts and subscription datasets. Raw CSV files were not modified.



\## 1. Executive summary



The accounts dataset is structurally clean based on the checks recorded in the dataset inventory: all 500 account IDs are present and unique, there are no missing cells, and there are no exact duplicate rows.



The subscriptions dataset also has unique, non-null subscription IDs and no exact duplicate rows. Its main quality concern is the large number of missing `end\_date` values: 4,514 of 5,000 rows (90.28%). The meaning of these missing dates is not established by the source data and should be confirmed before using them to classify active, expired, or churned subscriptions.



The two datasets can be joined using `account\_id`. All 500 account IDs in the subscriptions data match an account in the accounts data. The relationship is one-to-many: multiple subscription records belong to each account.



\## 2. Dataset-level findings



| Dataset | Rows × columns | Missing cells | Exact duplicate rows | Identifier check |

|---|---:|---:|---:|---|

| `ravenstack\_accounts.csv` | 500 × 10 | 0 | 0 | `account\_id`: 500 unique, 0 null |

| `ravenstack\_subscriptions.csv` | 5,000 × 14 | 4,514 | 0 | `subscription\_id`: 5,000 unique, 0 null |



\## 3. Key quality findings



\### Finding 1 — Missing subscription end dates



\- \*\*Column:\*\* `ravenstack\_subscriptions.csv.end\_date`

\- \*\*Affected rows:\*\* 4,514 of 5,000 (90.28%)

\- \*\*Severity:\*\* High for lifecycle and retention analysis

\- \*\*Observation:\*\* Only 486 rows have a populated `end\_date`.

\- \*\*Impact:\*\* Subscription duration, expiration, renewal, and active-subscription calculations may be misleading if missing dates are treated as ordinary nulls or automatically interpreted as active subscriptions.

\- \*\*Recommended treatment:\*\* Confirm the business meaning of a missing end date with the data owner. Preserve nulls in the raw data. In the analysis layer, use an explicitly documented rule for open-ended or active subscriptions only after confirmation.



\### Finding 2 — Dates stored as text



\- \*\*Columns:\*\* `accounts.signup\_date`, `subscriptions.start\_date`, `subscriptions.end\_date`

\- \*\*Affected fields:\*\* All three date fields are stored as `object` in the raw CSV inspection.

\- \*\*Severity:\*\* Medium

\- \*\*Observation:\*\* The observed populated values use `YYYY-MM-DD` format and parsed successfully in the inventory checks.

\- \*\*Impact:\*\* Date arithmetic, chronological filtering, and time-based grouping can be unreliable if the fields remain strings.

\- \*\*Recommended treatment:\*\* Parse the fields to date/datetime types in a separate cleaning or transformation layer. Retain the original CSV files unchanged and record any parse failures.



\### Finding 3 — One-to-many account/subscription relationship



\- \*\*Join key:\*\* `account\_id`

\- \*\*Severity:\*\* Medium if the table grain is not respected

\- \*\*Observation:\*\* All 500 subscription-side account IDs match the 500 account IDs in the accounts table. No unmatched subscription account IDs or accounts without a subscription record were found. The subscriptions table contains multiple records per account (2–19; average 10).

\- \*\*Impact:\*\* Joining account rows directly to subscription rows increases the row count. Account-level metrics can be double-counted if calculated after the join without controlling for grain.

\- \*\*Recommended treatment:\*\* Use `account\_id` as the join key, retain `subscription\_id` as the subscription-level identifier, and aggregate subscription metrics to account level before calculating account-level totals or rates.



\### Finding 4 — Monetary units are unspecified



\- \*\*Columns:\*\* `mrr\_amount`, `arr\_amount`

\- \*\*Severity:\*\* Medium for financial reporting

\- \*\*Observation:\*\* The inspected files do not specify a currency or unit for these fields.

\- \*\*Impact:\*\* Revenue values should not be labelled with a currency symbol or compared with external financial figures until the unit is confirmed.

\- \*\*Recommended treatment:\*\* Confirm currency and amount conventions from the dataset owner or source documentation. Until then, report values as source units without assuming a currency.



\## 4. Impact on downstream analysis



1\. \*\*Churn and retention:\*\* Missing `end\_date` values require a confirmed interpretation before subscription status or tenure is derived.

2\. \*\*Subscription duration:\*\* Duration calculations should use parsed dates and a documented rule for missing end dates.

3\. \*\*Account-level reporting:\*\* The one-to-many relationship can multiply account rows; aggregate at the correct grain before calculating account-level KPIs.

4\. \*\*Revenue analysis:\*\* Confirm the units of MRR and ARR before presenting currency-based totals, averages, or comparisons.

5\. \*\*Time-series analysis:\*\* Parse date fields before monthly, quarterly, or yearly grouping.



\## 5. Limitations and validation still required



\- The source CSVs alone do not establish why `end\_date` is missing.

\- The currency/unit for `mrr\_amount` and `arr\_amount` is not documented in the inspected files.

\- The inventory confirms the observed date values parsed successfully, but further business-rule validation should still check date chronology (for example, `end\_date` versus `start\_date`).

\- Consistency between lifecycle flags (such as `churn\_flag` and `auto\_renew\_flag`) and subscription dates should be checked against an agreed business definition.

\- No records were deleted, imputed, or overwritten as part of this inspection.



\## 6. Recommendations



1\. Keep the original CSV files unchanged and perform all cleaning in a separate transformation layer.

2\. Confirm the business meaning of missing `end\_date` values before deriving subscription status or duration.

3\. Convert date fields to date/datetime types and log any invalid values.

4\. Validate date ordering and lifecycle-flag consistency using documented business rules.

5\. Preserve the distinction between account-level and subscription-level records when joining and aggregating.

6\. Confirm the currency/unit for MRR and ARR before producing financial reports.

7\. Record each cleaning decision, affected-row count, and reason in a cleaning log so the analysis is reproducible.



\## 7. Handover notes for Member 3



The datasets are ready for downstream analysis once the following points are handled:



\- Join accounts to subscriptions using `account\_id`; expect multiple subscription rows per account.

\- Do not treat the 4,514 missing `end\_date` values as confirmed active subscriptions without business-owner confirmation.

\- Parse `signup\_date`, `start\_date`, and populated `end\_date` values before time-based analysis.

\- Confirm the MRR/ARR currency or unit before financial interpretation.

\- Keep account-level and subscription-level KPIs separate, and document the aggregation grain used.



\## 8. Source references



\- `dataset\_inventory\_yash.md` — file counts, missingness, duplicate checks, date coverage, identifier checks, and relationship validation.

\- `data\_dictionary\_accounts\_plans.md` — source columns, observed types, field descriptions, and observed values.



\*\*Overall assessment:\*\* The accounts file passed the recorded structural checks. The subscriptions file has reliable unique identifiers and a validated account relationship, but missing end dates and undocumented monetary units need to be addressed before lifecycle and financial conclusions are treated as final.



