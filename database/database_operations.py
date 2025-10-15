from database.supabase_client import get_supabase_client
from database.models import Property, Income, Expense, Category, Organization, UserOrganization, Budget, BudgetLine, BudgetPeriod, BudgetScope, RecurringTransaction, PendingTransaction
from typing import List, Optional
import streamlit as st
from datetime import datetime

class DatabaseOperations:
    def __init__(self):
        self.client = get_supabase_client()
        self.supabase = self.client  # Alias for compatibility with rent reminder service
    
    # Organization Operations
    def get_user_organizations(self, user_id: str) -> List[Organization]:
        """Get all organizations for a user"""
        try:
            result = self.client.table("user_organizations").select("organization_id, organizations(*)").eq("user_id", user_id).execute()
            organizations = []
            for row in result.data:
                if row.get("organizations"):
                    org_data = row["organizations"]
                    organizations.append(Organization(**org_data))
            return organizations
        except Exception as e:
            st.error(f"Error fetching user organizations: {str(e)}")
            return []
    
    def get_organization_by_id(self, org_id: int) -> Optional[Organization]:
        """Get organization by ID"""
        try:
            result = self.client.table("organizations").select("*").eq("id", org_id).execute()
            if result.data:
                return Organization(**result.data[0])
            return None
        except Exception as e:
            st.error(f"Error fetching organization: {str(e)}")
            return None
    
    def create_organization(self, organization: Organization, user_id: str) -> Optional[Organization]:
        """Create a new organization and add user as owner"""
        try:
            # Create organization
            org_dict = organization.dict(exclude={'id', 'created_at', 'updated_at'})
            result = self.client.table("organizations").insert(org_dict).execute()
            
            if result.data:
                org = Organization(**result.data[0])
                org_id = org.id
                
                # Add user as owner
                user_org = UserOrganization(
                    user_id=user_id,
                    organization_id=org_id,
                    role="owner"
                )
                user_org_dict = user_org.dict(exclude={'id', 'joined_at'})
                self.client.table("user_organizations").insert(user_org_dict).execute()
                
                return org
            return None
        except Exception as e:
            st.error(f"Error creating organization: {str(e)}")
            return None
    
    # Property Operations
    def create_property(self, property: Property, user_id: str = None, organization_id: int = None) -> Optional[Property]:
        """Create a new property"""
        try:
            property_dict = property.dict(exclude={'id', 'created_at', 'updated_at'})
            property_dict['purchase_date'] = property_dict['purchase_date'].isoformat()
            
            # Add user_id and organization_id for RLS compliance
            if user_id:
                property_dict['user_id'] = user_id
            if organization_id:
                property_dict['organization_id'] = organization_id
            
            result = self.client.table("properties").insert(property_dict).execute()
            if result.data:
                return Property(**result.data[0])
            return None
        except Exception as e:
            st.error(f"Error creating property: {str(e)}")
            return None
    
    def get_properties(self) -> List[Property]:
        """Get all properties"""
        try:
            result = self.client.table("properties").select("*").execute()
            return [Property(**prop) for prop in result.data]
        except Exception as e:
            st.error(f"Error fetching properties: {str(e)}")
            return []
    
    def get_property(self, property_id: int) -> Optional[Property]:
        """Get a specific property by ID"""
        try:
            result = self.client.table("properties").select("*").eq("id", property_id).execute()
            if result.data:
                return Property(**result.data[0])
            return None
        except Exception as e:
            st.error(f"Error fetching property: {str(e)}")
            return None
    
    def get_property_by_id(self, property_id: str) -> Optional[Property]:
        """Get a specific property by ID (string version for rent reminders)"""
        try:
            result = self.client.table("properties").select("*").eq("id", property_id).execute()
            if result.data:
                return Property(**result.data[0])
            return None
        except Exception as e:
            st.error(f"Error fetching property: {str(e)}")
            return None
    
    def get_properties_by_organization(self, organization_id: str) -> List[Property]:
        """Get all properties for a specific organization"""
        try:
            result = self.client.table("properties").select("*").eq("organization_id", organization_id).execute()
            properties = []
            for row in result.data:
                properties.append(Property(**row))
            return properties
        except Exception as e:
            st.error(f"Error fetching properties by organization: {str(e)}")
            return []
    
    def update_property(self, property_id: int, property: Property) -> bool:
        """Update a property"""
        try:
            property_dict = property.dict(exclude={'id', 'created_at', 'updated_at'})
            property_dict['purchase_date'] = property_dict['purchase_date'].isoformat()
            
            result = self.client.table("properties").update(property_dict).eq("id", property_id).execute()
            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error updating property: {str(e)}")
            return False
    
    def delete_property(self, property_id: int) -> bool:
        """Delete a property"""
        try:
            result = self.client.table("properties").delete().eq("id", property_id).execute()
            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error deleting property: {str(e)}")
            return False
    
    # Income Operations
    def create_income(self, income: Income, user_id: str = None, organization_id: int = None) -> Optional[Income]:
        """Create a new income record"""
        try:
            income_dict = income.dict(exclude={'id', 'created_at', 'updated_at'})
            income_dict['transaction_date'] = income_dict['transaction_date'].isoformat()
            
            # Add user_id and organization_id for RLS compliance
            if user_id:
                income_dict['user_id'] = user_id
            if organization_id:
                income_dict['organization_id'] = organization_id
            
            result = self.client.table("income").insert(income_dict).execute()
            if result.data:
                return Income(**result.data[0])
            return None
        except Exception as e:
            st.error(f"Error creating income: {str(e)}")
            return None
    
    def get_income_by_property(self, property_id: int) -> List[Income]:
        """Get all income records for a property"""
        try:
            result = self.client.table("income").select("*").eq("property_id", property_id).order("transaction_date", desc=True).execute()
            return [Income(**inc) for inc in result.data]
        except Exception as e:
            st.error(f"Error fetching income: {str(e)}")
            return []
    
    def get_all_income(self) -> List[Income]:
        """Get all income records"""
        try:
            result = self.client.table("income").select("*").order("transaction_date", desc=True).execute()
            return [Income(**inc) for inc in result.data]
        except Exception as e:
            st.error(f"Error fetching income: {str(e)}")
            return []
    
    # Expense Operations
    def create_expense(self, expense: Expense, user_id: str = None, organization_id: int = None) -> Optional[Expense]:
        """Create a new expense record"""
        try:
            expense_dict = expense.dict(exclude={'id', 'created_at', 'updated_at'})
            expense_dict['transaction_date'] = expense_dict['transaction_date'].isoformat()
            
            # Add user_id and organization_id for RLS compliance
            if user_id:
                expense_dict['user_id'] = user_id
            if organization_id:
                expense_dict['organization_id'] = organization_id
            
            result = self.client.table("expenses").insert(expense_dict).execute()
            if result.data:
                return Expense(**result.data[0])
            return None
        except Exception as e:
            st.error(f"Error creating expense: {str(e)}")
            return None
    
    def get_expenses_by_property(self, property_id: int) -> List[Expense]:
        """Get all expense records for a property"""
        try:
            result = self.client.table("expenses").select("*").eq("property_id", property_id).order("transaction_date", desc=True).execute()
            return [Expense(**exp) for exp in result.data]
        except Exception as e:
            st.error(f"Error fetching expenses: {str(e)}")
            return []
    
    def get_all_expenses(self) -> List[Expense]:
        """Get all expense records"""
        try:
            result = self.client.table("expenses").select("*").order("transaction_date", desc=True).execute()
            return [Expense(**exp) for exp in result.data]
        except Exception as e:
            st.error(f"Error fetching expenses: {str(e)}")
            return []
    
    # Financial Summary Operations
    def get_property_financial_summary(self, property_id: int, start_date: datetime = None, end_date: datetime = None) -> dict:
        """Get financial summary for a property"""
        try:
            income_query = self.client.table("income").select("amount").eq("property_id", property_id)
            expense_query = self.client.table("expenses").select("amount").eq("property_id", property_id)
            
            if start_date:
                income_query = income_query.gte("transaction_date", start_date.isoformat())
                expense_query = expense_query.gte("transaction_date", start_date.isoformat())
            
            if end_date:
                income_query = income_query.lte("transaction_date", end_date.isoformat())
                expense_query = expense_query.lte("transaction_date", end_date.isoformat())
            
            income_result = income_query.execute()
            expense_result = expense_query.execute()
            
            total_income = sum(record['amount'] for record in income_result.data)
            total_expenses = sum(record['amount'] for record in expense_result.data)
            net_income = total_income - total_expenses
            
            return {
                'total_income': total_income,
                'total_expenses': total_expenses,
                'net_income': net_income,
                'roi': (net_income / total_income * 100) if total_income > 0 else 0
            }
        except Exception as e:
            st.error(f"Error calculating financial summary: {str(e)}")
            return {'total_income': 0, 'total_expenses': 0, 'net_income': 0, 'roi': 0}
    
    # Budget Operations
    def create_budget(self, budget: Budget) -> Optional[Budget]:
        """Create a new budget"""
        try:
            budget_dict = budget.dict(exclude={'id', 'created_at', 'updated_at'})
            budget_dict['start_date'] = budget_dict['start_date'].isoformat()
            budget_dict['end_date'] = budget_dict['end_date'].isoformat()
            
            result = self.client.table("budgets").insert(budget_dict).execute()
            if result.data:
                return Budget(**result.data[0])
            return None
        except Exception as e:
            st.error(f"Error creating budget: {str(e)}")
            return None
    
    def get_budgets_by_organization(self, organization_id: int) -> List[Budget]:
        """Get all budgets for an organization"""
        try:
            result = self.client.table("budgets").select("*").eq("organization_id", organization_id).order("created_at", desc=True).execute()
            return [Budget(**budget) for budget in result.data]
        except Exception as e:
            st.error(f"Error fetching budgets: {str(e)}")
            return []
    
    def get_budgets_by_property(self, property_id: int) -> List[Budget]:
        """Get all budgets for a specific property"""
        try:
            result = self.client.table("budgets").select("*").eq("property_id", property_id).order("created_at", desc=True).execute()
            return [Budget(**budget) for budget in result.data]
        except Exception as e:
            st.error(f"Error fetching property budgets: {str(e)}")
            return []
    
    def get_budget_by_id(self, budget_id: int) -> Optional[Budget]:
        """Get a specific budget by ID"""
        try:
            result = self.client.table("budgets").select("*").eq("id", budget_id).execute()
            if result.data:
                return Budget(**result.data[0])
            return None
        except Exception as e:
            st.error(f"Error fetching budget: {str(e)}")
            return None
    
    def update_budget(self, budget_id: int, budget: Budget) -> bool:
        """Update a budget"""
        try:
            budget_dict = budget.dict(exclude={'id', 'created_at', 'updated_at'})
            budget_dict['start_date'] = budget_dict['start_date'].isoformat()
            budget_dict['end_date'] = budget_dict['end_date'].isoformat()
            
            result = self.client.table("budgets").update(budget_dict).eq("id", budget_id).execute()
            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error updating budget: {str(e)}")
            return False
    
    def delete_budget(self, budget_id: int) -> bool:
        """Delete a budget"""
        try:
            result = self.client.table("budgets").delete().eq("id", budget_id).execute()
            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error deleting budget: {str(e)}")
            return False
    
    def create_budget_line(self, budget_line: BudgetLine) -> Optional[BudgetLine]:
        """Create a new budget line"""
        try:
            budget_line_dict = budget_line.dict(exclude={'id', 'created_at', 'updated_at'})
            
            result = self.client.table("budget_lines").insert(budget_line_dict).execute()
            if result.data:
                return BudgetLine(**result.data[0])
            return None
        except Exception as e:
            st.error(f"Error creating budget line: {str(e)}")
            return None
    
    def get_budget_lines(self, budget_id: int) -> List[BudgetLine]:
        """Get all budget lines for a budget"""
        try:
            result = self.client.table("budget_lines").select("*, categories(*)").eq("budget_id", budget_id).execute()
            budget_lines = []
            for row in result.data:
                budget_line_data = {k: v for k, v in row.items() if k != 'categories'}
                budget_lines.append(BudgetLine(**budget_line_data))
            return budget_lines
        except Exception as e:
            # If budget_lines table doesn't exist or has issues, return empty list
            # This prevents the error from breaking the budget overview
            return []
    
    def update_budget_line(self, budget_line_id: int, budget_line: BudgetLine) -> bool:
        """Update a budget line"""
        try:
            budget_line_dict = budget_line.dict(exclude={'id', 'created_at', 'updated_at'})
            
            result = self.client.table("budget_lines").update(budget_line_dict).eq("id", budget_line_id).execute()
            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error updating budget line: {str(e)}")
            return False
    
    def delete_budget_line(self, budget_line_id: int) -> bool:
        """Delete a budget line"""
        try:
            result = self.client.table("budget_lines").delete().eq("id", budget_line_id).execute()
            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error deleting budget line: {str(e)}")
            return False
    
    def get_budget_analysis(self, budget_id: int, start_date: datetime = None, end_date: datetime = None) -> dict:
        """Get budget analysis with actual vs budgeted amounts"""
        try:
            budget = self.get_budget_by_id(budget_id)
            if not budget:
                return {}
            
            budget_lines = self.get_budget_lines(budget_id)
            
            # Use budget's own dates if no dates provided
            if start_date is None:
                start_date = budget.start_date
            if end_date is None:
                end_date = budget.end_date
            
            # Get actual expenses for the budget period
            if budget.scope == BudgetScope.PROPERTY and budget.property_id:
                expenses_query = self.client.table("expenses").select("amount, expense_type, transaction_date").eq("property_id", budget.property_id)
            else:
                expenses_query = self.client.table("expenses").select("amount, expense_type, transaction_date").eq("organization_id", budget.organization_id)
            
            # Always filter by the budget period
            expenses_query = expenses_query.gte("transaction_date", start_date.isoformat())
            expenses_query = expenses_query.lte("transaction_date", end_date.isoformat())
            
            expenses_result = expenses_query.execute()
            
            # Calculate actual amounts by category
            actual_by_category = {}
            for expense in expenses_result.data:
                category = expense['expense_type']
                if category not in actual_by_category:
                    actual_by_category[category] = 0
                actual_by_category[category] += expense['amount']
            
            # Calculate budget vs actual
            # If no budget lines exist, use the main budget amount
            if budget_lines:
                total_budgeted = sum(line.budgeted_amount for line in budget_lines)
            else:
                total_budgeted = budget.budget_amount  # Use the main budget amount
            
            total_actual = sum(actual_by_category.values())
            
            analysis = {
                'budget': budget,
                'budget_lines': budget_lines,
                'total_budgeted': total_budgeted,
                'total_actual': total_actual,
                'variance': total_actual - total_budgeted,
                'variance_percentage': ((total_actual - total_budgeted) / total_budgeted * 100) if total_budgeted > 0 else 0,
                'actual_by_category': actual_by_category,
                'is_over_budget': total_actual > total_budgeted
            }
            
            return analysis
        except Exception as e:
            st.error(f"Error calculating budget analysis: {str(e)}")
            return {}
    
    # Recurring Transaction Operations
    def create_recurring_transaction(self, recurring_transaction: RecurringTransaction) -> Optional[RecurringTransaction]:
        """Create a new recurring transaction"""
        try:
            recurring_dict = recurring_transaction.dict(exclude={'id', 'created_at', 'updated_at'})
            recurring_dict['start_date'] = recurring_dict['start_date'].isoformat()
            if recurring_dict.get('end_date'):
                recurring_dict['end_date'] = recurring_dict['end_date'].isoformat()
            
            result = self.client.table("recurring_transactions").insert(recurring_dict).execute()
            if result.data:
                return RecurringTransaction(**result.data[0])
            return None
        except Exception as e:
            st.error(f"Error creating recurring transaction: {str(e)}")
            return None
    
    def get_recurring_transactions_by_organization(self, organization_id: int) -> List[RecurringTransaction]:
        """Get all recurring transactions for an organization"""
        try:
            result = self.client.table("recurring_transactions").select("*").eq("organization_id", organization_id).eq("is_active", True).execute()
            return [RecurringTransaction(**rt) for rt in result.data]
        except Exception as e:
            st.error(f"Error fetching recurring transactions: {str(e)}")
            return []
    
    def update_recurring_transaction(self, recurring_id: int, recurring_transaction: RecurringTransaction) -> bool:
        """Update a recurring transaction"""
        try:
            recurring_dict = recurring_transaction.dict(exclude={'id', 'created_at', 'updated_at'})
            recurring_dict['start_date'] = recurring_dict['start_date'].isoformat()
            if recurring_dict.get('end_date'):
                recurring_dict['end_date'] = recurring_dict['end_date'].isoformat()
            
            result = self.client.table("recurring_transactions").update(recurring_dict).eq("id", recurring_id).execute()
            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error updating recurring transaction: {str(e)}")
            return False
    
    def delete_recurring_transaction(self, recurring_id: int) -> bool:
        """Delete a recurring transaction"""
        try:
            result = self.client.table("recurring_transactions").delete().eq("id", recurring_id).execute()
            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error deleting recurring transaction: {str(e)}")
            return False
    
    # Pending Transaction Operations
    def create_pending_transaction(self, pending_transaction: PendingTransaction) -> Optional[PendingTransaction]:
        """Create a new pending transaction"""
        try:
            pending_dict = pending_transaction.dict(exclude={'id', 'created_at', 'updated_at'})
            pending_dict['transaction_date'] = pending_dict['transaction_date'].isoformat()
            
            result = self.client.table("pending_transactions").insert(pending_dict).execute()
            if result.data:
                return PendingTransaction(**result.data[0])
            return None
        except Exception as e:
            st.error(f"Error creating pending transaction: {str(e)}")
            return None
    
    def get_pending_transactions_by_organization(self, organization_id: int, transaction_type: str = None) -> List[PendingTransaction]:
        """Get all pending transactions for an organization"""
        try:
            query = self.client.table("pending_transactions").select("*").eq("organization_id", organization_id)
            if transaction_type:
                query = query.eq("transaction_type", transaction_type)
            
            result = query.order("transaction_date", desc=True).execute()
            return [PendingTransaction(**pt) for pt in result.data]
        except Exception as e:
            st.error(f"Error fetching pending transactions: {str(e)}")
            return []
    
    def update_pending_transaction(self, pending_id: int, pending_transaction: PendingTransaction) -> bool:
        """Update a pending transaction"""
        try:
            pending_dict = pending_transaction.dict(exclude={'id', 'created_at', 'updated_at'})
            pending_dict['transaction_date'] = pending_dict['transaction_date'].isoformat()
            
            result = self.client.table("pending_transactions").update(pending_dict).eq("id", pending_id).execute()
            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error updating pending transaction: {str(e)}")
            return False
    
    def delete_pending_transaction(self, pending_id: int) -> bool:
        """Delete a pending transaction"""
        try:
            result = self.client.table("pending_transactions").delete().eq("id", pending_id).execute()
            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error deleting pending transaction: {str(e)}")
            return False
    
    def confirm_pending_transaction(self, pending_id: int) -> bool:
        """Confirm a pending transaction by moving it to the appropriate table"""
        try:
            # Get the pending transaction
            result = self.client.table("pending_transactions").select("*").eq("id", pending_id).execute()
            if not result.data:
                return False
            
            pending_data = result.data[0]
            
            # Create the appropriate transaction based on type
            if pending_data['transaction_type'] == 'income':
                income_data = {
                    'organization_id': pending_data['organization_id'],
                    'property_id': pending_data['property_id'],
                    'amount': pending_data['amount'],
                    'income_type': pending_data['income_type'],
                    'description': pending_data['description'],
                    'transaction_date': pending_data['transaction_date']
                }
                self.client.table("income").insert(income_data).execute()
            else:  # expense
                expense_data = {
                    'organization_id': pending_data['organization_id'],
                    'property_id': pending_data['property_id'],
                    'amount': pending_data['amount'],
                    'expense_type': pending_data['expense_type'],
                    'description': pending_data['description'],
                    'transaction_date': pending_data['transaction_date']
                }
                self.client.table("expenses").insert(expense_data).execute()
            
            # Delete the pending transaction
            self.client.table("pending_transactions").delete().eq("id", pending_id).execute()
            return True
        except Exception as e:
            st.error(f"Error confirming pending transaction: {str(e)}")
            return False
