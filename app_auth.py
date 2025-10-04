import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from streamlit_option_menu import option_menu
from database.supabase_client import get_supabase_client
from database.database_operations import DatabaseOperations
from database.models import Property, Income, Expense, PropertyType, IncomeType, ExpenseType, Organization, UserOrganization
from llm.llm_insights import LLMInsights
import config
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="PropLedger - Rental Property Management",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    .auth-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        border: 1px solid #ddd;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        background-color: #f9f9f9;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
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

def initialize_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'auth_mode' not in st.session_state:
        st.session_state.auth_mode = 'login'  # 'login' or 'signup'

def show_auth_page():
    """Display authentication page"""
    st.markdown('<h1 class="main-header">🏠 PropLedger</h1>', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center; margin-bottom: 2rem;">Rental Property Management System</div>', unsafe_allow_html=True)
    
    # Create two columns for login/signup
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.markdown("### 🔐 Sign In")
        
        # Use a key to reset form after successful submission
        login_form_key = f"login_form_{st.session_state.get('login_form_reset_counter', 0)}"
        
        # Create a container for the form
        login_container = st.container()
        
        with login_container:
            with st.form(login_form_key):
                email = st.text_input("Email", key=f"login_email_{st.session_state.get('login_form_reset_counter', 0)}", placeholder="your@email.com")
                password = st.text_input("Password", type="password", key=f"login_password_{st.session_state.get('login_form_reset_counter', 0)}", placeholder="Enter your password")
                login_submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)
            
            if login_submitted:
                if email and password:
                    try:
                        supabase = get_supabase_client()
                        response = supabase.auth.sign_in_with_password({
                            "email": email,
                            "password": password
                        })
                        
                        if response.user:
                            st.session_state.authenticated = True
                            st.session_state.user = response.user
                            st.success("✅ Successfully signed in!")
                            # Clear the form by incrementing reset counter
                            st.session_state.login_form_reset_counter = st.session_state.get('login_form_reset_counter', 0) + 1
                            st.rerun()
                        else:
                            st.error("❌ Invalid email or password")
                    except Exception as e:
                        st.error(f"❌ Login failed: {str(e)}")
                else:
                    st.error("❌ Please fill in all fields")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.markdown("### 📝 Sign Up")
        
        # Use a key to reset form after successful submission
        signup_form_key = f"signup_form_{st.session_state.get('signup_form_reset_counter', 0)}"
        
        # Create a container for the form
        signup_container = st.container()
        
        with signup_container:
            with st.form(signup_form_key):
                signup_email = st.text_input("Email", key=f"signup_email_{st.session_state.get('signup_form_reset_counter', 0)}", placeholder="your@email.com")
                signup_password = st.text_input("Password", type="password", key=f"signup_password_{st.session_state.get('signup_form_reset_counter', 0)}", placeholder="Create a password")
                confirm_password = st.text_input("Confirm Password", type="password", key=f"confirm_password_{st.session_state.get('signup_form_reset_counter', 0)}", placeholder="Confirm your password")
                signup_organization = st.text_input("Organization Name", key=f"signup_organization_{st.session_state.get('signup_form_reset_counter', 0)}", placeholder="Your company/organization name")
                signup_submitted = st.form_submit_button("Sign Up", type="primary", use_container_width=True)
            
            if signup_submitted:
                if signup_email and signup_password and confirm_password and signup_organization:
                    if signup_password != confirm_password:
                        st.error("❌ Passwords do not match")
                    elif len(signup_password) < 6:
                        st.error("❌ Password must be at least 6 characters")
                    else:
                        try:
                            supabase = get_supabase_client()
                            response = supabase.auth.sign_up({
                                "email": signup_email,
                                "password": signup_password
                            })
                            
                            if response.user:
                                # Create organization for the new user
                                try:
                                    # First create the organization
                                    org_response = supabase.table("organizations").insert({
                                        "name": signup_organization,
                                        "description": f"Organization created by {signup_email}"
                                    }).execute()
                                    
                                    if org_response.data:
                                        org_id = org_response.data[0]["id"]
                                        
                                        # Add user to organization as owner
                                        user_org_response = supabase.table("user_organizations").insert({
                                            "user_id": response.user.id,
                                            "organization_id": org_id,
                                            "role": "owner"
                                        }).execute()
                                        
                                        if user_org_response.data:
                                            # Set the created organization as selected
                                            st.session_state.selected_organization = org_id
                                            st.success("✅ Account and organization created successfully! Please check your email to verify your account.")
                                            st.info("📧 A verification email has been sent to your email address.")
                                        else:
                                            st.success("✅ Account created successfully! Please check your email to verify your account.")
                                            st.warning("⚠️ Organization creation failed, but you can create one later.")
                                    else:
                                        st.success("✅ Account created successfully! Please check your email to verify your account.")
                                        st.warning("⚠️ Organization creation failed, but you can create one later.")
                                except Exception as org_error:
                                    st.success("✅ Account created successfully! Please check your email to verify your account.")
                                    st.warning(f"⚠️ Organization creation failed: {str(org_error)}")
                                
                                # Clear the form by incrementing reset counter (only once at the end)
                                st.session_state.signup_form_reset_counter = st.session_state.get('signup_form_reset_counter', 0) + 1
                                st.rerun()
                            else:
                                st.error("❌ Failed to create account. Email might already be in use.")
                        except Exception as e:
                            st.error(f"❌ Sign up failed: {str(e)}")
                else:
                    st.error("❌ Please fill in all fields")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Demo access
    st.markdown("---")
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown("### 🎯 Want to try without signing up?")
    st.markdown("Click the button below to access the demo version with sample data.")
    if st.button("🚀 Try Demo Version", use_container_width=True):
        st.session_state.authenticated = True
        st.session_state.user = {"email": "demo@example.com", "user_metadata": {"full_name": "Demo User"}}
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def show_main_app():
    """Display the main application"""
    # Initialize database and LLM
    @st.cache_resource
    def get_database():
        return DatabaseOperations()

    @st.cache_resource
    def get_llm():
        return LLMInsights()

    db = get_database()
    llm = get_llm()

    # Sidebar navigation
    with st.sidebar:
        st.markdown("# 🏠 PropLedger")
        
        # User info - Compact
        if st.session_state.user:
            # Handle both dict and User object types
            if hasattr(st.session_state.user, 'email'):
                # User object from Supabase
                user_email = getattr(st.session_state.user, 'email', 'Unknown')
                user_metadata = getattr(st.session_state.user, 'user_metadata', {})
                user_name = user_metadata.get('full_name', user_email) if isinstance(user_metadata, dict) else user_email
                user_id = getattr(st.session_state.user, 'id', None)
            else:
                # Dictionary format (demo mode)
                user_email = st.session_state.user.get('email', 'Unknown')
                user_name = st.session_state.user.get('user_metadata', {}).get('full_name', user_email)
                user_id = st.session_state.user.get('id', None)
            
            st.markdown(f"**{user_name}**")
            
            # Organization selection - Compact
            if user_id:
                db = DatabaseOperations()
                organizations = db.get_user_organizations(user_id)
                if organizations:
                    org_names = [org.name for org in organizations]
                    if 'selected_organization' not in st.session_state:
                        st.session_state.selected_organization = organizations[0].id
                    
                    # Find the index of the selected organization
                    selected_index = 0
                    if st.session_state.selected_organization:
                        try:
                            selected_org_name = next(org.name for org in organizations if org.id == st.session_state.selected_organization)
                            selected_index = org_names.index(selected_org_name)
                        except (StopIteration, ValueError):
                            # If selected organization not found, default to first one
                            selected_index = 0
                    
                    selected_org_name = st.selectbox(
                        "Organization",
                        options=org_names,
                        index=selected_index
                    )
                    
                    # Update selected organization
                    for org in organizations:
                        if org.name == selected_org_name:
                            st.session_state.selected_organization = org.id
                            break
                else:
                    st.warning("No organizations found")
                    # Clear selected organization if user has no organizations
                    if 'selected_organization' in st.session_state:
                        del st.session_state.selected_organization
        
        # Authentication status - Compact
        if st.session_state.user:
            # Check if it's demo mode
            if hasattr(st.session_state.user, 'email'):
                is_demo = getattr(st.session_state.user, 'email', '') == 'demo@example.com'
            else:
                is_demo = st.session_state.user.get('email', '') == 'demo@example.com'
            
            if is_demo:
                st.markdown('🎯 **DEMO MODE**')
            else:
                st.markdown('✅ **AUTHENTICATED**')
        
        st.markdown("---")
        
        # Navigation - Most important section
        selected = option_menu(
            menu_title="📋 Navigation",
            options=["Organizations Dashboard", "Dashboard", "Properties", "Income", "Expenses", "Analytics", "AI Insights"],
            icons=["building", "speedometer2", "house", "cash-coin", "receipt", "graph-up", "robot"],
            menu_icon="cast",
            default_index=0,
        )
        
        st.markdown("---")
        
        # Logout button - Compact
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()

    # Main content based on selected page
    if selected == "Organizations Dashboard":
        st.markdown('<h1 class="main-header">🏢 Organizations Dashboard</h1>', unsafe_allow_html=True)
        
        # Get user organizations
        if st.session_state.user:
            if hasattr(st.session_state.user, 'id'):
                user_id = st.session_state.user.id
            else:
                user_id = st.session_state.user.get('id', None)
            
            if user_id:
                db = DatabaseOperations()
                organizations = db.get_user_organizations(user_id)
                
                if organizations:
                    # Display organizations
                    st.markdown("### Your Organizations")
                    
                    for org in organizations:
                        with st.expander(f"🏢 {org.name}", expanded=True):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown(f"**Description:** {org.description or 'No description provided'}")
                                st.markdown(f"**Created:** {org.created_at.strftime('%Y-%m-%d') if org.created_at else 'Unknown'}")
                            
                            with col2:
                                # Get organization stats
                                properties = db.get_properties()
                                org_properties = [p for p in properties if p.organization_id == org.id]
                                
                                st.metric("Properties", len(org_properties))
                                
                                if org_properties:
                                    total_value = sum(p.purchase_price for p in org_properties)
                                    total_rent = sum(p.monthly_rent for p in org_properties)
                                    st.metric("Total Value", f"${total_value:,.2f}")
                                    st.metric("Monthly Rent", f"${total_rent:,.2f}")
                                    
                                    # Get financial data for P&L
                                    all_income = db.get_all_income()
                                    all_expenses = db.get_all_expenses()
                                    
                                    org_income = [inc for inc in all_income if inc.organization_id == org.id]
                                    org_expenses = [exp for exp in all_expenses if exp.organization_id == org.id]
                                    
                                    total_income = sum(inc.amount for inc in org_income)
                                    total_expenses = sum(exp.amount for exp in org_expenses)
                                    net_income = total_income - total_expenses
                                    profit_margin = (net_income / total_income * 100) if total_income > 0 else 0
                                    roi = (net_income / total_value * 100) if total_value > 0 else 0
                                    
                                    st.metric("Total Income", f"${total_income:,.2f}")
                                    st.metric("Total Expenses", f"${total_expenses:,.2f}")
                                    st.metric("Net Income", f"${net_income:,.2f}")
                                    st.metric("Profit Margin", f"{profit_margin:.1f}%")
                                    st.metric("ROI", f"{roi:.1f}%")
                            
                            # Add P&L Summary section
                            if org_properties and (org_income or org_expenses):
                                st.markdown("---")
                                st.markdown("### 📊 Profit & Loss Summary")
                                
                                col3, col4, col5 = st.columns(3)
                                
                                with col3:
                                    st.metric("💰 Total Income", f"${total_income:,.2f}")
                                with col4:
                                    st.metric("💸 Total Expenses", f"${total_expenses:,.2f}")
                                with col5:
                                    color = "normal" if net_income >= 0 else "inverse"
                                    st.metric("📈 Net Income", f"${net_income:,.2f}", delta=f"{profit_margin:.1f}% margin")
                    
                    # Add new organization button
                    if st.button("➕ Add New Organization", type="primary"):
                        st.session_state.show_add_org = True
                    
                    if st.session_state.get('show_add_org', False):
                        st.markdown("### Add New Organization")
                        with st.form("add_organization_form"):
                            org_name = st.text_input("Organization Name", placeholder="Enter organization name")
                            org_description = st.text_area("Description", placeholder="Enter organization description")
                            
                            submitted = st.form_submit_button("Create Organization", type="primary")
                            
                            if submitted and org_name:
                                new_org = Organization(
                                    name=org_name,
                                    description=org_description if org_description else None
                                )
                                
                                result = db.create_organization(new_org, user_id)
                                if result:
                                    st.success(f"Organization '{org_name}' created successfully!")
                                    st.session_state.show_add_org = False
                                    st.rerun()
                                else:
                                    st.error("Failed to create organization. Please try again.")
                else:
                    st.info("No organizations found. Create your first organization below.")
                    
                    # Create first organization
                    st.markdown("### Create Your First Organization")
                    with st.form("create_first_org_form"):
                        org_name = st.text_input("Organization Name", placeholder="Enter your organization name")
                        org_description = st.text_area("Description", placeholder="Enter organization description")
                        
                        submitted = st.form_submit_button("Create Organization", type="primary")
                        
                        if submitted and org_name:
                            new_org = Organization(
                                name=org_name,
                                description=org_description if org_description else None
                            )
                            
                            result = db.create_organization(new_org, user_id)
                            if result:
                                st.success(f"Organization '{org_name}' created successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to create organization. Please try again.")
            else:
                st.error("Unable to get user ID. Please log out and log back in.")
        else:
            st.error("Please log in to view organizations.")
    
    elif selected == "Dashboard":
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

    elif selected == "Properties":
        st.markdown('<h1 class="main-header">🏠 Property Management</h1>', unsafe_allow_html=True)
        
        # Check if demo mode
        is_demo_mode = False
        if st.session_state.user:
            if hasattr(st.session_state.user, 'email'):
                is_demo_mode = getattr(st.session_state.user, 'email', '') == 'demo@example.com'
            else:
                is_demo_mode = st.session_state.user.get('email', '') == 'demo@example.com'
        
        if is_demo_mode:
            st.info("🎯 Demo mode - showing sample properties. Sign up to manage your own properties!")
        else:
            # Get selected organization
            selected_org_id = st.session_state.get('selected_organization')
            if not selected_org_id:
                st.error("Please select an organization first.")
                return
            
            # Get organization name
            org = db.get_organization_by_id(selected_org_id)
            org_name = org.name if org else "Unknown Organization"
            
            st.info(f"Managing properties for: **{org_name}**")
            
            # Real property management with organization filtering
            # Tabs for property management
            tab1, tab2 = st.tabs(["View Properties", "Add/Edit Property"])
            
            with tab1:
                properties = db.get_properties()
                # Filter properties by organization
                org_properties = [p for p in properties if p.organization_id == selected_org_id]
                
                if org_properties:
                    for prop in org_properties:
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
                    st.info(f"No properties found for {org_name}. Add your first property below.")
            
            with tab2:
                st.subheader("Add New Property")
                
                # Use a key to reset form after successful submission
                form_key = f"add_property_form_{st.session_state.get('form_reset_counter', 0)}"
                
                with st.form(form_key):
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
                            
                            result = db.create_property(new_property, user_id, organization_id)
                            if result:
                                st.success(f"Property '{name}' added successfully!")
                                # Increment form reset counter to clear the form
                                st.session_state.form_reset_counter = st.session_state.get('form_reset_counter', 0) + 1
                                st.rerun()
                            else:
                                st.error("Failed to add property. Please try again.")
                        else:
                            st.error("Please fill in all required fields.")

    # Add other sections (Income, Expenses, Analytics, AI Insights) similar to original app.py
    # For brevity, I'll add a placeholder for now
    elif selected == "Income":
        st.markdown('<h1 class="main-header">💰 Income Tracking</h1>', unsafe_allow_html=True)
        
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
        
        # Tabs for income management
        tab1, tab2 = st.tabs(["View Income", "Add Income"])
        
        with tab1:
            
            if org_properties:
                # Filter by property
                property_names = {prop.id: prop.name for prop in org_properties}
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
    
    elif selected == "Expenses":
        st.markdown('<h1 class="main-header">💸 Expense Tracking</h1>', unsafe_allow_html=True)
        
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
        
        # Tabs for expense management
        tab1, tab2 = st.tabs(["View Expenses", "Add Expense"])
        
        with tab1:
            
            if org_properties:
                # Filter by property
                property_names = {prop.id: prop.name for prop in org_properties}
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
                    
                    df_expense = pd.DataFrame(expense_data)
                    st.dataframe(df_expense, use_container_width=True)
                    
                    # Expense summary
                    total_expenses = sum(exp.amount for exp in expense_records)
                    st.metric("Total Expenses", f"${total_expenses:,.2f}")
                else:
                    st.info("No expense records found.")
            else:
                st.info(f"No properties found for {org_name}. Please add a property first.")
        
        with tab2:
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
    
    elif selected == "Analytics":
        st.markdown('<h1 class="main-header">📊 Analytics & Reports</h1>', unsafe_allow_html=True)
        st.info("Analytics functionality - Sign up to use with your own data!")
    
    elif selected == "AI Insights":
        st.markdown('<h1 class="main-header">🤖 AI-Powered Insights</h1>', unsafe_allow_html=True)
        st.info("AI insights functionality - Sign up to use with your own data!")

def main():
    """Main application function"""
    initialize_session_state()
    
    if st.session_state.authenticated:
        show_main_app()
    else:
        show_auth_page()

if __name__ == "__main__":
    main()
