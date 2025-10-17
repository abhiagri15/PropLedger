"""
Budgets page for PropLedger
Full implementation with Supabase database integration
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime
from database.database_operations import DatabaseOperations

def render_budgets():
    """Render the Budgets page with full functionality"""
    st.markdown('<h1 class="main-header">📊 Budget Management</h1>', unsafe_allow_html=True)

    db = DatabaseOperations()

    if st.session_state.get('selected_organization'):
        try:
            selected_org_id = st.session_state.selected_organization

            # Get organization name
            org = db.get_organization_by_id(selected_org_id)
            org_name = org.name if org else "Unknown Organization"

            # Budget tabs
            budget_tab1, budget_tab2, budget_tab3, budget_tab4 = st.tabs([
                "📋 Budget vs Actual", "➕ Create Budget", "📈 Budget Trends", "📊 Budget Analysis"
            ])

            with budget_tab1:
                st.subheader("📋 Budget vs Actual")

                # Period selector
                col1, col2 = st.columns(2)

                with col1:
                    period_type = st.selectbox("Period Type", ["Monthly", "Yearly", "Custom"], key="budget_period")

                with col2:
                    if period_type == "Monthly":
                        month_names = ["January", "February", "March", "April", "May", "June",
                                     "July", "August", "September", "October", "November", "December"]
                        budget_month = st.selectbox("Month", month_names, index=date.today().month - 1)
                        budget_year = st.selectbox("Year", range(2020, 2030), index=date.today().year - 2020)
                        budget_month_num = month_names.index(budget_month) + 1
                    elif period_type == "Yearly":
                        budget_year = st.selectbox("Year", range(2020, 2030), index=date.today().year - 2020)
                        budget_month_num = None
                    else:
                        col_start, col_end = st.columns(2)
                        with col_start:
                            start_date = st.date_input("Start Date", value=date.today().replace(day=1))
                        with col_end:
                            end_date = st.date_input("End Date", value=date.today())

                # Get budget data from database
                try:
                    # Get categories first
                    categories_result = db.client.table("categories").select("*").execute()
                    categories = {cat['id']: cat['name'] for cat in categories_result.data} if categories_result.data else {}

                    # Get budget lines for the organization
                    budget_query = db.client.table("budget_lines").select("*").eq("company_id", selected_org_id)

                    if period_type == "Monthly" and budget_month_num:
                        budget_query = budget_query.eq("period_year", budget_year).eq("period_month", budget_month_num)
                    elif period_type == "Yearly":
                        budget_query = budget_query.eq("period_year", budget_year)

                    budget_result = budget_query.execute()
                    budget_lines = budget_result.data if budget_result.data else []

                    if budget_lines:
                        # Get actual expenses for comparison
                        expenses = db.get_all_expenses()
                        org_expenses = [e for e in expenses if hasattr(e, 'property_id')]

                        # Calculate budget vs actual
                        budget_vs_actual = []

                        for budget in budget_lines:
                            category_id = budget.get('category_id')
                            category_name = categories.get(category_id, 'Unknown')
                            budgeted_amount = float(budget.get('amount_planned', 0))

                            # Calculate actual expenses for this category
                            actual_amount = 0
                            if period_type == "Monthly":
                                for expense in org_expenses:
                                    exp_date = expense.transaction_date
                                    if (exp_date.year == budget_year and
                                        exp_date.month == budget_month_num):
                                        actual_amount += float(expense.amount)
                            elif period_type == "Yearly":
                                for expense in org_expenses:
                                    if expense.transaction_date.year == budget_year:
                                        actual_amount += float(expense.amount)

                            variance = actual_amount - budgeted_amount
                            variance_percentage = (variance / budgeted_amount * 100) if budgeted_amount > 0 else 0

                            budget_vs_actual.append({
                                'Category': category_name,
                                'Budgeted': budgeted_amount,
                                'Actual': actual_amount,
                                'Variance': variance,
                                'Variance %': variance_percentage
                            })

                        # Display results
                        if budget_vs_actual:
                            # Summary metrics
                            col1, col2, col3, col4 = st.columns(4)

                            total_budgeted = sum(item['Budgeted'] for item in budget_vs_actual)
                            total_actual = sum(item['Actual'] for item in budget_vs_actual)
                            total_variance = total_actual - total_budgeted
                            total_variance_pct = (total_variance / total_budgeted * 100) if total_budgeted > 0 else 0

                            with col1:
                                st.metric("Total Budgeted", f"${total_budgeted:,.2f}")
                            with col2:
                                st.metric("Total Actual", f"${total_actual:,.2f}")
                            with col3:
                                st.metric("Total Variance", f"${total_variance:,.2f}",
                                        f"{total_variance_pct:+.1f}%")
                            with col4:
                                utilization = (total_actual / total_budgeted * 100) if total_budgeted > 0 else 0
                                st.metric("Budget Utilization", f"{utilization:.1f}%")

                            # Data table
                            st.markdown("### Budget Comparison Details")
                            df_budget = pd.DataFrame(budget_vs_actual)

                            # Format columns for display
                            df_display = df_budget.copy()
                            df_display['Budgeted'] = df_display['Budgeted'].apply(lambda x: f"${x:,.2f}")
                            df_display['Actual'] = df_display['Actual'].apply(lambda x: f"${x:,.2f}")
                            df_display['Variance'] = df_display['Variance'].apply(lambda x: f"${x:,.2f}")
                            df_display['Variance %'] = df_display['Variance %'].apply(lambda x: f"{x:+.1f}%")

                            st.dataframe(df_display, use_container_width=True, hide_index=True)

                            # Visualization
                            st.markdown("### Visual Comparison")

                            fig = go.Figure()
                            fig.add_trace(go.Bar(
                                name='Budgeted',
                                x=df_budget['Category'],
                                y=df_budget['Budgeted'],
                                marker_color='#4169E1'
                            ))
                            fig.add_trace(go.Bar(
                                name='Actual',
                                x=df_budget['Category'],
                                y=df_budget['Actual'],
                                marker_color='#2E8B57'
                            ))
                            fig.update_layout(
                                title="Budget vs Actual by Category",
                                barmode='group',
                                xaxis_title="Category",
                                yaxis_title="Amount ($)"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No budget data found for the selected period. Create budgets in the 'Create Budget' tab.")

                except Exception as e:
                    if "budget_lines" in str(e):
                        st.error("Budget tables not properly configured. Please contact support.")
                    else:
                        st.error(f"Error loading budget data: {str(e)}")

            with budget_tab2:
                st.subheader("➕ Create Budget")

                # Get categories for dropdown
                try:
                    categories_result = db.client.table("categories").select("*").execute()
                    categories_list = categories_result.data if categories_result.data else []

                    if not categories_list:
                        st.warning("No categories found. Creating default categories...")
                        # Create default categories
                        default_categories = [
                            {"name": "Maintenance", "type": "expense"},
                            {"name": "Utilities", "type": "expense"},
                            {"name": "Insurance", "type": "expense"},
                            {"name": "Property Tax", "type": "expense"},
                            {"name": "HOA Fees", "type": "expense"},
                            {"name": "Management", "type": "expense"},
                            {"name": "Repairs", "type": "expense"},
                            {"name": "Marketing", "type": "expense"},
                            {"name": "Legal", "type": "expense"},
                            {"name": "Other", "type": "expense"}
                        ]

                        for cat in default_categories:
                            db.client.table("categories").insert(cat).execute()

                        # Refresh categories
                        categories_result = db.client.table("categories").select("*").execute()
                        categories_list = categories_result.data if categories_result.data else []

                    with st.form("create_budget_form"):
                        col1, col2 = st.columns(2)

                        with col1:
                            # Budget scope
                            budget_scope = st.selectbox("Scope", ["Organization", "Property"])

                            if budget_scope == "Property":
                                properties = db.get_properties()
                                org_properties = [p for p in properties if p.organization_id == selected_org_id]
                                if org_properties:
                                    property_names = {p.id: p.name for p in org_properties}
                                    selected_property = st.selectbox("Property",
                                                                    options=list(property_names.keys()),
                                                                    format_func=lambda x: property_names[x])
                                else:
                                    st.error("No properties found. Add properties first.")
                                    selected_property = None
                            else:
                                selected_property = None

                            # Category selection
                            category_names = {cat['id']: cat['name'] for cat in categories_list}
                            selected_category = st.selectbox("Category",
                                                           options=list(category_names.keys()),
                                                           format_func=lambda x: category_names[x])

                        with col2:
                            # Period selection
                            period_year = st.selectbox("Year", range(2020, 2030),
                                                      index=date.today().year - 2020)

                            month_names = ["January", "February", "March", "April", "May", "June",
                                         "July", "August", "September", "October", "November", "December"]
                            period_month = st.selectbox("Month", month_names,
                                                       index=date.today().month - 1)
                            period_month_num = month_names.index(period_month) + 1

                            # Amount
                            amount_planned = st.number_input("Budget Amount ($)",
                                                           min_value=0.01,
                                                           step=10.0,
                                                           value=1000.0)

                        # Notes
                        notes = st.text_area("Notes (Optional)", height=100)

                        # Submit button
                        submitted = st.form_submit_button("Create Budget", type="primary", use_container_width=True)

                        if submitted:
                            if selected_category and amount_planned > 0:
                                try:
                                    # Prepare budget data
                                    budget_data = {
                                        'company_id': selected_org_id,
                                        'category_id': selected_category,
                                        'amount_planned': amount_planned,
                                        'period_year': period_year,
                                        'period_month': period_month_num,
                                        'scope_type': 'PROPERTY' if budget_scope == "Property" else 'ORGANIZATION',
                                        'scope_id': selected_property if budget_scope == "Property" else selected_org_id,
                                        'notes': notes if notes else None
                                    }

                                    # Insert into database
                                    result = db.client.table("budget_lines").insert(budget_data).execute()

                                    if result.data:
                                        st.success(f"✅ Budget created successfully for {category_names[selected_category]}!")
                                        st.balloons()
                                        st.rerun()
                                    else:
                                        st.error("Failed to create budget.")

                                except Exception as e:
                                    st.error(f"Error creating budget: {str(e)}")
                            else:
                                st.error("Please fill in all required fields.")

                except Exception as e:
                    st.error(f"Error loading categories: {str(e)}")

            with budget_tab3:
                st.subheader("📈 Budget Trends")

                # Period selector
                trend_year = st.selectbox("Select Year", range(2020, 2030),
                                        index=date.today().year - 2020, key="trend_year")

                try:
                    # Get all budgets for the year
                    budget_result = db.client.table("budget_lines").select("*") \
                        .eq("company_id", selected_org_id) \
                        .eq("period_year", trend_year) \
                        .execute()

                    if budget_result.data:
                        # Get categories
                        categories_result = db.client.table("categories").select("*").execute()
                        categories = {cat['id']: cat['name'] for cat in categories_result.data}

                        # Prepare data for visualization
                        monthly_budgets = {}
                        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

                        for budget in budget_result.data:
                            month = budget.get('period_month', 1) - 1
                            amount = float(budget.get('amount_planned', 0))

                            if month not in monthly_budgets:
                                monthly_budgets[month] = 0
                            monthly_budgets[month] += amount

                        # Create dataframe
                        trend_data = []
                        for month_idx in range(12):
                            trend_data.append({
                                'Month': month_names[month_idx],
                                'Budget': monthly_budgets.get(month_idx, 0)
                            })

                        df_trends = pd.DataFrame(trend_data)

                        # Visualization
                        col1, col2 = st.columns(2)

                        with col1:
                            # Line chart
                            fig_line = px.line(df_trends, x='Month', y='Budget',
                                             title=f"Monthly Budget Trend - {trend_year}",
                                             markers=True)
                            fig_line.update_layout(yaxis_title="Budget Amount ($)")
                            st.plotly_chart(fig_line, use_container_width=True)

                        with col2:
                            # Bar chart
                            fig_bar = px.bar(df_trends, x='Month', y='Budget',
                                           title=f"Monthly Budget Breakdown - {trend_year}",
                                           color='Budget',
                                           color_continuous_scale='Blues')
                            fig_bar.update_layout(yaxis_title="Budget Amount ($)")
                            st.plotly_chart(fig_bar, use_container_width=True)

                        # Summary statistics
                        st.markdown("### Summary Statistics")
                        col1, col2, col3, col4 = st.columns(4)

                        total_budget = df_trends['Budget'].sum()
                        avg_budget = df_trends['Budget'].mean()
                        max_budget = df_trends['Budget'].max()
                        min_budget = df_trends[df_trends['Budget'] > 0]['Budget'].min() if any(df_trends['Budget'] > 0) else 0

                        with col1:
                            st.metric("Total Annual Budget", f"${total_budget:,.2f}")
                        with col2:
                            st.metric("Average Monthly", f"${avg_budget:,.2f}")
                        with col3:
                            st.metric("Highest Month", f"${max_budget:,.2f}")
                        with col4:
                            st.metric("Lowest Month", f"${min_budget:,.2f}")

                        # Category breakdown
                        st.markdown("### Budget by Category")

                        category_budgets = {}
                        for budget in budget_result.data:
                            cat_id = budget.get('category_id')
                            cat_name = categories.get(cat_id, 'Unknown')
                            amount = float(budget.get('amount_planned', 0))

                            if cat_name not in category_budgets:
                                category_budgets[cat_name] = 0
                            category_budgets[cat_name] += amount

                        if category_budgets:
                            df_categories = pd.DataFrame(list(category_budgets.items()),
                                                       columns=['Category', 'Total Budget'])

                            fig_pie = px.pie(df_categories, values='Total Budget', names='Category',
                                           title=f"Budget Distribution by Category - {trend_year}")
                            st.plotly_chart(fig_pie, use_container_width=True)

                    else:
                        st.info(f"No budget data found for {trend_year}. Create budgets in the 'Create Budget' tab.")

                except Exception as e:
                    st.error(f"Error loading budget trends: {str(e)}")

            with budget_tab4:
                st.subheader("📊 Budget Analysis")

                # Get current period budgets
                current_year = date.today().year
                current_month = date.today().month

                try:
                    # Get budgets for current period
                    budget_result = db.client.table("budget_lines").select("*") \
                        .eq("company_id", selected_org_id) \
                        .eq("period_year", current_year) \
                        .eq("period_month", current_month) \
                        .execute()

                    if budget_result.data:
                        # Get categories
                        categories_result = db.client.table("categories").select("*").execute()
                        categories = {cat['id']: cat['name'] for cat in categories_result.data}

                        # Get actual expenses
                        expenses = db.get_all_expenses()

                        # Analysis metrics
                        st.markdown("### Current Month Analysis")

                        total_budgeted = sum(float(b['amount_planned']) for b in budget_result.data)

                        # Calculate actual expenses for current month
                        actual_expenses = 0
                        for expense in expenses:
                            if (hasattr(expense, 'transaction_date') and
                                expense.transaction_date.year == current_year and
                                expense.transaction_date.month == current_month):
                                actual_expenses += float(expense.amount)

                        # Metrics
                        col1, col2, col3, col4 = st.columns(4)

                        variance = actual_expenses - total_budgeted
                        variance_pct = (variance / total_budgeted * 100) if total_budgeted > 0 else 0
                        utilization = (actual_expenses / total_budgeted * 100) if total_budgeted > 0 else 0
                        remaining = max(0, total_budgeted - actual_expenses)

                        with col1:
                            st.metric("Budget Remaining", f"${remaining:,.2f}")
                        with col2:
                            st.metric("Utilization", f"{utilization:.1f}%",
                                    delta=f"{variance_pct:+.1f}%" if variance_pct != 0 else None)
                        with col3:
                            st.metric("Days Remaining", f"{30 - date.today().day} days")
                        with col4:
                            daily_avg = actual_expenses / date.today().day if date.today().day > 0 else 0
                            st.metric("Daily Average", f"${daily_avg:,.2f}")

                        # Recommendations
                        st.markdown("### Recommendations")

                        recommendations = []

                        if utilization > 90:
                            recommendations.append("⚠️ **High Budget Utilization**: Consider reviewing expenses for cost-saving opportunities.")
                        elif utilization > 110:
                            recommendations.append("🚨 **Over Budget**: Immediate action needed to control expenses.")
                        elif utilization < 50 and date.today().day > 15:
                            recommendations.append("✅ **Under Budget**: Good expense control. Consider reallocating unused funds.")

                        if variance_pct > 20:
                            recommendations.append("📊 **Significant Variance**: Review budget assumptions for accuracy.")

                        if daily_avg * 30 > total_budgeted:
                            recommendations.append("📈 **Trending Over Budget**: Current spending rate will exceed budget.")

                        if recommendations:
                            for rec in recommendations:
                                st.markdown(rec)
                        else:
                            st.success("✅ Budget performance is on track!")

                        # Category performance
                        st.markdown("### Category Performance")

                        category_performance = []
                        for budget in budget_result.data:
                            cat_id = budget['category_id']
                            cat_name = categories.get(cat_id, 'Unknown')
                            budgeted = float(budget['amount_planned'])

                            # Calculate actual for this category (simplified)
                            actual = actual_expenses * (budgeted / total_budgeted) if total_budgeted > 0 else 0

                            performance = (actual / budgeted * 100) if budgeted > 0 else 0

                            category_performance.append({
                                'Category': cat_name,
                                'Budgeted': f"${budgeted:,.2f}",
                                'Performance': f"{performance:.1f}%",
                                'Status': '✅' if performance <= 100 else '⚠️'
                            })

                        df_performance = pd.DataFrame(category_performance)
                        st.dataframe(df_performance, use_container_width=True, hide_index=True)

                    else:
                        st.info("No budget data for current month. Create budgets in the 'Create Budget' tab.")

                except Exception as e:
                    st.error(f"Error loading budget analysis: {str(e)}")

        except Exception as e:
            st.error(f"Error in Budget module: {str(e)}")
    else:
        st.warning("Please select an organization first to access budget management.")