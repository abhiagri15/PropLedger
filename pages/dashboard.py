"""
Dashboard page for PropLedger
Extracted from app_auth.py for better maintainability
"""

import streamlit as st
import pandas as pd
from database.database_operations import DatabaseOperations

def render_dashboard():
    """Render the Dashboard page"""
    db = DatabaseOperations()

    st.markdown('<h1 class="main-header">🏠 PropLedger Dashboard</h1>', unsafe_allow_html=True)

    # Get data based on authentication mode
    is_demo_mode = False
    if st.session_state.user:
        if hasattr(st.session_state.user, 'email'):
            is_demo_mode = getattr(st.session_state.user, 'email', '') == 'demo@example.com'
        else:
            is_demo_mode = st.session_state.user.get('email', '') == 'demo@example.com'

    if is_demo_mode:
        # Demo mode - use sample data
        st.markdown('<div class="info-box">🎯 <strong>Demo Mode</strong> - Showing sample data. Sign up to use your own data!</div>', unsafe_allow_html=True)

        demo_properties = [
            {
                'id': 1,
                'name': 'Downtown Apartment',
                'address': '123 Main St, Downtown, City',
                'property_type': 'apartment',
                'monthly_rent': 2000.00,
                'purchase_price': 250000.00,
                'roi': 8.5
            },
            {
                'id': 2,
                'name': 'Suburban House',
                'address': '456 Oak Ave, Suburb, City',
                'property_type': 'house',
                'monthly_rent': 2500.00,
                'purchase_price': 350000.00,
                'roi': 7.2
            }
        ]

        demo_income = [
            {'property': 'Downtown Apartment', 'amount': 2000, 'type': 'rent', 'date': '2023-12-01'},
            {'property': 'Suburban House', 'amount': 2500, 'type': 'rent', 'date': '2023-12-01'},
            {'property': 'Downtown Apartment', 'amount': 2000, 'type': 'rent', 'date': '2023-11-01'},
        ]

        demo_expenses = [
            {'property': 'Downtown Apartment', 'amount': 150, 'type': 'maintenance', 'date': '2023-12-15'},
            {'property': 'Suburban House', 'amount': 300, 'type': 'repairs', 'date': '2023-12-05'},
            {'property': 'Downtown Apartment', 'amount': 200, 'type': 'utilities', 'date': '2023-12-10'},
        ]

        # Portfolio overview metrics
        col1, col2, col3, col4 = st.columns(4)

        total_properties = len(demo_properties)
        total_monthly_rent = sum(prop['monthly_rent'] for prop in demo_properties)
        total_purchase_price = sum(prop['purchase_price'] for prop in demo_properties)
        total_income = sum(inc['amount'] for inc in demo_income)
        total_expenses = sum(exp['amount'] for exp in demo_expenses)
        net_income = total_income - total_expenses

        with col1:
            st.metric("Total Properties", total_properties)
        with col2:
            st.metric("Monthly Rent Income", f"${total_monthly_rent:,.2f}")
        with col3:
            st.metric("Total Investment", f"${total_purchase_price:,.2f}")
        with col4:
            st.metric("Net Income", f"${net_income:,.2f}")

        st.markdown("---")

        # Properties overview table
        st.subheader("Properties Overview")
        df_properties = pd.DataFrame(demo_properties)
        st.dataframe(df_properties, use_container_width=True)

        # Recent transactions
        st.subheader("Recent Transactions")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Recent Income**")
            for inc in demo_income:
                st.write(f"• {inc['property']}: ${inc['amount']:,.2f} - {inc['type']} ({inc['date']})")

        with col2:
            st.markdown("**Recent Expenses**")
            for exp in demo_expenses:
                st.write(f"• {exp['property']}: ${exp['amount']:,.2f} - {exp['type']} ({exp['date']})")

    else:
        # Get selected organization
        selected_org_id = st.session_state.get('selected_organization')
        if not selected_org_id:
            st.error("Please select an organization first.")
            return

        # Get organization name
        org = db.get_organization_by_id(selected_org_id)
        org_name = org.name if org else "Unknown Organization"

        st.info(f"Dashboard for: **{org_name}**")

        # Real mode - use database with organization filtering
        properties = db.get_properties()
        # Filter properties by organization
        org_properties = [p for p in properties if p.organization_id == selected_org_id]

        if not org_properties:
            st.info(f"No properties found for {org_name}. Add your first property to get started!")
            st.markdown("### Quick Start")
            st.markdown("1. Go to **Properties** tab to add your first rental property")
            st.markdown("2. Add income and expense records in their respective tabs")
            st.markdown("3. View analytics and AI insights to optimize your portfolio")
        else:
            # Get organization-specific financial data
            all_income = db.get_all_income()
            all_expenses = db.get_all_expenses()

            # Filter by organization
            org_income = [inc for inc in all_income if inc.organization_id == selected_org_id]
            org_expenses = [exp for exp in all_expenses if exp.organization_id == selected_org_id]

            # Calculate organization-specific financials
            total_properties = len(org_properties)
            total_monthly_rent = sum(prop.monthly_rent for prop in org_properties)
            total_purchase_price = sum(prop.purchase_price for prop in org_properties)
            total_income = sum(inc.amount for inc in org_income)
            total_expenses = sum(exp.amount for exp in org_expenses)
            net_income = total_income - total_expenses
            profit_margin = (net_income / total_income * 100) if total_income > 0 else 0
            roi = (net_income / total_purchase_price * 100) if total_purchase_price > 0 else 0

            # Ultra-compact metrics layout - 1 row with 6 key metrics
            st.markdown("### 📊 Financial Overview")

            # Single row with 6 most important metrics
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            with col1:
                st.metric("🏠 Properties", total_properties)
            with col2:
                st.metric("💰 Monthly Rent", f"${total_monthly_rent:,.0f}")
            with col3:
                st.metric("📊 Total Income", f"${total_income:,.0f}")
            with col4:
                st.metric("💸 Total Expenses", f"${total_expenses:,.0f}")
            with col5:
                st.metric("📈 Net Income", f"${net_income:,.0f}")
            with col6:
                st.metric("📊 ROI", f"{roi:.1f}%")

            st.markdown("---")

            # Ultra-compact P&L Breakdown - Single row
            st.markdown("### 💰 Income & Expense Breakdown")

            # Income breakdown
            income_by_type = {}
            for inc in org_income:
                income_type = inc.income_type.title()
                if income_type not in income_by_type:
                    income_by_type[income_type] = 0
                income_by_type[income_type] += inc.amount

            # Expense breakdown
            expense_by_type = {}
            for exp in org_expenses:
                expense_type = exp.expense_type.title()
                if expense_type not in expense_by_type:
                    expense_by_type[expense_type] = 0
                expense_by_type[expense_type] += exp.amount

            # Create single row layout for income and expenses
            if income_by_type or expense_by_type:
                # Combine all types into one row
                all_types = list(income_by_type.items()) + list(expense_by_type.items())
                if all_types:
                    type_cols = st.columns(min(len(all_types), 8))  # Max 8 columns
                    for i, (type_name, amount) in enumerate(all_types[:8]):  # Limit to 8 items
                        with type_cols[i]:
                            icon = "💰" if type_name in [inc[0] for inc in income_by_type.items()] else "💸"
                            st.metric(f"{icon} {type_name}", f"${amount:,.0f}")
            else:
                st.info("No income or expense records found")

            st.markdown("---")

            # Compact Properties Overview
            st.markdown("### 🏠 Properties Performance")

            # Create property cards in horizontal layout
            if org_properties:
                prop_cols = st.columns(min(len(org_properties), 3))  # Max 3 properties per row

                for i, prop in enumerate(org_properties):
                    with prop_cols[i % 3]:
                        # Get property-specific income and expenses
                        prop_income = [inc for inc in org_income if inc.property_id == prop.id]
                        prop_expenses = [exp for exp in org_expenses if exp.property_id == prop.id]

                        prop_total_income = sum(inc.amount for inc in prop_income)
                        prop_total_expenses = sum(exp.amount for exp in prop_expenses)
                        prop_net_income = prop_total_income - prop_total_expenses
                        prop_roi = (prop_net_income / prop.purchase_price * 100) if prop.purchase_price > 0 else 0

                        with st.container():
                            st.markdown(f"**{prop.name}**")
                            st.markdown(f"*{prop.address}*")
                            st.metric("Monthly Rent", f"${prop.monthly_rent:,.0f}")
                            st.metric("Net Income", f"${prop_net_income:,.0f}")
                            st.metric("ROI", f"{prop_roi:.1f}%")
                            st.markdown("---")
            else:
                st.info("No properties found for this organization")

            # Compact Recent Transactions
            st.markdown("### 📋 Recent Activity")

            # Combine recent income and expenses
            recent_income = sorted(org_income, key=lambda x: x.transaction_date, reverse=True)[:3]
            recent_expenses = sorted(org_expenses, key=lambda x: x.transaction_date, reverse=True)[:3]

            if recent_income or recent_expenses:
                # Create horizontal layout for recent transactions
                trans_cols = st.columns(2)

                with trans_cols[0]:
                    st.markdown("**💰 Recent Income**")
                    if recent_income:
                        for inc in recent_income:
                            prop_name = next((p.name for p in org_properties if p.id == inc.property_id), "Unknown")
                            st.write(f"• {prop_name}: ${inc.amount:,.0f}")
                    else:
                        st.write("No recent income")

                with trans_cols[1]:
                    st.markdown("**💸 Recent Expenses**")
                    if recent_expenses:
                        for exp in recent_expenses:
                            prop_name = next((p.name for p in org_properties if p.id == exp.property_id), "Unknown")
                            st.write(f"• {prop_name}: ${exp.amount:,.0f}")
                    else:
                        st.write("No recent expenses")
            else:
                st.info("No recent transactions found")
