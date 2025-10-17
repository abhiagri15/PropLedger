"""
Dashboard page for PropLedger
Extracted from app_auth.py for better maintainability
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from database.database_operations import DatabaseOperations

def render_dashboard():
    """Render the Dashboard page"""
    db = DatabaseOperations()

    # Custom CSS to reduce metric font sizes and spacing
    st.markdown("""
    <style>
    /* Reduce metric value font size */
    [data-testid="stMetricValue"] {
        font-size: 1.2rem !important;
    }
    /* Reduce metric label font size */
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
    }
    /* Reduce metric delta font size */
    [data-testid="stMetricDelta"] {
        font-size: 0.75rem !important;
    }
    /* Reduce vertical spacing between sections */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 1rem !important;
    }
    /* Reduce spacing in columns */
    [data-testid="column"] {
        gap: 0.5rem !important;
    }
    /* Reduce horizontal rule spacing */
    hr {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Date Filter dropdown (30% width)
    date_col, spacer_col = st.columns([3, 7])

    with date_col:
        st.markdown('<p style="font-size: 0.9rem; font-weight: 600; color: #1f77b4;">Date Filter</p>', unsafe_allow_html=True)
        date_filter = st.selectbox(
            "Select Date Range",
            options=["Current Year", "Last 30 Days", "Last 90 Days", "Last 12 Months", "All Time"],
            index=0,
            key="dashboard_date_filter",
            label_visibility="collapsed"
        )

    # Calculate date range based on filter
    today = date.today()
    if date_filter == "Current Year":
        start_date = date(today.year, 1, 1)
        end_date = today
    elif date_filter == "Last 30 Days":
        start_date = today - timedelta(days=30)
        end_date = today
    elif date_filter == "Last 90 Days":
        start_date = today - timedelta(days=90)
        end_date = today
    elif date_filter == "Last 12 Months":
        start_date = today - timedelta(days=365)
        end_date = today
    else:  # All Time
        start_date = date(2020, 1, 1)
        end_date = today

    st.markdown("---")

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

            # Main 60/40 split for entire dashboard content
            left_column, right_column = st.columns([3, 2])

            with left_column:
                # Financial Summary section
                st.markdown('<p style="font-size: 1rem; font-weight: 600;">📊 Financial Summary</p>', unsafe_allow_html=True)

                # Two rows of 3 metrics each
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

                st.markdown('<div style="margin: 1rem 0;"></div>', unsafe_allow_html=True)

                # Income & Expense Breakdown section
                st.markdown('<p style="font-size: 1rem; font-weight: 600;">💰 Income & Expense Breakdown</p>', unsafe_allow_html=True)

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
                        type_cols = st.columns(min(len(all_types), 4))  # Max 4 columns
                        for i, (type_name, amount) in enumerate(all_types[:4]):  # Limit to 4 items
                            with type_cols[i]:
                                icon = "💰" if type_name in [inc[0] for inc in income_by_type.items()] else "💸"
                                st.metric(f"{icon} {type_name}", f"${amount:,.0f}")
                else:
                    st.info("No income or expense records found")

                st.markdown('<div style="margin: 1rem 0;"></div>', unsafe_allow_html=True)

                # Recent Activity table (Last 10 Transactions)
                st.markdown('<p style="font-size: 1rem; font-weight: 600;">📋 Recent Activity (Last 10 Transactions)</p>', unsafe_allow_html=True)

                # Combine recent income and expenses into a single list
                recent_transactions = []

                for inc in org_income:
                    prop_name = next((p.name for p in org_properties if p.id == inc.property_id), "Unknown")
                    recent_transactions.append({
                        'Property': prop_name,
                        'Category': 'Income',
                        'Type': inc.income_type.title(),
                        'Amount': f"${inc.amount:,.2f}",
                        'Description': inc.description or 'Monthly Rent',
                        'Date': inc.transaction_date.strftime('%Y-%m-%d')
                    })

                for exp in org_expenses:
                    prop_name = next((p.name for p in org_properties if p.id == exp.property_id), "Unknown")
                    recent_transactions.append({
                        'Property': prop_name,
                        'Category': 'Expense',
                        'Type': exp.expense_type.title(),
                        'Amount': f"${exp.amount:,.2f}",
                        'Description': exp.description or exp.expense_type.title(),
                        'Date': exp.transaction_date.strftime('%Y-%m-%d')
                    })

                # Sort by date and take last 10
                recent_transactions.sort(key=lambda x: x['Date'], reverse=True)
                recent_transactions = recent_transactions[:10]

                if recent_transactions:
                    # Create DataFrame for table display
                    df_transactions = pd.DataFrame(recent_transactions)
                    st.dataframe(df_transactions, use_container_width=True, hide_index=True)
                else:
                    st.info("No recent transactions found")

            with right_column:
                # Charts section
                st.markdown('<p style="font-size: 1rem; font-weight: 600;">📈 Financial Summary</p>', unsafe_allow_html=True)

                # Financial Overview section with bar chart
                st.markdown('<p style="font-size: 0.9rem; font-weight: 600;">Financial Overview</p>', unsafe_allow_html=True)

                # Bar chart showing income vs expenses vs net income
                fig = go.Figure(data=[
                    go.Bar(name='Income', x=['Category'], y=[total_income], marker_color='#16a34a', text=[f'${total_income:,.0f}'], textposition='inside'),
                    go.Bar(name='Expenses', x=['Category'], y=[total_expenses], marker_color='#dc2626', text=[f'${total_expenses:,.0f}'], textposition='inside'),
                    go.Bar(name='Net Income', x=['Category'], y=[net_income], marker_color='#2563eb', text=[f'${net_income:,.0f}'], textposition='inside')
                ])
                fig.update_layout(
                    xaxis_title="Category",
                    yaxis_title="Amount ($)",
                    barmode='group',
                    height=280,
                    showlegend=True,
                    margin=dict(l=40, r=20, t=20, b=40),
                    font=dict(size=10),
                    legend=dict(font=dict(size=10))
                )
                st.plotly_chart(fig, use_container_width=True)

                # Income Breakdown section with donut chart
                st.markdown('<p style="font-size: 0.9rem; font-weight: 600;">💰 Income Breakdown</p>', unsafe_allow_html=True)

                # Calculate income breakdown
                income_by_type_chart = {}
                for inc in org_income:
                    income_type = inc.income_type.title()
                    if income_type not in income_by_type_chart:
                        income_by_type_chart[income_type] = 0
                    income_by_type_chart[income_type] += inc.amount

                if income_by_type_chart:
                    labels = list(income_by_type_chart.keys())
                    values = list(income_by_type_chart.values())

                    fig = go.Figure(data=[go.Pie(
                        labels=labels,
                        values=values,
                        hole=0.4,
                        marker=dict(colors=['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'])
                    )])
                    fig.update_layout(
                        height=280,
                        margin=dict(l=20, r=20, t=20, b=20),
                        showlegend=True,
                        font=dict(size=10),
                        legend=dict(font=dict(size=10))
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No income data available")

                # Expense Breakdown section with donut chart
                st.markdown('<p style="font-size: 0.9rem; font-weight: 600;">💸 Expense Breakdown</p>', unsafe_allow_html=True)

                # Calculate expense breakdown
                expense_by_type_chart = {}
                for exp in org_expenses:
                    expense_type = exp.expense_type.title()
                    if expense_type not in expense_by_type_chart:
                        expense_by_type_chart[expense_type] = 0
                    expense_by_type_chart[expense_type] += exp.amount

                if expense_by_type_chart:
                    labels = list(expense_by_type_chart.keys())
                    values = list(expense_by_type_chart.values())

                    fig = go.Figure(data=[go.Pie(
                        labels=labels,
                        values=values,
                        hole=0.4,
                        marker=dict(colors=['#ef4444', '#f59e0b', '#8b5cf6', '#ec4899', '#14b8a6'])
                    )])
                    fig.update_layout(
                        height=280,
                        margin=dict(l=20, r=20, t=20, b=20),
                        showlegend=True,
                        font=dict(size=10),
                        legend=dict(font=dict(size=10))
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No expense data available")
