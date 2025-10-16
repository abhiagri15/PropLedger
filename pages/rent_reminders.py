"""
Rent Reminders page for PropLedger
Extracted from app_auth.py for better maintainability
"""

import streamlit as st
from datetime import date
from database.database_operations import DatabaseOperations

def render_rent_reminders():
    """Render the Rent Reminders page"""
    db = DatabaseOperations()

    st.markdown('<h1 class="main-header">🔔 Rent Reminders</h1>', unsafe_allow_html=True)

    # Check if demo mode
    is_demo_mode = False
    if st.session_state.user:
        if hasattr(st.session_state.user, 'email'):
            is_demo_mode = getattr(st.session_state.user, 'email', '') == 'demo@example.com'
        else:
            is_demo_mode = st.session_state.user.get('email', '') == 'demo@example.com'

    if is_demo_mode:
        # Demo mode - show sample rent reminder data
        st.markdown('<div class="info-box">🎯 <strong>Demo Mode</strong> - Showing sample rent reminder data. Sign up to manage your own reminders!</div>', unsafe_allow_html=True)

        # Demo rent reminders
        st.markdown("### Sample Rent Reminders")

        demo_reminders = [
            {
                'property': 'Downtown Apartment',
                'month': 'January 2024',
                'status': 'Due',
                'reminder_count': 2,
                'next_reminder': '2024-01-15',
                'rent_recorded': False
            },
            {
                'property': 'Suburban House',
                'month': 'January 2024',
                'status': 'Completed',
                'reminder_count': 1,
                'next_reminder': 'N/A',
                'rent_recorded': True
            },
            {
                'property': 'Commercial Space',
                'month': 'January 2024',
                'status': 'Overdue',
                'reminder_count': 4,
                'next_reminder': '2024-01-20',
                'rent_recorded': False
            }
        ]

        for reminder in demo_reminders:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

                with col1:
                    st.write(f"**{reminder['property']}**")
                    st.caption(f"Month: {reminder['month']}")

                with col2:
                    if reminder['status'] == 'Completed':
                        st.success("✅ Rent Recorded")
                    elif reminder['status'] == 'Due':
                        st.warning("⏰ Due Soon")
                    else:
                        st.error("🚨 Overdue")

                with col3:
                    st.write(f"Reminders: {reminder['reminder_count']}/6")
                    if not reminder['rent_recorded']:
                        st.caption(f"Next: {reminder['next_reminder']}")

                with col4:
                    if not reminder['rent_recorded']:
                        if st.button("Mark as Recorded", key=f"demo_record_{reminder['property']}"):
                            st.success("Demo: Rent marked as recorded!")
                    else:
                        st.info("Rent recorded")

                st.markdown("---")

        # Demo reminder settings
        st.markdown("### Reminder Settings (Demo)")

        with st.form("demo_reminder_settings"):
            col1, col2 = st.columns(2)

            with col1:
                st.selectbox("Property", ["Downtown Apartment", "Suburban House", "Commercial Space"], key="demo_reminder_property")
                st.selectbox("Month", ["January 2024", "February 2024", "March 2024"], key="demo_reminder_month")

            with col2:
                st.number_input("Reminder Frequency (days)", value=5, min_value=1, max_value=30, key="demo_reminder_frequency")
                st.number_input("Max Reminders", value=6, min_value=1, max_value=12, key="demo_max_reminders")

            if st.form_submit_button("Create Demo Reminder", type="primary"):
                st.success("Demo reminder created! Reminders will be sent every 5 days after the 5th of each month.")
                st.info("Sign up to create real rent reminders!")
        return

    # Get selected organization
    selected_org_id = st.session_state.get('selected_organization')
    if not selected_org_id:
        st.error("Please select an organization first.")
        return

    # Import rent reminder service
    try:
        from services.rent_reminder_service import RentReminderService
        reminder_service = RentReminderService()
    except ImportError:
        st.error("Rent reminder service not available. Please check the installation.")
        return

    # Check if rent_reminders table exists
    try:
        # Try to query the table to see if it exists
        test_result = reminder_service.db.supabase.table("rent_reminders").select("id").limit(1).execute()
    except Exception as e:
        if "Could not find the table" in str(e):
            st.error("❌ **Rent Reminders table not found in database!**")
            st.markdown("""
            **To set up the Rent Reminders feature, you need to:**

            1. **Go to your Supabase Dashboard**
            2. **Navigate to SQL Editor**
            3. **Run the complete setup script:**

            ```sql
            -- Copy and paste the contents of database/setup_rent_reminders_complete.sql
            ```

            4. **Refresh this page after running the SQL**

            **Alternative setup:**
            - Run `python scripts/setup_rent_reminders.py` in your terminal
            """)
            return
        else:
            st.error(f"Database error: {str(e)}")
            return

    # Get organization name
    org = db.get_organization_by_id(selected_org_id)
    org_name = org.name if org else "Unknown Organization"

    st.info(f"Rent Reminders for: **{org_name}**")

    # Create monthly reminders button
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        if st.button("🔄 Create Monthly Reminders", type="primary"):
            with st.spinner("Creating reminders for all properties..."):
                # Get user ID from session state user object
                user_id = None
                if st.session_state.user:
                    if hasattr(st.session_state.user, 'id'):
                        user_id = st.session_state.user.id
                    elif isinstance(st.session_state.user, dict):
                        user_id = st.session_state.user.get('id')

                if not user_id:
                    st.error("Unable to get user ID. Please log out and log back in.")
                    return

                created_count = reminder_service.create_monthly_reminders(
                    selected_org_id, user_id
                )
                if created_count > 0:
                    st.success(f"Created {created_count} new reminders for this month!")
                else:
                    st.info("No new reminders needed - all properties already have reminders for this month.")

    with col2:
        if st.button("📧 Process Due Reminders"):
            with st.spinner("Processing due reminders..."):
                processed_count = reminder_service.process_due_reminders()
                if processed_count > 0:
                    st.success(f"Processed {processed_count} due reminders!")
                else:
                    st.info("No reminders are due at this time.")

    with col3:
        if st.button("🔄 Refresh"):
            st.rerun()

    st.markdown("---")

    # Get user ID for RLS compliance
    user_id = None
    if st.session_state.user:
        if hasattr(st.session_state.user, 'id'):
            user_id = st.session_state.user.id
        elif isinstance(st.session_state.user, dict):
            user_id = st.session_state.user.get('id')

    # Get properties for the organization
    properties = db.get_properties_by_organization(selected_org_id)

    if not properties:
        st.info(f"No properties found for {org_name}. Please add a property first.")
    else:
        # Show reminders for each property
        current_date = date.today()
        current_month = current_date.month
        current_year = current_date.year

        st.markdown("### Current Month Reminders")

        for property_obj in properties:
            with st.expander(f"🏠 {property_obj.address}", expanded=False):
                # Get reminder status for this property
                status = reminder_service.get_reminder_status(
                    property_obj.id, current_month, current_year
                )

                col1, col2, col3 = st.columns(3)

                with col1:
                    if status['rent_recorded']:
                        st.success("✅ Rent Recorded")
                    elif status['is_due']:
                        st.error("🚨 Reminder Due")
                    else:
                        st.info("⏰ Pending")

                with col2:
                    if status['has_reminder']:
                        st.write(f"Reminders: {status['reminder_count']}/6")
                        if status['next_reminder']:
                            st.caption(f"Next: {status['next_reminder']}")
                    else:
                        st.write("No reminders set")

                with col3:
                    if not status['rent_recorded']:
                        if st.button("Mark Rent as Recorded", key=f"record_{property_obj.id}"):
                            reminder_service.mark_rent_recorded(
                                property_obj.id, current_month, current_year, selected_org_id, user_id
                            )
                    else:
                        st.info("Rent already recorded")

        # Historical reminders
        st.markdown("### Historical Reminders")

        # Get all reminders for this organization
        try:
            result = reminder_service.db.supabase.table("rent_reminders").select("*").eq(
                "organization_id", selected_org_id
            ).order("reminder_year", desc=True).order("reminder_month", desc=True).execute()

            if result.data:
                reminders_data = []
                for reminder_data in result.data:
                    # Get property name
                    property_obj = next((p for p in properties if p.id == reminder_data['property_id']), None)
                    property_name = property_obj.address if property_obj else f"Property ID: {reminder_data['property_id']}"

                    reminders_data.append({
                        'property': property_name,
                        'month': f"{reminder_data['reminder_month']:02d}/{reminder_data['reminder_year']}",
                        'status': 'Completed' if reminder_data['is_rent_recorded'] else 'Pending',
                        'reminder_count': reminder_data['reminder_count'],
                        'last_sent': reminder_data['last_sent_date'],
                        'created': reminder_data['created_at']
                    })

                # Display in a table
                if reminders_data:
                    st.dataframe(
                        reminders_data,
                        column_config={
                            "property": "Property",
                            "month": "Month",
                            "status": "Status",
                            "reminder_count": "Reminders Sent",
                            "last_sent": "Last Sent",
                            "created": "Created"
                        },
                        use_container_width=True
                    )
                else:
                    st.info("No historical reminders found.")
            else:
                st.info("No reminders found for this organization.")

        except Exception as e:
            st.error(f"Error fetching historical reminders: {str(e)}")
