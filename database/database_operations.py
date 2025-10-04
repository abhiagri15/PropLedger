from database.supabase_client import get_supabase_client
from database.models import Property, Income, Expense, Category, Organization, UserOrganization
from typing import List, Optional
import streamlit as st
from datetime import datetime

class DatabaseOperations:
    def __init__(self):
        self.client = get_supabase_client()
    
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
