"""
Analytics page for PropLedger
Extracted from app_auth.py for better maintainability
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database.database_operations import DatabaseOperations

def render_analytics():
    """Render the Analytics page"""
    st.markdown('<h1 class="main-header">📊 Analytics & Reports</h1>', unsafe_allow_html=True)

    try:
        # Check if demo mode
        is_demo_mode = False
        if st.session_state.user:
            if hasattr(st.session_state.user, 'email'):
                is_demo_mode = getattr(st.session_state.user, 'email', '') == 'demo@example.com'
            else:
                is_demo_mode = st.session_state.user.get('email', '') == 'demo@example.com'

        if is_demo_mode:
            # Demo mode - show sample analytics data
            st.markdown('<div class="info-box">🎯 <strong>Demo Mode</strong> - Showing sample analytics data. Sign up to see your own analytics!</div>', unsafe_allow_html=True)

            # Demo financial overview
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Properties", "3", "1")
            with col2:
                st.metric("Monthly Revenue", "$4,500", "5.2%")
            with col3:
                st.metric("Total Expenses", "$2,100", "-2.1%")
            with col4:
                st.metric("Net Profit", "$2,400", "8.3%")

            st.markdown("---")

            # Demo charts
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📈 Revenue Trend")
                # Sample data for demo
                dates = [datetime.now() - timedelta(days=30-i) for i in range(30)]
                revenue = [4000 + i*20 + (i%7)*100 for i in range(30)]

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=dates, y=revenue, mode='lines+markers', name='Revenue', line=dict(color='#2E8B57')))
                fig.update_layout(title="Monthly Revenue Trend", xaxis_title="Date", yaxis_title="Revenue ($)")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("🏠 Property Performance")
                # Sample property data
                properties = ['Downtown Apt', 'Suburban House', 'Commercial Space']
                income = [1800, 2200, 500]
                expenses = [800, 1200, 200]

                fig = go.Figure()
                fig.add_trace(go.Bar(name='Income', x=properties, y=income, marker_color='#2E8B57'))
                fig.add_trace(go.Bar(name='Expenses', x=properties, y=expenses, marker_color='#DC143C'))
                fig.update_layout(title="Property Income vs Expenses", barmode='group')
                st.plotly_chart(fig, use_container_width=True)

            # Demo expense breakdown
            st.subheader("💰 Expense Breakdown")
            col1, col2 = st.columns(2)

            with col1:
                # Pie chart for expense categories
                categories = ['Maintenance', 'Utilities', 'Insurance', 'Taxes', 'Other']
                amounts = [800, 600, 400, 200, 100]

                fig = go.Figure(data=[go.Pie(labels=categories, values=amounts, hole=0.3)])
                fig.update_layout(title="Expense Categories")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Monthly expense trend
                months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
                monthly_expenses = [1800, 1900, 2100, 2000, 2200, 2100]

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=months, y=monthly_expenses, mode='lines+markers',
                                       name='Monthly Expenses', line=dict(color='#DC143C')))
                fig.update_layout(title="Monthly Expense Trend", xaxis_title="Month", yaxis_title="Expenses ($)")
                st.plotly_chart(fig, use_container_width=True)
            return

        # Get selected organization
        selected_org_id = st.session_state.get('selected_organization')
        if not selected_org_id:
            st.error("Please select an organization first.")
            return

        # Get organization name
        db = DatabaseOperations()
        org = db.get_organization_by_id(selected_org_id)
        org_name = org.name if org else "Unknown Organization"

        # Check if demo mode
        is_demo_mode = False
        if st.session_state.user:
            if hasattr(st.session_state.user, 'email'):
                is_demo_mode = getattr(st.session_state.user, 'email', '') == 'demo@example.com'
            else:
                is_demo_mode = st.session_state.user.get('email', '') == 'demo@example.com'

        if is_demo_mode:
            # Demo analytics with sample data
            st.info("🎯 **DEMO MODE** - Showing sample analytics data")

            # Demo financial overview
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Properties", "3", "1")
            with col2:
                st.metric("Monthly Revenue", "$4,500", "5.2%")
            with col3:
                st.metric("Total Expenses", "$2,100", "-2.1%")
            with col4:
                st.metric("Net Profit", "$2,400", "8.3%")

            st.markdown("---")

            # Demo charts
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📈 Revenue Trend")
                # Sample data for demo

                dates = [datetime.now() - timedelta(days=30-i) for i in range(30)]
                revenue = [4000 + i*20 + (i%7)*100 for i in range(30)]

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=dates, y=revenue, mode='lines+markers', name='Revenue', line=dict(color='#2E8B57')))
                fig.update_layout(title="Monthly Revenue Trend", xaxis_title="Date", yaxis_title="Revenue ($)")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("🏠 Property Performance")
                # Sample property data
                properties = ['Downtown Apt', 'Suburban House', 'Commercial Space']
                income = [1800, 2200, 500]
                expenses = [800, 1200, 200]

                fig = go.Figure()
                fig.add_trace(go.Bar(name='Income', x=properties, y=income, marker_color='#2E8B57'))
                fig.add_trace(go.Bar(name='Expenses', x=properties, y=expenses, marker_color='#DC143C'))
                fig.update_layout(title="Property Income vs Expenses", barmode='group')
                st.plotly_chart(fig, use_container_width=True)

            # Demo expense breakdown
            st.subheader("💰 Expense Breakdown")
            col1, col2 = st.columns(2)

            with col1:
                # Pie chart for expense categories
                categories = ['Maintenance', 'Utilities', 'Insurance', 'Taxes', 'Other']
                amounts = [800, 600, 400, 200, 100]

                fig = go.Figure(data=[go.Pie(labels=categories, values=amounts, hole=0.3)])
                fig.update_layout(title="Expense Categories")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Monthly expense trend
                months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
                monthly_expenses = [1800, 1900, 2100, 2000, 2200, 2100]

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=months, y=monthly_expenses, mode='lines+markers',
                                       name='Monthly Expenses', line=dict(color='#DC143C')))
                fig.update_layout(title="Monthly Expense Trend", xaxis_title="Month", yaxis_title="Expenses ($)")
                st.plotly_chart(fig, use_container_width=True)
            return

        # ... existing real analytics code continues below unchanged ...
        # Real analytics for selected organization
        # Fetch income and expenses for org and render basic KPIs and charts
        income_result = db.supabase.table("income").select("*").eq("organization_id", selected_org_id).order("transaction_date").execute()
        expense_result = db.supabase.table("expenses").select("*").eq("organization_id", selected_org_id).order("transaction_date").execute()

        income_rows = income_result.data or []
        expense_rows = expense_result.data or []

        inc_df = pd.DataFrame(income_rows)
        exp_df = pd.DataFrame(expense_rows)

        if inc_df.empty and exp_df.empty:
            st.info("No financial data found for this organization.")
            return

        total_income = float(inc_df['amount'].sum()) if not inc_df.empty else 0.0
        total_expenses = float(exp_df['amount'].sum()) if not exp_df.empty else 0.0
        net_income = total_income - total_expenses

        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric("Total Income", f"${total_income:,.2f}")
        with k2:
            st.metric("Total Expenses", f"${total_expenses:,.2f}")
        with k3:
            delta = (net_income / total_income * 100) if total_income else 0
            st.metric("Net Income", f"${net_income:,.2f}", f"{delta:.1f}%")

        st.markdown("---")
        c1, c2 = st.columns(2)

        # Monthly trend chart
        with c1:
            st.subheader("Monthly Trend")
            def to_month_str(x):
                return str(x)[:7]
            if not inc_df.empty:
                inc_df['month'] = inc_df['transaction_date'].map(to_month_str)
                inc_m = inc_df.groupby('month')['amount'].sum()
            else:
                inc_m = pd.Series(dtype=float)
            if not exp_df.empty:
                exp_df['month'] = exp_df['transaction_date'].map(to_month_str)
                exp_m = exp_df.groupby('month')['amount'].sum()
            else:
                exp_m = pd.Series(dtype=float)
            months = sorted(set(inc_m.index).union(exp_m.index))
            y_inc = [float(inc_m.get(m, 0)) for m in months]
            y_exp = [float(exp_m.get(m, 0)) for m in months]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=months, y=y_inc, mode='lines+markers', name='Income', line=dict(color='#2E8B57')))
            fig.add_trace(go.Scatter(x=months, y=y_exp, mode='lines+markers', name='Expenses', line=dict(color='#DC143C')))
            fig.update_layout(xaxis_title="Month", yaxis_title="Amount ($)")
            st.plotly_chart(fig, use_container_width=True)

        # Category breakdown pies
        with c2:
            st.subheader("Category Breakdown")
            pc1, pc2 = st.columns(2)
            if not inc_df.empty and 'income_type' in inc_df.columns:
                inc_cat = inc_df.groupby('income_type')['amount'].sum().reset_index()
                pc1.plotly_chart(go.Figure(data=[go.Pie(labels=inc_cat['income_type'], values=inc_cat['amount'])]).update_layout(title_text="Income"), use_container_width=True)
            if not exp_df.empty and 'expense_type' in exp_df.columns:
                exp_cat = exp_df.groupby('expense_type')['amount'].sum().reset_index()
                pc2.plotly_chart(go.Figure(data=[go.Pie(labels=exp_cat['expense_type'], values=exp_cat['amount'])]).update_layout(title_text="Expenses"), use_container_width=True)

        return
    except UnboundLocalError as e:
        st.error("Analytics error: please refresh the page. If it persists, reselect your organization.")
    except Exception as e:
        st.error(f"Analytics error: {str(e)}")
