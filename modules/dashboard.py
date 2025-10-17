"""
Dashboard page for PropLedger
Extracted from app_auth.py for better maintainability
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from database.database_operations import DatabaseOperations

def render_dashboard():
    """Render the Dashboard page"""
    db = DatabaseOperations()

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

            # Income breakdown by type
            income_by_type = {}
            for inc in org_income:
                income_type = inc.income_type.title()
                if income_type not in income_by_type:
                    income_by_type[income_type] = 0
                income_by_type[income_type] += inc.amount

            # Expense breakdown by type
            expense_by_type = {}
            for exp in org_expenses:
                expense_type = exp.expense_type.title()
                if expense_type not in expense_by_type:
                    expense_by_type[expense_type] = 0
                expense_by_type[expense_type] += exp.amount

            # Create 60/40 vertical split layout
            left_col, right_col = st.columns([3, 2])  # 60% left, 40% right

            with left_col:
                # 1. Financial Summary on left (2 rows of 3 metrics)
                st.markdown("### 📊 Financial Summary")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("🏠 Properties", total_properties)
                with col2:
                    st.metric("💰 Monthly Rent", f"${total_monthly_rent:,.0f}")
                with col3:
                    st.metric("📊 Total Income", f"${total_income:,.0f}")

                col4, col5, col6 = st.columns(3)
                with col4:
                    st.metric("💸 Total Expenses", f"${total_expenses:,.0f}")
                with col5:
                    st.metric("📈 Net Income", f"${net_income:,.0f}")
                with col6:
                    st.metric("📊 ROI", f"{roi:.1f}%")

                st.markdown("---")

                # 2. Income & Expense Breakdown on left
                st.markdown("### 💰 Income & Expense Breakdown")

                if income_by_type or expense_by_type:
                    # Display income types
                    if income_by_type:
                        income_cols = st.columns(len(income_by_type))
                        for i, (income_type, amount) in enumerate(income_by_type.items()):
                            with income_cols[i]:
                                st.metric(f"💰 {income_type}", f"${amount:,.0f}")

                    # Display expense types
                    if expense_by_type:
                        expense_cols = st.columns(len(expense_by_type))
                        for i, (expense_type, amount) in enumerate(expense_by_type.items()):
                            with expense_cols[i]:
                                st.metric(f"💸 {expense_type}", f"${amount:,.0f}")
                else:
                    st.info("No income or expense records found")

                st.markdown("---")

                # 3. Recent Activity (Last 10 Transactions) on left
                st.markdown("### 📋 Recent Activity (Last 10 Transactions)")

                # Combine and sort all transactions by date
                all_transactions = []
                for inc in org_income:
                    prop_name = next((p.name for p in org_properties if p.id == inc.property_id), "Unknown")
                    all_transactions.append({
                        'date': inc.transaction_date,
                        'property': prop_name,
                        'category': 'Income',
                        'type': inc.income_type.title(),
                        'amount': inc.amount,
                        'description': inc.description or ''
                    })

                for exp in org_expenses:
                    prop_name = next((p.name for p in org_properties if p.id == exp.property_id), "Unknown")
                    all_transactions.append({
                        'date': exp.transaction_date,
                        'property': prop_name,
                        'category': 'Expense',
                        'type': exp.expense_type.title(),
                        'amount': exp.amount,
                        'description': exp.description or ''
                    })

                # Sort by date (most recent first) and take last 10
                recent_transactions = sorted(all_transactions, key=lambda x: x['date'], reverse=True)[:10]

                if recent_transactions:
                    # Create DataFrame for display
                    df_transactions = pd.DataFrame(recent_transactions)
                    df_transactions['date'] = pd.to_datetime(df_transactions['date']).dt.strftime('%Y-%m-%d')
                    df_transactions['amount'] = df_transactions['amount'].apply(lambda x: f"${x:,.2f}")

                    # Display as table
                    st.dataframe(
                        df_transactions[['property', 'category', 'type', 'amount', 'description', 'date']],
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("No transactions found")

            with right_col:
                # 1. Financial Overview Chart on right
                st.markdown("### 📊 Financial Summary")

                # Bar chart for Income vs Expenses vs Net Income
                fig_overview = go.Figure()
                fig_overview.add_trace(go.Bar(
                    name='Income',
                    x=['Income'],
                    y=[total_income],
                    marker_color='green'
                ))
                fig_overview.add_trace(go.Bar(
                    name='Expenses',
                    x=['Expenses'],
                    y=[total_expenses],
                    marker_color='red'
                ))
                fig_overview.add_trace(go.Bar(
                    name='Net Income',
                    x=['Net Income'],
                    y=[net_income],
                    marker_color='blue'
                ))
                fig_overview.update_layout(
                    title="Financial Overview",
                    showlegend=True,
                    height=300,
                    margin=dict(l=0, r=0, t=40, b=0)
                )
                st.plotly_chart(fig_overview, use_container_width=True)

                st.markdown("---")

                # 2. Income Breakdown Pie Chart on right
                if income_by_type:
                    st.markdown("### 💰 Income Breakdown")
                    fig_income = px.pie(
                        values=list(income_by_type.values()),
                        names=list(income_by_type.keys()),
                        title="Income by Type"
                    )
                    fig_income.update_layout(
                        height=300,
                        margin=dict(l=0, r=0, t=40, b=0)
                    )
                    st.plotly_chart(fig_income, use_container_width=True)
                else:
                    st.info("No income data available")

                st.markdown("---")

                # 3. Expense Breakdown Pie Chart on right
                if expense_by_type:
                    st.markdown("### 💸 Expense Breakdown")
                    fig_expense = px.pie(
                        values=list(expense_by_type.values()),
                        names=list(expense_by_type.keys()),
                        title="Expenses by Type"
                    )
                    fig_expense.update_layout(
                        height=300,
                        margin=dict(l=0, r=0, t=40, b=0)
                    )
                    st.plotly_chart(fig_expense, use_container_width=True)
                else:
                    st.info("No expense data available")
