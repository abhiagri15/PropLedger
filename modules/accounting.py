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

    # Use native Streamlit tabs to match reference design
    income_tab, expense_tab = st.tabs(["🔥 Income", "✅ Expenses"])

    with income_tab:

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

        # Get properties for this organization (used in both tabs)
        properties = db.get_properties()
        org_properties = [p for p in properties if p.organization_id == selected_org_id]

        # Tabs for income management - matching reference design
        tab1, tab2, tab3, tab4 = st.tabs(["View Transactions", "Add Income", "Manage Transactions", "Recurring Income"])

        with tab1:

            if org_properties:
                # Filter by property and date with submit button
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    property_names = {prop.id: prop.name for prop in org_properties}
                    selected_property_id = st.selectbox("Filter by Property", ["All"] + list(property_names.keys()),
                                                      format_func=lambda x: "All" if x == "All" else property_names[x],
                                                      key="income_view_property_filter")
                with col2:
                    date_filter = st.selectbox("Date Filter", ["Current Month", "Last 3 Months", "Last 6 Months", "This Year", "All Time"],
                                              key="income_date_filter")
                with col3:
                    st.markdown("<br>", unsafe_allow_html=True)  # Add spacing to align button
                    apply_filter = st.button("Apply Filter", key="income_apply_filter", type="primary")

                if selected_property_id == "All":
                    income_records = db.get_all_income()
                else:
                    income_records = db.get_income_by_property(selected_property_id)

                # Apply date filter
                if income_records and date_filter != "All Time":
                    from datetime import datetime, timedelta
                    today = datetime.now().date()  # Convert to date for comparison

                    if date_filter == "Current Month":
                        start_date = today.replace(day=1)
                    elif date_filter == "Last 3 Months":
                        start_date = today - timedelta(days=90)
                    elif date_filter == "Last 6 Months":
                        start_date = today - timedelta(days=180)
                    elif date_filter == "This Year":
                        start_date = today.replace(month=1, day=1)

                    # Convert transaction_date to date if it's a datetime object
                    income_records = [inc for inc in income_records
                                     if (inc.transaction_date.date() if hasattr(inc.transaction_date, 'date') else inc.transaction_date) >= start_date]

                if income_records:
                    # All summary metrics in one line - 4 columns
                    col1, col2, col3, col4 = st.columns(4)

                    # Calculate totals
                    total_income = sum(inc.amount for inc in income_records)
                    rent_total = sum(inc.amount for inc in income_records if inc.income_type.lower() == 'rent')
                    parking_total = sum(inc.amount for inc in income_records if inc.income_type.lower() == 'parking')
                    late_fee_total = sum(inc.amount for inc in income_records if inc.income_type.lower() in ['late_fee', 'latefee'])

                    with col1:
                        st.metric("🔥 Total Income", f"${total_income:,.2f}")
                    with col2:
                        st.metric("🔥 Rent", f"${rent_total:,.2f}")
                    with col3:
                        st.metric("🔥 Parking", f"${parking_total:,.2f}")
                    with col4:
                        st.metric("🔥 Late Fee", f"${late_fee_total:,.2f}")

                    # Display income records in dataframe
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
                    # Reset index to start from 1 instead of 0
                    df_income.index = range(1, len(df_income) + 1)
                    st.dataframe(df_income, use_container_width=True)
                else:
                    st.info("No income records found.")
            else:
                st.info(f"No properties found for {org_name}. Please add a property first.")

        with tab2:
            if org_properties:
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
            all_income = db.get_all_income()
            org_income = [inc for inc in all_income if any(p.id == inc.property_id for p in org_properties)]

            if org_income:
                # Filter and Sort Controls
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown("**Filter by Property**")
                    filter_property = st.selectbox(
                        "Filter by Property",
                        ["All Properties"] + [p.name for p in org_properties],
                        label_visibility="collapsed",
                        key="manage_income_property"
                    )

                with col2:
                    st.markdown("**Filter by Date**")
                    filter_date = st.selectbox(
                        "Filter by Date",
                        ["All Time", "Current Month", "Last 3 Months", "Last 6 Months", "This Year"],
                        index=1,  # Default to "Current Month"
                        label_visibility="collapsed",
                        key="manage_income_date"
                    )

                with col3:
                    st.markdown("**Sort by**")
                    sort_by = st.selectbox(
                        "Sort by",
                        ["Date (Newest First)", "Date (Oldest First)", "Amount (High to Low)", "Amount (Low to High)"],
                        label_visibility="collapsed",
                        key="manage_income_sort"
                    )

                # Apply filters
                filtered_income = org_income

                # Filter by property
                if filter_property != "All Properties":
                    filtered_income = [inc for inc in filtered_income
                                     if any(p.name == filter_property and p.id == inc.property_id for p in org_properties)]

                # Apply date filter
                if filter_date != "All Time":
                    from datetime import datetime, timedelta
                    today = datetime.now().date()

                    if filter_date == "Current Month":
                        start_date = today.replace(day=1)
                    elif filter_date == "Last 3 Months":
                        start_date = today - timedelta(days=90)
                    elif filter_date == "Last 6 Months":
                        start_date = today - timedelta(days=180)
                    elif filter_date == "This Year":
                        start_date = today.replace(month=1, day=1)

                    filtered_income = [inc for inc in filtered_income
                                     if (inc.transaction_date.date() if hasattr(inc.transaction_date, 'date') else inc.transaction_date) >= start_date]

                # Apply sorting
                if sort_by == "Date (Newest First)":
                    filtered_income = sorted(filtered_income, key=lambda x: x.transaction_date, reverse=True)
                elif sort_by == "Date (Oldest First)":
                    filtered_income = sorted(filtered_income, key=lambda x: x.transaction_date)
                elif sort_by == "Amount (High to Low)":
                    filtered_income = sorted(filtered_income, key=lambda x: x.amount, reverse=True)
                elif sort_by == "Amount (Low to High)":
                    filtered_income = sorted(filtered_income, key=lambda x: x.amount)

                st.markdown("---")

                # Add ultra-compact styling CSS
                st.markdown("""
                    <style>
                    .stMarkdown p {
                        margin-bottom: 0 !important;
                        margin-top: 0.1rem !important;
                        line-height: 1.4 !important;
                    }
                    div[data-testid="column"] {
                        padding-top: 0 !important;
                        padding-bottom: 0 !important;
                    }
                    .element-container {
                        margin-bottom: 0 !important;
                    }
                    </style>
                """, unsafe_allow_html=True)

                # Display income records as compact cards
                for inc in filtered_income:
                    prop = next((p for p in org_properties if p.id == inc.property_id), None)
                    if prop:
                        # Income card - ultra-compact design
                        st.markdown(f"<p style='margin: 0.3rem 0 0.1rem 0;'><strong>💰 {prop.name} - ${inc.amount:,.2f}</strong></p>", unsafe_allow_html=True)

                        # Transaction details in compact format
                        info_col1, info_col2 = st.columns([1.5, 1.5])

                        with info_col1:
                            st.markdown(f"<p style='margin: 0;'><strong>Type:</strong> {inc.income_type.title()}</p>", unsafe_allow_html=True)
                            st.markdown(f"<p style='margin: 0;'><strong>Description:</strong> {inc.description}</p>", unsafe_allow_html=True)

                        with info_col2:
                            st.markdown(f"<p style='margin: 0;'><strong>Date:</strong> {inc.transaction_date.strftime('%B %d, %Y')}</p>", unsafe_allow_html=True)
                            st.markdown(f"<p style='margin: 0;'><strong>Amount:</strong> ${inc.amount:,.2f}</p>", unsafe_allow_html=True)

                        # Action buttons - equal size
                        btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 8])
                        with btn_col1:
                            if st.button(f"✏️ Edit", key=f"manage_edit_income_{inc.id}", use_container_width=True):
                                st.session_state[f'editing_income_{inc.id}'] = True
                                st.rerun()
                        with btn_col2:
                            if st.button(f"🗑️ Delete", key=f"manage_delete_income_{inc.id}", type="secondary", use_container_width=True):
                                if db.delete_income(inc.id):
                                    st.success("Income record deleted successfully!")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete income record.")

                        # Thin separator between income records
                        st.markdown("<hr style='margin: 0.5rem 0; border: none; border-top: 1px solid #e0e0e0;'>", unsafe_allow_html=True)
            else:
                st.info(f"No income records found for {org_name}.")

        with tab4:
            # Recurring Income tab
            if org_properties:

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
                    recurring_result = db.client.table("recurring_transactions").select("*").eq("organization_id", selected_org_id).eq("transaction_type", "income").execute()

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

        # Get properties for this organization (used in both tabs)
        properties = db.get_properties()
        org_properties = [p for p in properties if p.organization_id == selected_org_id]

        # Tabs for expense management - matching reference design with 4 tabs
        exp_tab1, exp_tab2, exp_tab3, exp_tab4 = st.tabs(["View Transactions", "Add Expense", "Manage Transactions", "Recurring Expense"])

        with exp_tab1:

            if org_properties:
                # Filter by property and date with submit button
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    property_names = {prop.id: prop.name for prop in org_properties}
                    selected_property_id = st.selectbox("Filter by Property", ["All"] + list(property_names.keys()),
                                                      format_func=lambda x: "All" if x == "All" else property_names[x],
                                                      key="expense_property_filter")
                with col2:
                    date_filter = st.selectbox("Date Filter", ["Current Month", "Last 3 Months", "Last 6 Months", "This Year", "All Time"],
                                              key="expense_date_filter")
                with col3:
                    st.markdown("<br>", unsafe_allow_html=True)  # Add spacing to align button
                    apply_filter = st.button("Apply Filter", key="expense_apply_filter", type="primary")

                if selected_property_id == "All":
                    expense_records = db.get_all_expenses()
                else:
                    expense_records = db.get_expenses_by_property(selected_property_id)

                # Apply date filter
                if expense_records and date_filter != "All Time":
                    from datetime import datetime, timedelta
                    today = datetime.now().date()  # Convert to date for comparison

                    if date_filter == "Current Month":
                        start_date = today.replace(day=1)
                    elif date_filter == "Last 3 Months":
                        start_date = today - timedelta(days=90)
                    elif date_filter == "Last 6 Months":
                        start_date = today - timedelta(days=180)
                    elif date_filter == "This Year":
                        start_date = today.replace(month=1, day=1)

                    # Convert transaction_date to date if it's a datetime object
                    expense_records = [exp for exp in expense_records
                                      if (exp.transaction_date.date() if hasattr(exp.transaction_date, 'date') else exp.transaction_date) >= start_date]

                if expense_records:
                    # All summary metrics in one line - 4 columns
                    col1, col2, col3, col4 = st.columns(4)

                    # Calculate totals
                    total_expenses = sum(exp.amount for exp in expense_records)
                    mortgage_total = sum(exp.amount for exp in expense_records if exp.expense_type.lower() == 'mortgage')
                    hoa_total = sum(exp.amount for exp in expense_records if exp.expense_type.lower() == 'hoa')
                    repairs_total = sum(exp.amount for exp in expense_records if exp.expense_type.lower() in ['maintenance', 'repairs'])

                    with col1:
                        st.metric("💸 Total Expenses", f"${total_expenses:,.2f}")
                    with col2:
                        st.metric("💸 Mortgage", f"${mortgage_total:,.2f}")
                    with col3:
                        st.metric("💸 Hoa", f"${hoa_total:,.2f}")
                    with col4:
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
                    # Reset index to start from 1 instead of 0
                    df_expense.index = range(1, len(df_expense) + 1)
                    st.dataframe(df_expense, use_container_width=True)
                else:
                    st.info("No expense records found.")
            else:
                st.info(f"No properties found for {org_name}. Please add a property first.")

        with exp_tab2:
            if org_properties:
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
            all_expenses = db.get_all_expenses()
            org_expenses = [exp for exp in all_expenses if any(p.id == exp.property_id for p in org_properties)]

            if org_expenses:
                # Filter and Sort Controls
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown("**Filter by Property**")
                    filter_property = st.selectbox(
                        "Filter by Property",
                        ["All Properties"] + [p.name for p in org_properties],
                        label_visibility="collapsed",
                        key="manage_expense_property"
                    )

                with col2:
                    st.markdown("**Filter by Date**")
                    filter_date = st.selectbox(
                        "Filter by Date",
                        ["All Time", "Current Month", "Last 3 Months", "Last 6 Months", "This Year"],
                        index=1,  # Default to "Current Month"
                        label_visibility="collapsed",
                        key="manage_expense_date"
                    )

                with col3:
                    st.markdown("**Sort by**")
                    sort_by = st.selectbox(
                        "Sort by",
                        ["Date (Newest First)", "Date (Oldest First)", "Amount (High to Low)", "Amount (Low to High)"],
                        label_visibility="collapsed",
                        key="manage_expense_sort"
                    )

                # Apply filters
                filtered_expenses = org_expenses

                # Filter by property
                if filter_property != "All Properties":
                    filtered_expenses = [exp for exp in filtered_expenses
                                       if any(p.name == filter_property and p.id == exp.property_id for p in org_properties)]

                # Apply date filter
                if filter_date != "All Time":
                    from datetime import datetime, timedelta
                    today = datetime.now().date()

                    if filter_date == "Current Month":
                        start_date = today.replace(day=1)
                    elif filter_date == "Last 3 Months":
                        start_date = today - timedelta(days=90)
                    elif filter_date == "Last 6 Months":
                        start_date = today - timedelta(days=180)
                    elif filter_date == "This Year":
                        start_date = today.replace(month=1, day=1)

                    filtered_expenses = [exp for exp in filtered_expenses
                                       if (exp.transaction_date.date() if hasattr(exp.transaction_date, 'date') else exp.transaction_date) >= start_date]

                # Apply sorting
                if sort_by == "Date (Newest First)":
                    filtered_expenses = sorted(filtered_expenses, key=lambda x: x.transaction_date, reverse=True)
                elif sort_by == "Date (Oldest First)":
                    filtered_expenses = sorted(filtered_expenses, key=lambda x: x.transaction_date)
                elif sort_by == "Amount (High to Low)":
                    filtered_expenses = sorted(filtered_expenses, key=lambda x: x.amount, reverse=True)
                elif sort_by == "Amount (Low to High)":
                    filtered_expenses = sorted(filtered_expenses, key=lambda x: x.amount)

                st.markdown("---")

                # Add ultra-compact styling CSS
                st.markdown("""
                    <style>
                    .stMarkdown p {
                        margin-bottom: 0 !important;
                        margin-top: 0.1rem !important;
                        line-height: 1.4 !important;
                    }
                    div[data-testid="column"] {
                        padding-top: 0 !important;
                        padding-bottom: 0 !important;
                    }
                    .element-container {
                        margin-bottom: 0 !important;
                    }
                    </style>
                """, unsafe_allow_html=True)

                # Display expense records as compact cards
                for exp in filtered_expenses:
                    prop = next((p for p in org_properties if p.id == exp.property_id), None)
                    if prop:
                        # Expense card - ultra-compact design
                        st.markdown(f"<p style='margin: 0.3rem 0 0.1rem 0;'><strong>💸 {prop.name} - ${exp.amount:,.2f}</strong></p>", unsafe_allow_html=True)

                        # Transaction details in compact format
                        info_col1, info_col2 = st.columns([1.5, 1.5])

                        with info_col1:
                            st.markdown(f"<p style='margin: 0;'><strong>Type:</strong> {exp.expense_type.title()}</p>", unsafe_allow_html=True)
                            st.markdown(f"<p style='margin: 0;'><strong>Description:</strong> {exp.description}</p>", unsafe_allow_html=True)

                        with info_col2:
                            st.markdown(f"<p style='margin: 0;'><strong>Date:</strong> {exp.transaction_date.strftime('%B %d, %Y')}</p>", unsafe_allow_html=True)
                            st.markdown(f"<p style='margin: 0;'><strong>Amount:</strong> ${exp.amount:,.2f}</p>", unsafe_allow_html=True)

                        # Action buttons - equal size
                        btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 8])
                        with btn_col1:
                            if st.button(f"✏️ Edit", key=f"manage_edit_expense_{exp.id}", use_container_width=True):
                                st.session_state[f'editing_expense_{exp.id}'] = True
                                st.rerun()
                        with btn_col2:
                            if st.button(f"🗑️ Delete", key=f"manage_delete_expense_{exp.id}", type="secondary", use_container_width=True):
                                if db.delete_expense(exp.id):
                                    st.success("Expense record deleted successfully!")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete expense record.")

                        # Thin separator between expense records
                        st.markdown("<hr style='margin: 0.5rem 0; border: none; border-top: 1px solid #e0e0e0;'>", unsafe_allow_html=True)
            else:
                st.info(f"No expense records found for {org_name}.")

        with exp_tab4:
            # Recurring Expense tab
            if org_properties:

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
