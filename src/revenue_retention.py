"""Week 3 Day 13: customer-month revenue, GRR/NRR and value segmentation.

Run from repository root after Day 11 cohort files exist:
    python src/revenue_retention.py
Revenue values remain in unconfirmed source amount units.
"""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ACCOUNTS = ROOT / 'data/raw/ravenstack_accounts.csv'
DEFAULT_SUBSCRIPTIONS = ROOT / 'data/raw/ravenstack_subscriptions.csv'
DEFAULT_COHORTS = ROOT / 'data/processed/week3/customer_cohort_assignments.csv'
DEFAULT_ACTIVITY = ROOT / 'data/processed/week3/customer_month_activity.csv'
DEFAULT_OUTPUT = ROOT / 'data/processed/week3'


def build_customer_month_revenue(accounts, cohorts, activity, subscriptions):
    """One row per account-month; revenue is already aggregated from subscriptions."""
    required = {'account_id','country','referral_source','signup_date','plan_tier'}
    missing = required - set(accounts.columns)
    if missing: raise ValueError(f'accounts missing columns: {sorted(missing)}')
    first = subscriptions.loc[(~subscriptions.is_trial.astype(bool)) & (pd.to_numeric(subscriptions.mrr_amount)>0)].copy()
    first['start_date'] = pd.to_datetime(first.start_date)
    first = first.sort_values(['account_id','start_date','subscription_id'],kind='stable').drop_duplicates('account_id')
    cohort_plan = first[['account_id','plan_tier']].rename(columns={'plan_tier':'cohort_plan_tier'})
    result = activity[['account_id','cohort_month','activity_month','cohort_age_month','customer_mrr']].copy()
    account_attrs = accounts[['account_id','country','referral_source','signup_date','plan_tier']].copy()
    result = result.merge(account_attrs,on='account_id',how='left',validate='many_to_one')
    result = result.merge(cohort_plan,on='account_id',how='left',validate='many_to_one')
    result = result.rename(columns={'customer_mrr':'customer_month_mrr'})
    result['customer_month_mrr'] = pd.to_numeric(result.customer_month_mrr,errors='raise')
    if result.duplicated(['account_id','activity_month']).any():
        raise AssertionError('customer-month revenue must be unique at account x month')
    return result


def calculate_grr_nrr(customer_month_revenue):
    """Consecutive-month GRR/NRR for the same opening paid customer base.

    GRR caps each opening customer's closing revenue at opening MRR. NRR
    includes expansion/contraction on opening customers, excludes new logos.
    """
    x=customer_month_revenue.copy()
    x['activity_month']=pd.to_datetime(x.activity_month).dt.to_period('M').dt.to_timestamp()
    panel=x.pivot_table(index='account_id',columns='activity_month',values='customer_month_mrr',aggfunc='sum',fill_value=0)
    months=sorted(panel.columns)
    rows=[]
    for i in range(1,len(months)):
        opening_month,closing_month=months[i-1],months[i]
        opening,closing=panel[opening_month],panel[closing_month]
        base=opening>0
        opening_mrr=float(opening[base].sum())
        closing_mrr=float(closing[base].sum())
        if opening_mrr>0:
            expansion=float((closing[base]-opening[base]).clip(lower=0).sum())
            contraction=float((opening[base]-closing[base]).clip(lower=0).sum())
            churned=float(opening[base & (closing == 0)].sum())
            grr=float(np.minimum(opening[base],closing[base]).sum()/opening_mrr*100)
            nrr=float(closing_mrr/opening_mrr*100)
            status='available_for_opening_paid_customer_base'
        else:
            expansion=contraction=churned=grr=nrr=np.nan; status='unavailable_zero_opening_revenue'
        rows.append({'opening_month':opening_month,'closing_month':closing_month,
          'opening_mrr_source_amount':opening_mrr,
          'closing_mrr_from_opening_customer_base_source_amount':closing_mrr,
          'expansion_mrr_source_amount':expansion,'contraction_mrr_source_amount':contraction,
          'churned_mrr_source_amount':churned,'grr_pct':grr,'nrr_pct':nrr,
          'opening_base_customers':int(base.sum()),'status':status})
    return pd.DataFrame(rows)


def create_customer_segments(customer_month_revenue):
    x=customer_month_revenue.copy()
    x['activity_month']=pd.to_datetime(x.activity_month)
    grouped=x.groupby('account_id').agg(
      observed_active_months=('activity_month','nunique'),
      total_observed_revenue_source_amount=('customer_month_mrr','sum'),
      average_active_month_mrr_source_amount=('customer_month_mrr','mean'),
      first_active_month=('activity_month','min'),last_active_month=('activity_month','max'),
      cohort_month=('cohort_month','first'),cohort_plan_tier=('cohort_plan_tier','first'),
      country=('country','first'),referral_source=('referral_source','first')).reset_index()
    grouped['tenure_months_observed']=(grouped.last_active_month.dt.year-grouped.first_active_month.dt.year)*12+grouped.last_active_month.dt.month-grouped.first_active_month.dt.month+1
    threshold=float(grouped.average_active_month_mrr_source_amount.median())
    grouped['value_threshold_median_active_month_mrr_source_amount']=threshold
    grouped['value_segment']=np.where(grouped.average_active_month_mrr_source_amount>=threshold,'high_value_at_or_above_median','low_value_below_median')
    grouped['segment_rule']='Median of customer average MRR across observed active months; descriptive, not predictive'
    return grouped


def run_pipeline(accounts_path=DEFAULT_ACCOUNTS, subscriptions_path=DEFAULT_SUBSCRIPTIONS,
                 cohorts_path=DEFAULT_COHORTS, activity_path=DEFAULT_ACTIVITY, output_dir=DEFAULT_OUTPUT):
    accounts=pd.read_csv(accounts_path)
    subscriptions=pd.read_csv(subscriptions_path,parse_dates=['start_date','end_date'])
    cohorts=pd.read_csv(cohorts_path,parse_dates=['cohort_month'])
    activity=pd.read_csv(activity_path,parse_dates=['cohort_month','activity_month'])
    output_dir=Path(output_dir); output_dir.mkdir(parents=True,exist_ok=True)
    revenue=build_customer_month_revenue(accounts,cohorts,activity,subscriptions)
    summary=calculate_grr_nrr(revenue)
    segments=create_customer_segments(revenue)
    revenue.to_csv(output_dir/'customer_month_revenue.csv',index=False,date_format='%Y-%m-%d')
    summary.to_csv(output_dir/'revenue_retention_summary.csv',index=False,date_format='%Y-%m-%d')
    segments.to_csv(output_dir/'customer_segments.csv',index=False,date_format='%Y-%m-%d')
    print(f'Customer-month revenue rows: {len(revenue)}; GRR/NRR periods: {len(summary)}; segments: {len(segments)}')
    return revenue,summary,segments

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--accounts',type=Path,default=DEFAULT_ACCOUNTS)
    parser.add_argument('--subscriptions',type=Path,default=DEFAULT_SUBSCRIPTIONS)
    parser.add_argument('--cohorts',type=Path,default=DEFAULT_COHORTS)
    parser.add_argument('--activity',type=Path,default=DEFAULT_ACTIVITY)
    parser.add_argument('--output-dir',type=Path,default=DEFAULT_OUTPUT)
    args=parser.parse_args(); run_pipeline(args.accounts,args.subscriptions,args.cohorts,args.activity,args.output_dir)
