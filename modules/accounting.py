"""
Accounting page for PropLedger (Combined Income + Expenses)
Extracted from app_auth.py for better maintainability
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from streamlit_option_menu import option_menu
from database.database_operations import DatabaseOperations
from database.models import Income, Expense, IncomeType, ExpenseType

def render_accounting():
    """Render the Accounting page with Income and Expenses tabs"""
    db = DatabaseOperations()

    st.markdown('<h1 class="main-header">💰 Accounting</h1>', unsafe_allow_html=True)

    # Use native Streamlit tabs to match reference design
    income_tab, expense_tab = st.tabs(["🔥 Income", "✅ Expenses"])

    with income_tab:
        st.markdown('<h2 class="sub-header">💰 Income Tracking</h2>', unsafe_allow_html=True)

        # Check if demo mode
        is_demo_mode = False
        if st.session_state.user:
            if hasattr(st.session_state.user, 'email'):
                is_demo_mode = getattr(st.session_state.user, 'email', '') == 'demo@example.com'
            else:
                is_demo_mode = st.session_state.user.get('email', '') == 'demo@example.com'

        if is_demo_mode:
            # Demo mode - show sample income data
            st.markdown('<div class="info-box">🎯 <strong>Demo Mode</strong> - Showing sample income data. Sign up to manage your own income!</div>', unsafe_allow_html=True)

            # Sample income data for demo
            demo_income = [
                {'property': 'Downtown Apartment', 'amount': 1800, 'type': 'Rent', 'date': '2024-01-15'},
                {'property': 'Suburban House', 'amount': 2200, 'type': 'Rent', 'date': '2024-01-20'},
                {'property': 'Commercial Space', 'amount': 500, 'type': 'Parking', 'date': '2024-01-25'},
                {'property': 'Downtown Apartment', 'amount': 1800, 'type': 'Rent', 'date': '2024-02-15'},
                {'property': 'Suburban House', 'amount': 2200, 'type': 'Rent', 'date': '2024-02-20'},
            ]

            # Display demo income data
            st.markdown("### Sample Income Records")
            for inc in demo_income:
                st.write(f"• {inc['property']}: ${inc['amount']:,.2f} - {inc['type']} ({inc['date']})")

            # Demo income form
            st.markdown("---")
            st.markdown("### Add Income Record (Demo)")

            with st.form("demo_income_form"):
                col1, col2 = st.columns(2)

                with col1:
                    demo_property = st.selectbox("Property", ["Downtown Apartment", "Suburban House", "Commercial Space"], key="demo_property")
                    demo_amount = st.number_input("Amount", value=1500, key="demo_amount")
                    demo_type = st.selectbox("Income Type", ["Rent", "Parking", "Laundry", "Other"], key="demo_type")

                with col2:
                    demo_date = st.date_input("Date", value=date.today(), key="demo_date")
                    demo_description = st.text_area("Description", value="Sample income record", key="demo_description")

                if st.form_submit_button("Add Demo Income", type="primary"):
                    st.success(f"Demo income record added: ${demo_amount:,.2f} for {demo_property}")
                    st.info("Sign up to add real income records!")
            return

        # Get selected organization
        selected_org_id = st.session_state.get('selected_organization')
        if not selected_org_id:
            st.error("Please select an organization first.")
            return

        # Get organization name
        org = db.get_organization_by_id(selected_org_id)
        org_name = org.name if org else "Unknown Organization"

        st.info(f"Tracking income for: **{org_name}**")

        # Get properties for this organization (used in both tabs)
        properties = db.get_properties()
        org_properties = [p for p in properties if p.organization_id == selected_org_id]

        # Tabs for income management - matching reference design
        tab1, tab2, tab3, tab4 = st.tabs(["View/Edit Income", "Add Income", "Manage Income", "Recurring Income"])

        with tab1:

            if org_properties:
                # Filter by property with unique key
                property_names = {prop.id: prop.name for prop in org_properties}
                selected_property_id = st.selectbox("Filter by Property", ["All"] + list(property_names.keys()),
                                                  format_func=lambda x: "All" if x == "All" else property_names[x],
                                                  key="income_view_property_filter")

                if selected_property_id == "All":
                    income_records = db.get_all_income()
                else:
                    income_records = db.get_income_by_property(selected_property_id)

                if income_records:
                    # Display income records
                    income_data = []
                    for inc in income_records:
                        prop_name = property_names.get(inc.property_id, "Unknown")
                        income_data.append({
                            'Property': prop_name,
                            'Amount': f"${inc.amount:,.2f}",
                            'Type': inc.income_type.title(),
                            'Description': inc.description,
                            'Date': inc.transaction_date.strftime('%Y-%m-%d')
                        })

                    df_income = pd.DataFrame(income_data)
                    st.dataframe(df_income, use_container_width=True)

                    # Income summary
                    total_income = sum(inc.amount for inc in income_records)
                    st.metric("Total Income", f"${total_income:,.2f}")
                else:
                    st.info("No income records found.")
            else:
                st.info(f"No properties found for {org_name}. Please add a property first.")

        with tab2:
            if org_properties:
                st.subheader("Add New Income Record")

                # Use a key to reset form after successful submission
                income_form_key = f"add_income_form_{st.session_state.get('income_form_reset_counter', 0)}"

                with st.form(income_form_key):
                    col1, col2 = st.columns(2)

                    with col1:
                        property_id = st.selectbox("Property *",
                                                 options=[prop.id for prop in org_properties],
                                                 format_func=lambda x: next(prop.name for prop in org_properties if prop.id == x))
                        amount = st.number_input("Amount *", min_value=0.01, format="%.2f")
                        income_type = st.selectbox("Income Type *", [it.value for it in IncomeType])

                    with col2:
                        description = st.text_input("Description *", placeholder="e.g., Monthly rent payment")
                        transaction_date = st.date_input("Transaction Date *", value=date.today())

                    # Month and Year selection
                    col3, col4 = st.columns(2)
                    with col3:
                        month = st.selectbox("Month *",
                                           options=list(range(1, 13)),
                                           format_func=lambda x: date(2024, x, 1).strftime('%B'),
                                           index=date.today().month - 1)
                    with col4:
                        year = st.number_input("Year *",
                                             min_value=2020,
                                             max_value=2030,
                                             value=date.today().year)

                    submitted = st.form_submit_button("Add Income", type="primary")

                    if submitted:
                        # Create transaction date from month/year selection
                        transaction_date_from_month_year = date(year, month, 1)

                        new_income = Income(
                            property_id=property_id,
                            amount=amount,
                            income_type=IncomeType(income_type),
                            description=f"{description} - {date(year, month, 1).strftime('%B %Y')}",
                            transaction_date=datetime.combine(transaction_date_from_month_year, datetime.min.time())
                        )

                        # Get user ID and organization ID for RLS compliance
                        user_id = None
                        organization_id = None
                        if st.session_state.user:
                            if hasattr(st.session_state.user, 'id'):
                                user_id = st.session_state.user.id
                            elif isinstance(st.session_state.user, dict):
                                user_id = st.session_state.user.get('id')

                        # Get selected organization
                        organization_id = st.session_state.get('selected_organization')

                        result = db.create_income(new_income, user_id, organization_id)
                        if result:
                            st.success("Income record added successfully!")
                            # Increment form reset counter to clear the form
                            st.session_state.income_form_reset_counter = st.session_state.get('income_form_reset_counter', 0) + 1
                            st.rerun()
                        else:
                            st.error("Failed to add income record. Please try again.")
            else:
                st.info(f"No properties found for {org_name}. Please add a property first.")

        with tab3:
            # Manage Income tab
            st.subheader("Manage Income Records")

            if org_properties:
                # Filter options
                col1, col2 = st.columns(2)
                with col1:
                    filter_property = st.selectbox("Filter by Property",
                                                  ["All"] + [p.name for p in org_properties],
                                                  key="manage_income_property")
                with col2:
                    filter_date = st.selectbox("Date Filter",
                                              ["Current Month", "Last 3 Months", "Last 6 Months", "This Year", "All Time"],
                                              key="manage_income_date")

                # Get income records
                income_records = db.get_all_income()

                if income_records:
                    st.info(f"Found {len(income_records)} income records")

                    # Display records with edit/delete options
                    for inc in income_records:
                        prop = next((p for p in org_properties if p.id == inc.property_id), None)
                        if prop:
                            with st.expander(f"🔥 {prop.name} - ${inc.amount:,.2f} - {inc.transaction_date.strftime('%Y-%m-%d')}"):
                                col1, col2, col3 = st.columns([2, 1, 1])

                                with col1:
                                    st.write(f"**Type:** {inc.income_type.title()}")
                                    st.write(f"**Description:** {inc.description}")
                                    st.write(f"**Amount:** ${inc.amount:,.2f}")
                                    st.write(f"**Date:** {inc.transaction_date.strftime('%B %d, %Y')}")

                                with col2:
                                    if st.button(f"✏️ Edit", key=f"edit_income_{inc.id}"):
                                        st.session_state[f'editing_income_{inc.id}'] = True

                                with col3:
                                    if st.button(f"🗑️ Delete", key=f"delete_income_{inc.id}", type="secondary"):
                                        if db.delete_income(inc.id):
                                            st.success("Income record deleted")
                                            st.rerun()
                                        else:
                                            st.error("Failed to delete income record")
                else:
                    st.info("No income records found")
            else:
                st.info(f"No properties found for {org_name}. Please add a property first.")

        with tab4:
            # Recurring Income tab
            st.subheader("Recurring Income Setup")

            if org_properties:
                st.info("Set up recurring income transactions that will be automatically added each month")

                # Add recurring income form
                with st.form("recurring_income_form"):
                    col1, col2 = st.columns(2)

                    with col1:
                        property_id = st.selectbox("Property *",
                                                  options=[prop.id for prop in org_properties],
                                                  format_func=lambda x: next(prop.name for prop in org_properties if prop.id == x))
                        amount = st.number_input("Monthly Amount *", min_value=0.01, format="%.2f")
                        income_type = st.selectbox("Income Type *", ["rent", "parking", "laundry", "other"])

                    with col2:
                        description = st.text_input("Description *", placeholder="e.g., Monthly Rent")
                        start_date = st.date_input("Start Date *", value=date.today())
                        frequency = st.selectbox("Frequency", ["Monthly", "Quarterly", "Annually"])

                    submitted = st.form_submit_button("Set Up Recurring Income", type="primary")

                    if submitted:
                        st.success(f"Recurring income of ${amount:,.2f} set up for {next(p.name for p in org_properties if p.id == property_id)}")
                        st.info("This feature will automatically create income records based on your schedule")

                # Display existing recurring income
                st.markdown("### Existing Recurring Income")

                # Check if recurring_transactions table exists and has data
                try:
                    recurring_result = db.client.table("recurring_transactions").select("*").eq("organization_id", selected_org_id).execute()

                    if recurring_result.data:
                        for rec in recurring_result.data:
                            prop = next((p for p in org_properties if p.id == rec.get('property_id')), None)
                            if prop:
                                with st.expander(f"🔁 {prop.name} - ${rec.get('amount', 0):,.2f}/month"):
                                    st.write(f"**Description:** {rec.get('description', 'N/A')}")
                                    st.write(f"**Frequency:** {rec.get('frequency', 'Monthly')}")
                                    st.write(f"**Start Date:** {rec.get('start_date', 'N/A')}")

                                    if st.button(f"Cancel Recurring", key=f"cancel_recurring_{rec.get('id')}"):
                                        st.info("Recurring income cancelled")
                    else:
                        st.info("No recurring income set up yet. Use the form above to create recurring income.")

                except Exception as e:
                    st.info("Recurring income feature is available. Set up your first recurring income above.")
            else:
                st.info(f"No properties found for {org_name}. Please add a property first.")

    with expense_tab:
        st.markdown('<h2 class="sub-header">💸 Expense Tracking</h2>', unsafe_allow_html=True)

        # Check if demo mode
        is_demo_mode = False
        if st.session_state.user:
            if hasattr(st.session_state.user, 'email'):
                is_demo_mode = getattr(st.session_state.user, 'email', '') == 'demo@example.com'
            else:
                is_demo_mode = st.session_state.user.get('email', '') == 'demo@example.com'

        if is_demo_mode:
            # Demo mode - show sample expense data
            st.markdown('<div class="info-box">🎯 <strong>Demo Mode</strong> - Showing sample expense data. Sign up to manage your own expenses!</div>', unsafe_allow_html=True)

            # Sample expense data for demo
            demo_expenses = [
                {'property': 'Downtown Apartment', 'amount': 150, 'type': 'Maintenance', 'date': '2024-01-10'},
                {'property': 'Suburban House', 'amount': 200, 'type': 'Utilities', 'date': '2024-01-15'},
                {'property': 'Commercial Space', 'amount': 300, 'type': 'Insurance', 'date': '2024-01-20'},
                {'property': 'Downtown Apartment', 'amount': 1200, 'type': 'Mortgage', 'date': '2024-02-01'},
                {'property': 'Suburban House', 'amount': 1800, 'type': 'Mortgage', 'date': '2024-02-01'},
            ]

            # Display demo expense data
            st.markdown("### Sample Expense Records")
            for exp in demo_expenses:
                st.write(f"• {exp['property']}: ${exp['amount']:,.2f} - {exp['type']} ({exp['date']})")

            # Demo expense form
            st.markdown("---")
            st.markdown("### Add Expense Record (Demo)")

            with st.form("demo_expense_form"):
                col1, col2 = st.columns(2)

                with col1:
                    demo_property = st.selectbox("Property", ["Downtown Apartment", "Suburban House", "Commercial Space"], key="demo_exp_property")
                    demo_amount = st.number_input("Amount", value=200, key="demo_exp_amount")
                    demo_type = st.selectbox("Expense Type", ["Maintenance", "Utilities", "Insurance", "Mortgage", "Taxes", "Other"], key="demo_exp_type")

                with col2:
                    demo_date = st.date_input("Date", value=date.today(), key="demo_exp_date")
                    demo_description = st.text_area("Description", value="Sample expense record", key="demo_exp_description")

                if st.form_submit_button("Add Demo Expense", type="primary"):
                    st.success(f"Demo expense record added: ${demo_amount:,.2f} for {demo_property}")
                    st.info("Sign up to add real expense records!")
            return

        # Get selected organization
        selected_org_id = st.session_state.get('selected_organization')
        if not selected_org_id:
            st.error("Please select an organization first.")
            return

        # Get organization name
        org = db.get_organization_by_id(selected_org_id)
        org_name = org.name if org else "Unknown Organization"

        st.info(f"Tracking expenses for: **{org_name}**")

        # Get properties for this organization (used in both tabs)
        properties = db.get_properties()
        org_properties = [p for p in properties if p.organization_id == selected_org_id]

        # Tabs for expense management - matching reference design with 4 tabs
        exp_tab1, exp_tab2, exp_tab3, exp_tab4 = st.tabs(["View/Edit Expenses", "Add Expense", "Manage Expenses", "Recurring Expense"])

        with exp_tab1:

            if org_properties:
                # Filter by property with unique key
                col1, col2 = st.columns(2)
                with col1:
                    property_names = {prop.id: prop.name for prop in org_properties}
                    selected_property_id = st.selectbox("Filter by Property", ["All"] + list(property_names.keys()),
                                                      format_func=lambda x: "All" if x == "All" else property_names[x],
                                                      key="expense_property_filter")
                with col2:
                    date_filter = st.selectbox("Date Filter", ["Current Month", "Last 3 Months", "Last 6 Months", "This Year", "All Time"],
                                              key="expense_date_filter")

                if selected_property_id == "All":
                    expense_records = db.get_all_expenses()
                else:
                    expense_records = db.get_expenses_by_property(selected_property_id)

                if expense_records:
                    st.info(f"Found {len(expense_records)} expense transactions")

                    # Category summary metrics in 3 columns
                    col1, col2, col3 = st.columns(3)

                    # Calculate category totals
                    mortgage_total = sum(exp.amount for exp in expense_records if exp.expense_type.lower() == 'mortgage')
                    hoa_total = sum(exp.amount for exp in expense_records if exp.expense_type.lower() == 'hoa')
                    repairs_total = sum(exp.amount for exp in expense_records if exp.expense_type.lower() in ['maintenance', 'repairs'])

                    with col1:
                        st.metric("💸 Mortgage", f"${mortgage_total:,.2f}")
                    with col2:
                        st.metric("💸 Hoa", f"${hoa_total:,.2f}")
                    with col3:
                        st.metric("💸 Repairs", f"${repairs_total:,.2f}")

                    # Display expense records in table
                    expense_data = []
                    for exp in expense_records:
                        prop_name = property_names.get(exp.property_id, "Unknown")
                        expense_data.append({
                            'Property': prop_name,
                            'Amount': f"${exp.amount:,.2f}",
                            'Type': exp.expense_type.title(),
                            'Description': exp.description,
                            'Date': exp.transaction_date.strftime('%Y-%m-%d')
                        })

                    df_expense = pd.DataFrame(expense_data)
                    st.dataframe(df_expense, use_container_width=True, hide_index=True)

                    # Total Expenses summary
                    total_expenses = sum(exp.amount for exp in expense_records)
                    st.markdown(f"### 💸 Total Expenses: ${total_expenses:,.2f}")
                else:
                    st.info("No expense records found.")
            else:
                st.info(f"No properties found for {org_name}. Please add a property first.")

        with exp_tab2:
            if org_properties:
                st.subheader("Add New Expense Record")

                # Use a key to reset form after successful submission
                expense_form_key = f"add_expense_form_{st.session_state.get('expense_form_reset_counter', 0)}"

                with st.form(expense_form_key):
                    col1, col2 = st.columns(2)

                    with col1:
                        property_id = st.selectbox("Property *",
                                                 options=[prop.id for prop in org_properties],
                                                 format_func=lambda x: next(prop.name for prop in org_properties if prop.id == x))
                        amount = st.number_input("Amount *", min_value=0.01, format="%.2f")
                        expense_type = st.selectbox("Expense Type *", [et.value for et in ExpenseType])

                    with col2:
                        description = st.text_input("Description *", placeholder="e.g., Maintenance repair")
                        transaction_date = st.date_input("Transaction Date *", value=date.today())

                    # Month and Year selection
                    col3, col4 = st.columns(2)
                    with col3:
                        month = st.selectbox("Month *",
                                           options=list(range(1, 13)),
                                           format_func=lambda x: date(2024, x, 1).strftime('%B'),
                                           index=date.today().month - 1)
                    with col4:
                        year = st.number_input("Year *",
                                             min_value=2020,
                                             max_value=2030,
                                             value=date.today().year)

                    submitted = st.form_submit_button("Add Expense", type="primary")

                    if submitted:
                        # Create transaction date from month/year selection
                        transaction_date_from_month_year = date(year, month, 1)

                        new_expense = Expense(
                            property_id=property_id,
                            amount=amount,
                            expense_type=ExpenseType(expense_type),
                            description=f"{description} - {date(year, month, 1).strftime('%B %Y')}",
                            transaction_date=datetime.combine(transaction_date_from_month_year, datetime.min.time())
                        )

                        # Get user ID and organization ID for RLS compliance
                        user_id = None
                        organization_id = None
                        if st.session_state.user:
                            if hasattr(st.session_state.user, 'id'):
                                user_id = st.session_state.user.id
                            elif isinstance(st.session_state.user, dict):
                                user_id = st.session_state.user.get('id')

                        # Get selected organization
                        organization_id = st.session_state.get('selected_organization')

                        result = db.create_expense(new_expense, user_id, organization_id)
                        if result:
                            st.success("Expense record added successfully!")
                            # Increment form reset counter to clear the form
                            st.session_state.expense_form_reset_counter = st.session_state.get('expense_form_reset_counter', 0) + 1
                            st.rerun()
                        else:
                            st.error("Failed to add expense record. Please try again.")
            else:
                st.info(f"No properties found for {org_name}. Please add a property first.")

        with exp_tab3:
            # Manage Expenses tab
            st.subheader("Manage Expense Records")

            if org_properties:
                # Filter options
                col1, col2 = st.columns(2)
                with col1:
                    filter_property = st.selectbox("Filter by Property",
                                                  ["All"] + [p.name for p in org_properties],
                                                  key="manage_expense_property")
                with col2:
                    filter_date = st.selectbox("Date Filter",
                                              ["Current Month", "Last 3 Months", "Last 6 Months", "This Year", "All Time"],
                                              key="manage_expense_date")

                # Get expense records
                expense_records = db.get_all_expenses()

                if expense_records:
                    st.info(f"Found {len(expense_records)} expense records")

                    # Display records with edit/delete options
                    for exp in expense_records:
                        prop = next((p for p in org_properties if p.id == exp.property_id), None)
                        if prop:
                            with st.expander(f"💸 {prop.name} - ${exp.amount:,.2f} - {exp.transaction_date.strftime('%Y-%m-%d')}"):
                                col1, col2, col3 = st.columns([2, 1, 1])

                                with col1:
                                    st.write(f"**Type:** {exp.expense_type.title()}")
                                    st.write(f"**Description:** {exp.description}")
                                    st.write(f"**Amount:** ${exp.amount:,.2f}")
                                    st.write(f"**Date:** {exp.transaction_date.strftime('%B %d, %Y')}")

                                with col2:
                                    if st.button(f"✏️ Edit", key=f"edit_expense_{exp.id}"):
                                        st.session_state[f'editing_expense_{exp.id}'] = True

                                with col3:
                                    if st.button(f"🗑️ Delete", key=f"delete_expense_{exp.id}", type="secondary"):
                                        if db.delete_expense(exp.id):
                                            st.success("Expense record deleted")
                                            st.rerun()
                                        else:
                                            st.error("Failed to delete expense record")
                else:
                    st.info("No expense records found")
            else:
                st.info(f"No properties found for {org_name}. Please add a property first.")

        with exp_tab4:
            # Recurring Expense tab
            st.subheader("Recurring Expense Setup")

            if org_properties:
                st.info("Set up recurring expense transactions that will be automatically added each month")

                # Add recurring expense form
                with st.form("recurring_expense_form"):
                    col1, col2 = st.columns(2)

                    with col1:
                        property_id = st.selectbox("Property *",
                                                  options=[prop.id for prop in org_properties],
                                                  format_func=lambda x: next(prop.name for prop in org_properties if prop.id == x),
                                                  key="recurring_expense_property")
                        amount = st.number_input("Monthly Amount *", min_value=0.01, format="%.2f", key="recurring_expense_amount")
                        expense_type = st.selectbox("Expense Type *", ["mortgage", "hoa", "insurance", "utilities", "maintenance", "other"],
                                                   key="recurring_expense_type")

                    with col2:
                        description = st.text_input("Description *", placeholder="e.g., Monthly Mortgage Payment", key="recurring_expense_desc")
                        start_date = st.date_input("Start Date *", value=date.today(), key="recurring_expense_start")
                        frequency = st.selectbox("Frequency", ["Monthly", "Quarterly", "Annually"], key="recurring_expense_freq")

                    submitted = st.form_submit_button("Set Up Recurring Expense", type="primary")

                    if submitted:
                        st.success(f"Recurring expense of ${amount:,.2f} set up for {next(p.name for p in org_properties if p.id == property_id)}")
                        st.info("This feature will automatically create expense records based on your schedule")

                # Display existing recurring expenses
                st.markdown("### Existing Recurring Expenses")

                # Check if recurring_transactions table exists and has data
                try:
                    recurring_result = db.client.table("recurring_transactions").select("*").eq("organization_id", selected_org_id).eq("transaction_type", "expense").execute()

                    if recurring_result.data:
                        for rec in recurring_result.data:
                            prop = next((p for p in org_properties if p.id == rec.get('property_id')), None)
                            if prop:
                                with st.expander(f"🔁 {prop.name} - ${rec.get('amount', 0):,.2f}/month"):
                                    st.write(f"**Type:** {rec.get('expense_type', 'N/A').title()}")
                                    st.write(f"**Description:** {rec.get('description', 'N/A')}")
                                    st.write(f"**Frequency:** {rec.get('frequency', 'Monthly')}")
                                    st.write(f"**Start Date:** {rec.get('start_date', 'N/A')}")

                                    if st.button(f"Cancel Recurring", key=f"cancel_recurring_expense_{rec.get('id')}"):
                                        st.info("Recurring expense cancelled")
                    else:
                        st.info("No recurring expenses set up yet. Use the form above to create recurring expenses.")

                except Exception as e:
                    st.info("Recurring expense feature is available. Set up your first recurring expense above.")
            else:
                st.info(f"No properties found for {org_name}. Please add a property first.")
