"""
Rent Reminder Service
Handles rent reminder scheduling and management
"""
from datetime import datetime, date, timedelta
from typing import List, Optional
import streamlit as st
from database.database_operations import DatabaseOperations
from database.models import RentReminder, Property, Income
from config import get_supabase_url, get_supabase_key

class RentReminderService:
    def __init__(self):
        self.db = DatabaseOperations()
    
    def create_rent_reminder(self, property_id: int, organization_id: int, user_id: str, 
                           month: int, year: int) -> Optional[RentReminder]:
        """Create a new rent reminder for a property and month"""
        try:
            # Calculate reminder dates
            reminder_date = date(year, month, 5)  # Start on 5th of month
            next_reminder_date = reminder_date + timedelta(days=5)  # First reminder after 5 days
            
            reminder_data = {
                "property_id": property_id,
                "organization_id": organization_id,
                "user_id": user_id,
                "reminder_month": month,
                "reminder_year": year,
                "reminder_date": reminder_date.isoformat(),
                "next_reminder_date": next_reminder_date.isoformat(),
                "is_rent_recorded": False,
                "reminder_count": 0,
                "max_reminders": 6
            }
            
            result = self.db.supabase.table("rent_reminders").insert(reminder_data).execute()
            
            if result.data:
                return RentReminder(**result.data[0])
            return None
            
        except Exception as e:
            st.error(f"Error creating rent reminder: {str(e)}")
            return None
    
    def get_reminders_for_property(self, property_id: int, month: int, year: int) -> List[RentReminder]:
        """Get all reminders for a specific property and month"""
        try:
            result = self.db.supabase.table("rent_reminders").select("*").eq(
                "property_id", property_id
            ).eq("reminder_month", month).eq("reminder_year", year).execute()
            
            return [RentReminder(**reminder) for reminder in result.data]
        except Exception as e:
            if "Could not find the table" in str(e):
                # Table doesn't exist, return empty list
                return []
            st.error(f"Error fetching reminders: {str(e)}")
            return []
    
    def get_due_reminders(self) -> List[RentReminder]:
        """Get all reminders that are due to be sent"""
        try:
            today = date.today().isoformat()
            # Use raw SQL query to properly compare columns
            result = self.db.supabase.rpc("get_due_reminders").execute()
            
            reminders = []
            for reminder_data in result.data:
                # Convert the result to RentReminder object
                reminder_dict = {
                    "id": reminder_data.get("id"),
                    "property_id": reminder_data.get("property_id"),
                    "organization_id": reminder_data.get("organization_id"),
                    "user_id": reminder_data.get("user_id"),
                    "reminder_month": reminder_data.get("reminder_month"),
                    "reminder_year": reminder_data.get("reminder_year"),
                    "reminder_date": reminder_data.get("reminder_date"),
                    "last_sent_date": reminder_data.get("last_sent_date"),
                    "next_reminder_date": reminder_data.get("next_reminder_date"),
                    "is_rent_recorded": reminder_data.get("is_rent_recorded"),
                    "reminder_count": reminder_data.get("reminder_count"),
                    "max_reminders": reminder_data.get("max_reminders"),
                    "created_at": reminder_data.get("created_at"),
                    "updated_at": reminder_data.get("updated_at")
                }
                reminders.append(RentReminder(**reminder_dict))
            
            return reminders
        except Exception as e:
            if "Could not find the table" in str(e):
                # Table doesn't exist, return empty list
                return []
            st.error(f"Error fetching due reminders: {str(e)}")
            return []
    
    def update_reminder_sent(self, reminder_id: int) -> bool:
        """Update reminder after it has been sent"""
        try:
            today = date.today()
            next_reminder = today + timedelta(days=5)
            
            update_data = {
                "last_sent_date": today.isoformat(),
                "next_reminder_date": next_reminder.isoformat(),
                "reminder_count": self.db.supabase.rpc("increment_reminder_count", {"reminder_id": reminder_id}).execute()
            }
            
            result = self.db.supabase.table("rent_reminders").update(update_data).eq("id", reminder_id).execute()
            return len(result.data) > 0
            
        except Exception as e:
            st.error(f"Error updating reminder: {str(e)}")
            return False
    
    def mark_rent_recorded(self, property_id: int, month: int, year: int, organization_id: int = None, user_id: str = None) -> bool:
        """Mark rent as recorded for a property and month"""
        try:
            # First check if the table exists
            try:
                test_result = self.db.supabase.table("rent_reminders").select("id").limit(1).execute()
            except Exception as e:
                if "Could not find the table" in str(e):
                    st.error("❌ Rent reminders table not found. Please set up the database first.")
                    st.markdown("""
                    **To set up the Rent Reminders feature:**
                    1. Go to your Supabase Dashboard
                    2. Navigate to SQL Editor
                    3. Run the complete setup script:
                    ```sql
                    -- Copy and paste the contents of database/setup_rent_reminders_complete.sql
                    ```
                    4. Refresh this page after running the SQL
                    """)
                    return False
                else:
                    st.error(f"Database error: {str(e)}")
                    return False
            
            # Check if there are any reminders for this property and month
            existing_reminders = self.get_reminders_for_property(property_id, month, year)
            
            if not existing_reminders:
                # Create a reminder first if none exists
                if organization_id is None or user_id is None:
                    st.error("Organization ID and User ID are required to create reminders")
                    return False
                    
                current_date = date.today()
                reminder = self.create_rent_reminder(
                    property_id=property_id,
                    organization_id=organization_id,
                    user_id=user_id,
                    month=month,
                    year=year
                )
                if not reminder:
                    st.error("Failed to create reminder record")
                    return False
            
            # Now mark as recorded
            update_data = {"is_rent_recorded": True}
            
            result = self.db.supabase.table("rent_reminders").update(update_data).eq(
                "property_id", property_id
            ).eq("reminder_month", month).eq("reminder_year", year).execute()
            
            if len(result.data) > 0:
                st.success("✅ Rent marked as recorded!")
                # Force a page refresh to show updated status
                st.rerun()
                return True
            else:
                st.error("No reminders found to update for this property and month")
                return False
            
        except Exception as e:
            st.error(f"Error marking rent as recorded: {str(e)}")
            return False
    
    def check_rent_recorded(self, property_id: int, month: int, year: int) -> bool:
        """Check if rent has been recorded for a property and month"""
        try:
            # First check if there's a rent reminder marked as recorded
            try:
                reminder_result = self.db.supabase.table("rent_reminders").select("is_rent_recorded").eq(
                    "property_id", property_id
                ).eq("reminder_month", month).eq("reminder_year", year).execute()
                
                if reminder_result.data and any(reminder['is_rent_recorded'] for reminder in reminder_result.data):
                    return True
            except Exception as e:
                # If rent_reminders table doesn't exist or has issues, continue to check income table
                pass
            
            # Also check if there's income record for this property and month
            result = self.db.supabase.table("income").select("id").eq(
                "property_id", property_id
            ).eq("income_type", "rent").gte(
                "transaction_date", f"{year}-{month:02d}-01"
            ).lt("transaction_date", f"{year}-{month+1:02d}-01" if month < 12 else f"{year+1}-01-01").execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            st.error(f"Error checking rent recorded: {str(e)}")
            return False
    
    def get_reminder_status(self, property_id: int, month: int, year: int) -> dict:
        """Get reminder status for a property and month"""
        try:
            reminders = self.get_reminders_for_property(property_id, month, year)
            rent_recorded = self.check_rent_recorded(property_id, month, year)
            
            if not reminders:
                return {
                    "has_reminder": False,
                    "rent_recorded": rent_recorded,
                    "next_reminder": None,
                    "reminder_count": 0,
                    "is_due": False
                }
            
            latest_reminder = max(reminders, key=lambda r: r.reminder_count)
            
            # Convert next_reminder_date to date for comparison if it's a datetime
            next_reminder_date = latest_reminder.next_reminder_date
            if hasattr(next_reminder_date, 'date'):
                next_reminder_date = next_reminder_date.date()
            elif isinstance(next_reminder_date, str):
                next_reminder_date = datetime.fromisoformat(next_reminder_date).date()
            
            return {
                "has_reminder": True,
                "rent_recorded": rent_recorded,
                "next_reminder": latest_reminder.next_reminder_date,
                "reminder_count": latest_reminder.reminder_count,
                "is_due": next_reminder_date <= date.today() and not rent_recorded
            }
        except Exception as e:
            st.error(f"Error getting reminder status: {str(e)}")
            return {
                "has_reminder": False,
                "rent_recorded": False,
                "next_reminder": None,
                "reminder_count": 0,
                "is_due": False
            }
    
    def create_monthly_reminders(self, organization_id: int, user_id: str) -> int:
        """Create reminders for all properties in an organization for the current month"""
        try:
            # Get all properties for the organization
            properties = self.db.get_properties_by_organization(organization_id)
            current_date = date.today()
            current_month = current_date.month
            current_year = current_date.year
            
            reminders_created = 0
            
            for property_obj in properties:
                # Check if reminder already exists for this month
                existing_reminders = self.get_reminders_for_property(
                    str(property_obj.id), current_month, current_year
                )
                
                if not existing_reminders:
                    # Create new reminder
                    reminder = self.create_rent_reminder(
                        str(property_obj.id), organization_id, user_id, 
                        current_month, current_year
                    )
                    if reminder:
                        reminders_created += 1
            
            return reminders_created
            
        except Exception as e:
            st.error(f"Error creating monthly reminders: {str(e)}")
            return 0
    
    def send_reminder_notification(self, reminder: RentReminder, property: Property) -> bool:
        """Send a reminder notification (placeholder for email/SMS integration)"""
        try:
            # This is where you would integrate with email/SMS services
            # For now, we'll just log the reminder
            st.info(f"🔔 Rent Reminder: {property.address} - Month {reminder.reminder_month}/{reminder.reminder_year}")
            st.info(f"Reminder #{reminder.reminder_count + 1} of {reminder.max_reminders}")
            
            # Update the reminder
            return self.update_reminder_sent(reminder.id)
            
        except Exception as e:
            st.error(f"Error sending reminder: {str(e)}")
            return False
    
    def process_due_reminders(self) -> int:
        """Process all due reminders"""
        due_reminders = self.get_due_reminders()
        processed = 0
        
        for reminder in due_reminders:
            # Get property details
            property_obj = self.db.get_property_by_id(reminder.property_id)
            if property_obj:
                # Send reminder
                if self.send_reminder_notification(reminder, property_obj):
                    processed += 1
        
        return processed
