#!/usr/bin/env python3
"""
Script to automatically generate pending transactions from recurring transactions.
This should be run daily (e.g., via cron job) to create pending transactions.
"""

import sys
import os
from datetime import datetime, timedelta, date
from typing import List

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database_operations import DatabaseOperations
from database.models import RecurringTransaction, PendingTransaction, RecurringInterval
from database.supabase_client import get_supabase_client

def latest_due_date_on_or_before(recurring_transaction: RecurringTransaction, current_date: date) -> date:
    """Return the most recent due date that is <= current_date.
    If current_date precedes start_date, returns start_date.
    """
    start_date = recurring_transaction.start_date.date()
    interval = recurring_transaction.interval

    if current_date <= start_date:
        return start_date

    if interval == RecurringInterval.WEEKLY:
        weeks = (current_date - start_date).days // 7
        return start_date + timedelta(weeks=weeks)
    elif interval == RecurringInterval.MONTHLY:
        years = current_date.year - start_date.year
        months = years * 12 + (current_date.month - start_date.month)
        # Clamp to at least 0
        months = max(0, months)
        # Compute candidate date in same day if possible
        y = start_date.year + (start_date.month - 1 + months) // 12
        m = (start_date.month - 1 + months) % 12 + 1
        d = min(start_date.day, [31,29 if (y%4==0 and (y%100!=0 or y%400==0)) else 28,31,30,31,30,31,31,30,31,30,31][m-1])
        return date(y, m, d)
    elif interval == RecurringInterval.QUARTERLY:
        years = current_date.year - start_date.year
        months = years * 12 + (current_date.month - start_date.month)
        quarters = max(0, months // 3)
        y = start_date.year + (start_date.month - 1 + quarters*3) // 12
        m = (start_date.month - 1 + quarters*3) % 12 + 1
        d = start_date.day
        # Adjust day to valid end-of-month
        d = min(d, [31,29 if (y%4==0 and (y%100!=0 or y%400==0)) else 28,31,30,31,30,31,31,30,31,30,31][m-1])
        return date(y, m, d)
    elif interval == RecurringInterval.YEARLY:
        years = max(0, current_date.year - start_date.year)
        y = start_date.year + years
        m = start_date.month
        d = min(start_date.day, [31,29 if (y%4==0 and (y%100!=0 or y%400==0)) else 28,31,30,31,30,31,31,30,31,30,31][m-1])
        return date(y, m, d)
    else:
        return start_date

def should_generate_pending_transaction(recurring_transaction: RecurringTransaction, current_date: date) -> bool:
    if not recurring_transaction.is_active:
        return False
    if recurring_transaction.end_date and current_date > recurring_transaction.end_date.date():
        return False
    # We always attempt to generate for the latest due date on/before today
    return True

def generate_pending_transactions():
    """Generate pending transactions for all active recurring transactions"""
    db = DatabaseOperations()
    client = get_supabase_client()
    current_date = date.today()
    
    print(f"Generating pending transactions for {current_date}")
    
    # Get all organizations
    try:
        orgs_result = client.table("organizations").select("id").execute()
        organizations = [org['id'] for org in orgs_result.data]
    except Exception as e:
        print(f"Error fetching organizations: {e}")
        return
    
    total_generated = 0
    
    for org_id in organizations:
        print(f"Processing organization {org_id}")
        
        # Get all active recurring transactions for this organization
        recurring_transactions = db.get_recurring_transactions_by_organization(org_id)
        
        for recurring in recurring_transactions:
            if should_generate_pending_transaction(recurring, current_date):
                # Determine the month key YYYY-MM for idempotence
                month_key = transaction_date.strftime('%Y-%m')
                
                # Guard 1: if last_generated_on is already same month, skip
                if getattr(recurring, 'last_generated_on', None):
                    if recurring.last_generated_on.strftime('%Y-%m') == month_key:
                        print(f"  Skipping recurring {recurring.id}; already generated for {month_key}")
                        continue
                
                # Guard 2: if a pending already exists in that month for this recurring id, skip
                start_month = transaction_date.replace(day=1)
                if start_month.month == 12:
                    next_month = start_month.replace(year=start_month.year+1, month=1, day=1)
                else:
                    next_month = start_month.replace(month=start_month.month+1, day=1)
                existing_pending = client.table("pending_transactions").select("id").eq(
                    "recurring_transaction_id", recurring.id
                ).gte("transaction_date", start_month.isoformat()).lt("transaction_date", next_month.isoformat()).execute()
                if existing_pending.data:
                    print(f"  Pending already exists for recurring {recurring.id} in {month_key}")
                    continue
                
                # Calculate the transaction date (latest due date on/before today)
                transaction_date = latest_due_date_on_or_before(recurring, current_date)
                
                # Create pending transaction
                pending_transaction = PendingTransaction(
                    organization_id=recurring.organization_id,
                    property_id=recurring.property_id,
                    transaction_type=recurring.transaction_type,
                    income_type=recurring.income_type,
                    expense_type=recurring.expense_type,
                    amount=recurring.amount,
                    description=recurring.description,
                    transaction_date=datetime.combine(transaction_date, datetime.min.time()),
                    recurring_transaction_id=recurring.id,
                    is_confirmed=False
                )
                
                # Save to database
                created = db.create_pending_transaction(pending_transaction)
                if created:
                    print(f"  Generated pending transaction for {recurring.transaction_type} - {recurring.description} - ${recurring.amount}")
                    # Update last_generated_on
                    try:
                        client.table("recurring_transactions").update({"last_generated_on": transaction_date.isoformat()}).eq("id", recurring.id).execute()
                    except Exception:
                        pass
                    total_generated += 1
                else:
                    print(f"  Failed to create pending transaction for recurring {recurring.id}")
    
    print(f"Generated {total_generated} pending transactions")

if __name__ == "__main__":
    generate_pending_transactions()
