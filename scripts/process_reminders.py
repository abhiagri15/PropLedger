#!/usr/bin/env python3
"""
Background script to process rent reminders
This script should be run as a scheduled task (cron job on Linux/Mac, Task Scheduler on Windows)
"""
import sys
import os
from datetime import datetime, date
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.rent_reminder_service import RentReminderService
from config import get_supabase_url, get_supabase_key

def main():
    """Main function to process due reminders"""
    print(f"[{datetime.now()}] Starting rent reminder processing...")
    
    try:
        # Initialize the reminder service
        reminder_service = RentReminderService()
        
        # Process due reminders
        processed_count = reminder_service.process_due_reminders()
        
        print(f"[{datetime.now()}] Processed {processed_count} due reminders")
        
        if processed_count > 0:
            print(f"[{datetime.now()}] Successfully processed {processed_count} reminders")
        else:
            print(f"[{datetime.now()}] No reminders were due at this time")
            
    except Exception as e:
        print(f"[{datetime.now()}] Error processing reminders: {str(e)}")
        sys.exit(1)
    
    print(f"[{datetime.now()}] Rent reminder processing completed")

if __name__ == "__main__":
    main()

