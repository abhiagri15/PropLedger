import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from streamlit_option_menu import option_menu
from database.database_operations import DatabaseOperations
from database.models import Property, Income, Expense, PropertyType, IncomeType, ExpenseType
from llm.llm_insights import LLMInsights
import config

# Page configuration
st.set_page_config(
    page_title="PropLedger - Rental Property Management",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database and LLM
@st.cache_resource
def get_database():
    return DatabaseOperations()

@st.cache_resource
def get_llm():
    return LLMInsights()

db = get_database()
llm = get_llm()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .insight-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.markdown("# 🏠 PropLedger")
    st.markdown("---")
    
    selected = option_menu(
        menu_title="Navigation",
        options=["Dashboard", "Properties", "Income", "Expenses", "Analytics", "AI Insights"],
        icons=["speedometer2", "house", "cash-coin", "receipt", "graph-up", "robot"],
        menu_icon="cast",
        default_index=0,
    )

# Main content based on selected page
if selected == "Dashboard":
    st.markdown('<h1 class="main-header">🏠 PropLedger Dashboard</h1>', unsafe_allow_html=True)
    
    # Get all properties and their financial data
    properties = db.get_properties()
    
    if not properties:
        st.info("No properties found. Add your first property to get started!")
        st.markdown("### Quick Start")
        st.markdown("1. Go to **Properties** tab to add your first rental property")
        st.markdown("2. Add income and expense records in their respective tabs")
        st.markdown("3. View analytics and AI insights to optimize your portfolio")
    else:
        # Portfolio overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_properties = len(properties)
        total_monthly_rent = sum(prop.monthly_rent for prop in properties)
        total_purchase_price = sum(prop.purchase_price for prop in properties)
        
        # Calculate portfolio-wide financials
        all_income = db.get_all_income()
        all_expenses = db.get_all_expenses()
        total_income = sum(inc.amount for inc in all_income)
        total_expenses = sum(exp.amount for exp in all_expenses)
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
        properties_data = []
        for prop in properties:
            financial_summary = db.get_property_financial_summary(prop.id)
            properties_data.append({
                'Name': prop.name,
                'Address': prop.address,
                'Type': prop.property_type.title(),
                'Monthly Rent': f"${prop.monthly_rent:,.2f}",
                'Total Income': f"${financial_summary['total_income']:,.2f}",
                'Total Expenses': f"${financial_summary['total_expenses']:,.2f}",
                'Net Income': f"${financial_summary['net_income']:,.2f}",
                'ROI': f"{financial_summary['roi']:.2f}%"
            })
        
        df_properties = pd.DataFrame(properties_data)
        st.dataframe(df_properties, use_container_width=True)
        
        # Recent transactions
        st.subheader("Recent Transactions")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Recent Income**")
            recent_income = all_income[:5]  # Last 5 income records
            for inc in recent_income:
                prop_name = next((p.name for p in properties if p.id == inc.property_id), "Unknown")
                st.write(f"• {prop_name}: ${inc.amount:,.2f} - {inc.description} ({inc.transaction_date.strftime('%Y-%m-%d')})")
        
        with col2:
            st.markdown("**Recent Expenses**")
            recent_expenses = all_expenses[:5]  # Last 5 expense records
            for exp in recent_expenses:
                prop_name = next((p.name for p in properties if p.id == exp.property_id), "Unknown")
                st.write(f"• {prop_name}: ${exp.amount:,.2f} - {exp.description} ({exp.transaction_date.strftime('%Y-%m-%d')})")

elif selected == "Properties":
    st.markdown('<h1 class="main-header">🏠 Property Management</h1>', unsafe_allow_html=True)
    
    # Tabs for property management
    tab1, tab2 = st.tabs(["View Properties", "Add/Edit Property"])
    
    with tab1:
        properties = db.get_properties()
        if properties:
            for prop in properties:
                with st.expander(f"{prop.name} - {prop.address}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Type:** {prop.property_type.title()}")
                        st.write(f"**Purchase Price:** ${prop.purchase_price:,.2f}")
                        st.write(f"**Purchase Date:** {prop.purchase_date.strftime('%Y-%m-%d')}")
                        st.write(f"**Monthly Rent:** ${prop.monthly_rent:,.2f}")
                    
                    with col2:
                        financial_summary = db.get_property_financial_summary(prop.id)
                        st.write(f"**Total Income:** ${financial_summary['total_income']:,.2f}")
                        st.write(f"**Total Expenses:** ${financial_summary['total_expenses']:,.2f}")
                        st.write(f"**Net Income:** ${financial_summary['net_income']:,.2f}")
                        st.write(f"**ROI:** {financial_summary['roi']:.2f}%")
                    
                    if prop.description:
                        st.write(f"**Description:** {prop.description}")
        else:
            st.info("No properties found. Add your first property below.")
    
    with tab2:
        st.subheader("Add New Property")
        
        with st.form("add_property_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Property Name *", placeholder="e.g., Downtown Apartment")
                address = st.text_area("Address *", placeholder="123 Main St, City, State")
                property_type = st.selectbox("Property Type *", [pt.value for pt in PropertyType])
                purchase_price = st.number_input("Purchase Price *", min_value=0.0, format="%.2f")
            
            with col2:
                purchase_date = st.date_input("Purchase Date *", value=date.today())
                monthly_rent = st.number_input("Monthly Rent *", min_value=0.0, format="%.2f")
                description = st.text_area("Description", placeholder="Additional details about the property")
            
            submitted = st.form_submit_button("Add Property", type="primary")
            
            if submitted:
                if name and address and purchase_price and monthly_rent:
                    new_property = Property(
                        name=name,
                        address=address,
                        property_type=PropertyType(property_type),
                        purchase_price=purchase_price,
                        purchase_date=datetime.combine(purchase_date, datetime.min.time()),
                        monthly_rent=monthly_rent,
                        description=description if description else None
                    )
                    
                    result = db.create_property(new_property)
                    if result:
                        st.success(f"Property '{name}' added successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to add property. Please try again.")
                else:
                    st.error("Please fill in all required fields.")

elif selected == "Income":
    st.markdown('<h1 class="main-header">💰 Income Tracking</h1>', unsafe_allow_html=True)
    
    # Tabs for income management
    tab1, tab2 = st.tabs(["View Income", "Add Income"])
    
    with tab1:
        properties = db.get_properties()
        if properties:
            # Filter by property
            property_names = {prop.id: prop.name for prop in properties}
            selected_property_id = st.selectbox("Filter by Property", ["All"] + list(property_names.keys()), 
                                              format_func=lambda x: "All" if x == "All" else property_names[x])
            
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
            st.info("No properties found. Please add a property first.")
    
    with tab2:
        properties = db.get_properties()
        if properties:
            st.subheader("Add New Income Record")
            
            with st.form("add_income_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    property_id = st.selectbox("Property *", 
                                             options=[prop.id for prop in properties],
                                             format_func=lambda x: next(prop.name for prop in properties if prop.id == x))
                    amount = st.number_input("Amount *", min_value=0.01, format="%.2f")
                    income_type = st.selectbox("Income Type *", [it.value for it in IncomeType])
                
                with col2:
                    description = st.text_input("Description *", placeholder="e.g., Monthly rent payment")
                    transaction_date = st.date_input("Transaction Date *", value=date.today())
                
                submitted = st.form_submit_button("Add Income", type="primary")
                
                if submitted:
                    new_income = Income(
                        property_id=property_id,
                        amount=amount,
                        income_type=IncomeType(income_type),
                        description=description,
                        transaction_date=datetime.combine(transaction_date, datetime.min.time())
                    )
                    
                    result = db.create_income(new_income)
                    if result:
                        st.success("Income record added successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to add income record. Please try again.")
        else:
            st.info("No properties found. Please add a property first.")

elif selected == "Expenses":
    st.markdown('<h1 class="main-header">💸 Expense Tracking</h1>', unsafe_allow_html=True)
    
    # Tabs for expense management
    tab1, tab2 = st.tabs(["View Expenses", "Add Expense"])
    
    with tab1:
        properties = db.get_properties()
        if properties:
            # Filter by property
            property_names = {prop.id: prop.name for prop in properties}
            selected_property_id = st.selectbox("Filter by Property", ["All"] + list(property_names.keys()), 
                                              format_func=lambda x: "All" if x == "All" else property_names[x])
            
            if selected_property_id == "All":
                expense_records = db.get_all_expenses()
            else:
                expense_records = db.get_expenses_by_property(selected_property_id)
            
            if expense_records:
                # Display expense records
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
                
                df_expenses = pd.DataFrame(expense_data)
                st.dataframe(df_expenses, use_container_width=True)
                
                # Expense summary
                total_expenses = sum(exp.amount for exp in expense_records)
                st.metric("Total Expenses", f"${total_expenses:,.2f}")
            else:
                st.info("No expense records found.")
        else:
            st.info("No properties found. Please add a property first.")
    
    with tab2:
        properties = db.get_properties()
        if properties:
            st.subheader("Add New Expense Record")
            
            with st.form("add_expense_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    property_id = st.selectbox("Property *", 
                                             options=[prop.id for prop in properties],
                                             format_func=lambda x: next(prop.name for prop in properties if prop.id == x))
                    amount = st.number_input("Amount *", min_value=0.01, format="%.2f")
                    expense_type = st.selectbox("Expense Type *", [et.value for et in ExpenseType])
                
                with col2:
                    description = st.text_input("Description *", placeholder="e.g., HVAC maintenance")
                    transaction_date = st.date_input("Transaction Date *", value=date.today())
                    receipt_url = st.text_input("Receipt URL (optional)", placeholder="https://...")
                
                submitted = st.form_submit_button("Add Expense", type="primary")
                
                if submitted:
                    new_expense = Expense(
                        property_id=property_id,
                        amount=amount,
                        expense_type=ExpenseType(expense_type),
                        description=description,
                        transaction_date=datetime.combine(transaction_date, datetime.min.time()),
                        receipt_url=receipt_url if receipt_url else None
                    )
                    
                    result = db.create_expense(new_expense)
                    if result:
                        st.success("Expense record added successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to add expense record. Please try again.")
        else:
            st.info("No properties found. Please add a property first.")

elif selected == "Analytics":
    st.markdown('<h1 class="main-header">📊 Analytics & Reports</h1>', unsafe_allow_html=True)
    
    properties = db.get_properties()
    if not properties:
        st.info("No properties found. Add properties to view analytics.")
    else:
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=date.today() - timedelta(days=365))
        with col2:
            end_date = st.date_input("End Date", value=date.today())
        
        # Property selector
        selected_property_id = st.selectbox("Select Property", 
                                          options=["All"] + [prop.id for prop in properties],
                                          format_func=lambda x: "All Properties" if x == "All" else next(prop.name for prop in properties if prop.id == x))
        
        if selected_property_id == "All":
            # Portfolio-wide analytics
            st.subheader("Portfolio Overview")
            
            # Get all financial data
            all_income = db.get_all_income()
            all_expenses = db.get_all_expenses()
            
            # Filter by date range
            filtered_income = [inc for inc in all_income if start_date <= inc.transaction_date.date() <= end_date]
            filtered_expenses = [exp for exp in all_expenses if start_date <= exp.transaction_date.date() <= end_date]
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Income", f"${sum(inc.amount for inc in filtered_income):,.2f}")
            with col2:
                st.metric("Total Expenses", f"${sum(exp.amount for exp in filtered_expenses):,.2f}")
            with col3:
                net_income = sum(inc.amount for inc in filtered_income) - sum(exp.amount for exp in filtered_expenses)
                st.metric("Net Income", f"${net_income:,.2f}")
            with col4:
                total_rent = sum(prop.monthly_rent for prop in properties)
                st.metric("Monthly Rent Potential", f"${total_rent:,.2f}")
            
            # Income vs Expenses chart
            st.subheader("Income vs Expenses Over Time")
            
            # Group by month
            income_by_month = {}
            expense_by_month = {}
            
            for inc in filtered_income:
                month_key = inc.transaction_date.strftime('%Y-%m')
                if month_key not in income_by_month:
                    income_by_month[month_key] = 0
                income_by_month[month_key] += inc.amount
            
            for exp in filtered_expenses:
                month_key = exp.transaction_date.strftime('%Y-%m')
                if month_key not in expense_by_month:
                    expense_by_month[month_key] = 0
                expense_by_month[month_key] += exp.amount
            
            # Create chart
            months = sorted(set(list(income_by_month.keys()) + list(expense_by_month.keys())))
            income_values = [income_by_month.get(month, 0) for month in months]
            expense_values = [expense_by_month.get(month, 0) for month in months]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=months, y=income_values, mode='lines+markers', name='Income', line=dict(color='green')))
            fig.add_trace(go.Scatter(x=months, y=expense_values, mode='lines+markers', name='Expenses', line=dict(color='red')))
            
            fig.update_layout(title="Monthly Income vs Expenses", xaxis_title="Month", yaxis_title="Amount ($)")
            st.plotly_chart(fig, use_container_width=True)
            
            # Property performance comparison
            st.subheader("Property Performance Comparison")
            property_performance = []
            for prop in properties:
                financial_summary = db.get_property_financial_summary(prop.id, 
                                                                     datetime.combine(start_date, datetime.min.time()),
                                                                     datetime.combine(end_date, datetime.min.time()))
                property_performance.append({
                    'Property': prop.name,
                    'ROI': financial_summary['roi'],
                    'Net Income': financial_summary['net_income'],
                    'Total Income': financial_summary['total_income'],
                    'Total Expenses': financial_summary['total_expenses']
                })
            
            df_performance = pd.DataFrame(property_performance)
            st.dataframe(df_performance, use_container_width=True)
            
            # ROI chart
            fig_roi = px.bar(df_performance, x='Property', y='ROI', title="Property ROI Comparison")
            st.plotly_chart(fig_roi, use_container_width=True)
        
        else:
            # Single property analytics
            prop = next(p for p in properties if p.id == selected_property_id)
            st.subheader(f"Analytics for {prop.name}")
            
            financial_summary = db.get_property_financial_summary(selected_property_id,
                                                                 datetime.combine(start_date, datetime.min.time()),
                                                                 datetime.combine(end_date, datetime.min.time()))
            
            # Property metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Income", f"${financial_summary['total_income']:,.2f}")
            with col2:
                st.metric("Total Expenses", f"${financial_summary['total_expenses']:,.2f}")
            with col3:
                st.metric("Net Income", f"${financial_summary['net_income']:,.2f}")
            with col4:
                st.metric("ROI", f"{financial_summary['roi']:.2f}%")
            
            # Income and expense breakdown by type
            income_records = db.get_income_by_property(selected_property_id)
            expense_records = db.get_expenses_by_property(selected_property_id)
            
            # Filter by date range
            filtered_income = [inc for inc in income_records if start_date <= inc.transaction_date.date() <= end_date]
            filtered_expenses = [exp for exp in expense_records if start_date <= exp.transaction_date.date() <= end_date]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Income by Type")
                income_by_type = {}
                for inc in filtered_income:
                    if inc.income_type not in income_by_type:
                        income_by_type[inc.income_type] = 0
                    income_by_type[inc.income_type] += inc.amount
                
                if income_by_type:
                    fig_income = px.pie(values=list(income_by_type.values()), 
                                      names=list(income_by_type.keys()), 
                                      title="Income Distribution")
                    st.plotly_chart(fig_income, use_container_width=True)
                else:
                    st.info("No income data for selected period")
            
            with col2:
                st.subheader("Expenses by Type")
                expense_by_type = {}
                for exp in filtered_expenses:
                    if exp.expense_type not in expense_by_type:
                        expense_by_type[exp.expense_type] = 0
                    expense_by_type[exp.expense_type] += exp.amount
                
                if expense_by_type:
                    fig_expense = px.pie(values=list(expense_by_type.values()), 
                                       names=list(expense_by_type.keys()), 
                                       title="Expense Distribution")
                    st.plotly_chart(fig_expense, use_container_width=True)
                else:
                    st.info("No expense data for selected period")

elif selected == "AI Insights":
    st.markdown('<h1 class="main-header">🤖 AI-Powered Insights</h1>', unsafe_allow_html=True)
    
    if not llm.enabled:
        st.warning("⚠️ LLM features are disabled. Please configure your OpenAI API key in the environment variables.")
        st.markdown("### Setup Instructions")
        st.markdown("1. Get an OpenAI API key from [OpenAI](https://platform.openai.com/api-keys)")
        st.markdown("2. Create a `.env` file in your project root")
        st.markdown("3. Add your API key: `OPENAI_API_KEY=your_key_here`")
        st.markdown("4. Restart the application")
    else:
        properties = db.get_properties()
        if not properties:
            st.info("No properties found. Add properties to get AI insights.")
        else:
            # Property selector
            selected_property_id = st.selectbox("Select Property for Analysis", 
                                              options=[prop.id for prop in properties],
                                              format_func=lambda x: next(prop.name for prop in properties if prop.id == x))
            
            if selected_property_id:
                prop = next(p for p in properties if p.id == selected_property_id)
                
                # Get financial data
                financial_summary = db.get_property_financial_summary(selected_property_id)
                income_records = db.get_income_by_property(selected_property_id)
                expense_records = db.get_expenses_by_property(selected_property_id)
                
                # Convert to dictionaries for LLM
                property_data = {
                    'name': prop.name,
                    'address': prop.address,
                    'property_type': prop.property_type,
                    'purchase_price': prop.purchase_price,
                    'monthly_rent': prop.monthly_rent
                }
                
                # Generate insights
                if st.button("Generate Financial Insights", type="primary"):
                    with st.spinner("Generating insights..."):
                        insights = llm.generate_financial_insights(property_data, financial_summary)
                        st.markdown(f'<div class="insight-box">{insights}</div>', unsafe_allow_html=True)
                
                # Expense analysis
                if expense_records:
                    if st.button("Analyze Expense Patterns"):
                        with st.spinner("Analyzing expenses..."):
                            expense_data = [{'expense_type': exp.expense_type, 'amount': exp.amount} for exp in expense_records]
                            expense_analysis = llm.generate_expense_analysis(expense_data)
                            st.markdown(f'<div class="insight-box">{expense_analysis}</div>', unsafe_allow_html=True)
                
                # Market insights
                if st.button("Get Market Insights"):
                    with st.spinner("Analyzing market conditions..."):
                        market_insights = llm.generate_rental_market_insights(property_data)
                        st.markdown(f'<div class="insight-box">{market_insights}</div>', unsafe_allow_html=True)
            
            # Portfolio-level insights
            if len(properties) > 1:
                st.markdown("---")
                st.subheader("Portfolio Analysis")
                
                if st.button("Generate Portfolio Recommendations"):
                    with st.spinner("Analyzing portfolio..."):
                        portfolio_data = []
                        for prop in properties:
                            financial_summary = db.get_property_financial_summary(prop.id)
                            portfolio_data.append({
                                'name': prop.name,
                                'property_type': prop.property_type,
                                'purchase_price': prop.purchase_price,
                                'monthly_rent': prop.monthly_rent,
                                'roi': financial_summary['roi'],
                                'net_income': financial_summary['net_income']
                            })
                        
                        portfolio_insights = llm.generate_investment_recommendations(portfolio_data)
                        st.markdown(f'<div class="insight-box">{portfolio_insights}</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit, Supabase, and OpenAI")
