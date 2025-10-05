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
from services.geocoding import geocoding_service
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
    }
    .address-suggestion {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.375rem;
        padding: 0.5rem;
        margin: 0.25rem 0;
        transition: all 0.2s ease;
    }
    .address-suggestion:hover {
        background-color: #e9ecef;
        border-color: #1f77b4;
    }
    .map-link {
        color: #1f77b4;
        text-decoration: none;
        font-size: 0.875rem;
    }
    .map-link:hover {
        text-decoration: underline;
    }
    .location-preview {
        background-color: #e7f3ff;
        border: 1px solid #b3d9ff;
        border-radius: 0.375rem;
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
            options=["Organizations Dashboard", "Dashboard", "Properties", "Income", "Expenses", "Analytics", "Rent Reminders", "Reports", "AI Insights"],
            icons=["building", "speedometer2", "house", "cash-coin", "receipt", "graph-up", "bell", "file-earmark-text", "robot"],
            menu_icon="cast",
            default_index=1,
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
        
        # Check if demo mode
        is_demo_mode = False
        if st.session_state.user:
            if hasattr(st.session_state.user, 'email'):
                is_demo_mode = getattr(st.session_state.user, 'email', '') == 'demo@example.com'
            else:
                is_demo_mode = st.session_state.user.get('email', '') == 'demo@example.com'
        
        if is_demo_mode:
            # Demo mode - show sample organizations
            st.markdown('<div class="info-box">🎯 <strong>Demo Mode</strong> - Showing sample organizations. Sign up to manage your own organizations!</div>', unsafe_allow_html=True)
            
            # Sample organizations for demo
            demo_organizations = [
                {
                    'name': 'Demo Property Group',
                    'description': 'Sample property management company',
                    'created_at': '2024-01-15',
                    'properties': 3,
                    'total_value': 750000,
                    'monthly_rent': 4500,
                    'total_income': 54000,
                    'total_expenses': 24000,
                    'net_income': 30000
                },
                {
                    'name': 'Sample Real Estate LLC',
                    'description': 'Demo real estate investment company',
                    'created_at': '2024-02-20',
                    'properties': 2,
                    'total_value': 500000,
                    'monthly_rent': 3200,
                    'total_income': 38400,
                    'total_expenses': 18000,
                    'net_income': 20400
                }
            ]
            
            st.markdown("### Sample Organizations")
            
            for org in demo_organizations:
                with st.expander(f"🏢 {org['name']}", expanded=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Description:** {org['description']}")
                        st.markdown(f"**Created:** {org['created_at']}")
                    
                    with col2:
                        st.metric("Properties", org['properties'])
                        st.metric("Total Value", f"${org['total_value']:,.2f}")
                        st.metric("Monthly Rent", f"${org['monthly_rent']:,.2f}")
                        
                        # P&L Summary
                        st.markdown("**Financial Summary:**")
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Total Income", f"${org['total_income']:,.2f}")
                        with col_b:
                            st.metric("Total Expenses", f"${org['total_expenses']:,.2f}")
                        with col_c:
                            st.metric("Net Income", f"${org['net_income']:,.2f}")
                        
                        # Profit margin
                        profit_margin = (org['net_income'] / org['total_income'] * 100) if org['total_income'] > 0 else 0
                        st.metric("Profit Margin", f"{profit_margin:.1f}%")
            
            # Demo organization creation
            st.markdown("---")
            st.markdown("### Create New Organization (Demo)")
            
            with st.form("demo_org_form_1"):
                col1, col2 = st.columns(2)
                
                with col1:
                    demo_org_name_1 = st.text_input("Organization Name", value="My Demo Company", key="demo_org_name_1")
                    demo_org_desc_1 = st.text_area("Description", value="A sample organization for demonstration", key="demo_org_desc_1")
                
                with col2:
                    st.info("**Demo Note:** This is a demonstration. In the real app, this would create an actual organization in your database.")
                
                if st.form_submit_button("Create Demo Organization", type="primary"):
                    st.success(f"Demo organization '{demo_org_name_1}' would be created!")
                    st.info("Sign up to create real organizations and manage your properties!")
        
        else:
            # Real mode - show message for now
            st.info("Real organization management - Sign up to use with your own data!")
        
        if is_demo_mode:
            # Demo mode - show sample organizations
            st.markdown('<div class="info-box">🎯 <strong>Demo Mode</strong> - Showing sample organizations. Sign up to manage your own organizations!</div>', unsafe_allow_html=True)
            
            # Sample organizations for demo
            demo_organizations = [
                {
                    'name': 'Demo Property Group',
                    'description': 'Sample property management company',
                    'created_at': '2024-01-15',
                    'properties': 3,
                    'total_value': 750000,
                    'monthly_rent': 4500,
                    'total_income': 54000,
                    'total_expenses': 24000,
                    'net_income': 30000
                },
                {
                    'name': 'Sample Real Estate LLC',
                    'description': 'Demo real estate investment company',
                    'created_at': '2024-02-20',
                    'properties': 2,
                    'total_value': 500000,
                    'monthly_rent': 3200,
                    'total_income': 38400,
                    'total_expenses': 18000,
                    'net_income': 20400
                }
            ]
            
            st.markdown("### Sample Organizations")
            
            for org in demo_organizations:
                with st.expander(f"🏢 {org['name']}", expanded=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Description:** {org['description']}")
                        st.markdown(f"**Created:** {org['created_at']}")
                    
                    with col2:
                        st.metric("Properties", org['properties'])
                        st.metric("Total Value", f"${org['total_value']:,.2f}")
                        st.metric("Monthly Rent", f"${org['monthly_rent']:,.2f}")
                        
                        # P&L Summary
                        st.markdown("**Financial Summary:**")
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Total Income", f"${org['total_income']:,.2f}")
                        with col_b:
                            st.metric("Total Expenses", f"${org['total_expenses']:,.2f}")
                        with col_c:
                            st.metric("Net Income", f"${org['net_income']:,.2f}")
                        
                        # Profit margin
                        profit_margin = (org['net_income'] / org['total_income'] * 100) if org['total_income'] > 0 else 0
                        st.metric("Profit Margin", f"{profit_margin:.1f}%")
            
            # Demo organization creation
            st.markdown("---")
            st.markdown("### Create New Organization (Demo)")
            
            with st.form("demo_org_form_1"):
                col1, col2 = st.columns(2)
                
                with col1:
                    demo_org_name_1 = st.text_input("Organization Name", value="My Demo Company", key="demo_org_name_1")
                    demo_org_desc_1 = st.text_area("Description", value="A sample organization for demonstration", key="demo_org_desc_1")
                
                with col2:
                    st.info("**Demo Note:** This is a demonstration. In the real app, this would create an actual organization in your database.")
                
                if st.form_submit_button("Create Demo Organization", type="primary"):
                    st.success(f"Demo organization '{demo_org_name_1}' would be created!")
                    st.info("Sign up to create real organizations and manage your properties!")
        
        else:
            # Real mode - get user organizations
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
                
                # Address input section (outside form for suggestions)
                st.markdown("### Property Details")
                
                # Address search input
                address_search_key = f"address_search_{st.session_state.get('form_reset_counter', 0)}"
                address_search = st.text_input(
                    "Search Address *", 
                    placeholder="Start typing address... (e.g., 123 Main St, New York)",
                    key=address_search_key
                )
                
                # Address suggestions using selectbox
                selected_address = None
                if address_search and len(address_search.strip()) >= 3:
                    try:
                        suggestions = geocoding_service.search_addresses(address_search.strip(), limit=10)
                        
                        if suggestions:
                            st.markdown("**Select Address:**")
                            suggestion_options = [f"📍 {s['address']}" for s in suggestions]
                            suggestion_index = st.selectbox(
                                "Choose from suggestions:",
                                options=range(len(suggestion_options)),
                                format_func=lambda x: suggestion_options[x] if x < len(suggestion_options) else "",
                                key=f"address_select_{st.session_state.get('form_reset_counter', 0)}"
                            )
                            
                            if suggestion_index is not None and suggestion_index < len(suggestions):
                                selected_suggestion = suggestions[suggestion_index]
                                selected_address = selected_suggestion['address']
                                
                                # Show map link for selected address
                                if selected_suggestion.get('lat') and selected_suggestion.get('lon'):
                                    map_url = f"https://www.google.com/maps?q={selected_suggestion['lat']},{selected_suggestion['lon']}"
                                    st.markdown(f'<a href="{map_url}" class="map-link" target="_blank">🗺️ View on Map</a>', unsafe_allow_html=True)
                        else:
                            st.info("No address suggestions found. You can enter manually below.")
                    except Exception as e:
                        st.warning(f"Address lookup temporarily unavailable: {str(e)}")
                
                # Manual address input
                st.markdown("**Or enter address manually:**")
                address_input_key = f"address_input_{st.session_state.get('form_reset_counter', 0)}"
                manual_address = st.text_input(
                    "Address *", 
                    value=selected_address if selected_address else "",
                    placeholder="Enter complete address manually",
                    key=address_input_key
                )
                
                # Use selected address or manual address
                final_address = selected_address if selected_address else manual_address
                
                # Show map preview for final address
                if final_address and len(final_address.strip()) >= 10:
                    try:
                        address_details = geocoding_service.get_address_details(final_address.strip())
                        if address_details:
                            st.markdown("**📍 Location Preview:**")
                            st.markdown(f'<div class="location-preview">', unsafe_allow_html=True)
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.info(f"Coordinates: {address_details['lat']:.6f}, {address_details['lon']:.6f}")
                            with col2:
                                st.markdown(f'<a href="{address_details["map_url"]}" class="map-link" target="_blank">🗺️ View on Map</a>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                    except Exception as e:
                        pass  # Silently fail for map preview
                
                st.markdown("---")
                
                # Use a key to reset form after successful submission
                form_key = f"add_property_form_{st.session_state.get('form_reset_counter', 0)}"
                
                with st.form(form_key):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        name = st.text_input("Property Name *", placeholder="e.g., Downtown Apartment")
                        property_type = st.selectbox("Property Type *", [pt.value for pt in PropertyType])
                        purchase_price = st.number_input("Purchase Price *", min_value=0.0, format="%.2f")
                    
                    with col2:
                        purchase_date = st.date_input("Purchase Date *", value=date.today())
                        monthly_rent = st.number_input("Monthly Rent *", min_value=0.0, format="%.2f")
                        description = st.text_area("Description", placeholder="Additional details about the property")
                    
                    submitted = st.form_submit_button("Add Property", type="primary")
                    
                    if submitted:
                        # Get address from final_address (selected or manual)
                        if name and final_address and purchase_price and monthly_rent:
                            new_property = Property(
                                name=name,
                                address=final_address,
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
        
        else:
            # Real analytics with user data
            # Get all data for the organization
            properties = db.get_properties()
            org_properties = [p for p in properties if p.organization_id == selected_org_id]
            
            if not org_properties:
                st.info(f"No properties found for {org_name}. Add properties to see analytics.")
                return
            
            # Get financial data
            all_income = db.get_all_income()
            all_expenses = db.get_all_expenses()
            
            # Filter by organization
            org_income = [inc for inc in all_income if inc.organization_id == selected_org_id]
            org_expenses = [exp for exp in all_expenses if exp.organization_id == selected_org_id]
            
            # Date range filter
            st.subheader("📅 Date Range Filter")
            col1, col2 = st.columns(2)
            
            with col1:
                start_date = st.date_input("Start Date", value=date.today() - timedelta(days=365))
            with col2:
                end_date = st.date_input("End Date", value=date.today())
            
            # Filter data by date range
            filtered_income = [inc for inc in org_income if start_date <= inc.transaction_date.date() <= end_date]
            filtered_expenses = [exp for exp in org_expenses if start_date <= exp.transaction_date.date() <= end_date]
            
            # Financial Overview
            st.subheader("💰 Financial Overview")
            
            total_income = sum(inc.amount for inc in filtered_income)
            total_expenses = sum(exp.amount for exp in filtered_expenses)
            net_income = total_income - total_expenses
            profit_margin = (net_income / total_income * 100) if total_income > 0 else 0
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Properties", len(org_properties))
            with col2:
                st.metric("Total Income", f"${total_income:,.2f}")
            with col3:
                st.metric("Total Expenses", f"${total_expenses:,.2f}")
            with col4:
                st.metric("Net Income", f"${net_income:,.2f}", f"{profit_margin:.1f}%")
            
            st.markdown("---")
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Income Trend")
                if filtered_income:
                    # Group income by month
                    income_by_month = {}
                    for inc in filtered_income:
                        month_key = inc.transaction_date.strftime('%Y-%m')
                        if month_key not in income_by_month:
                            income_by_month[month_key] = 0
                        income_by_month[month_key] += inc.amount
                    
                    months = sorted(income_by_month.keys())
                    amounts = [income_by_month[month] for month in months]
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=months, y=amounts, mode='lines+markers', 
                                           name='Income', line=dict(color='#2E8B57')))
                    fig.update_layout(title="Monthly Income Trend", xaxis_title="Month", yaxis_title="Income ($)")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No income data for selected period")
            
            with col2:
                st.subheader("🏠 Property Performance")
                if org_properties and filtered_income:
                    property_income = {}
                    property_expenses = {}
                    
                    # Calculate income per property
                    for inc in filtered_income:
                        prop_id = inc.property_id
                        if prop_id not in property_income:
                            property_income[prop_id] = 0
                        property_income[prop_id] += inc.amount
                    
                    # Calculate expenses per property
                    for exp in filtered_expenses:
                        prop_id = exp.property_id
                        if prop_id not in property_expenses:
                            property_expenses[prop_id] = 0
                        property_expenses[prop_id] += exp.amount
                    
                    # Get property names
                    prop_names = []
                    prop_income = []
                    prop_expenses = []
                    
                    for prop in org_properties:
                        prop_names.append(prop.name)
                        prop_income.append(property_income.get(prop.id, 0))
                        prop_expenses.append(property_expenses.get(prop.id, 0))
                    
                    fig = go.Figure()
                    fig.add_trace(go.Bar(name='Income', x=prop_names, y=prop_income, marker_color='#2E8B57'))
                    fig.add_trace(go.Bar(name='Expenses', x=prop_names, y=prop_expenses, marker_color='#DC143C'))
                    fig.update_layout(title="Property Income vs Expenses", barmode='group')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No property performance data available")
            
            # Expense Analysis
            if filtered_expenses:
                st.subheader("💰 Expense Analysis")
                col1, col2 = st.columns(2)
                
                with col1:
                    # Expense categories
                    expense_categories = {}
                    for exp in filtered_expenses:
                        category = exp.expense_type
                        if category not in expense_categories:
                            expense_categories[category] = 0
                        expense_categories[category] += exp.amount
                    
                    if expense_categories:
                        categories = list(expense_categories.keys())
                        amounts = list(expense_categories.values())
                        
                        fig = go.Figure(data=[go.Pie(labels=categories, values=amounts, hole=0.3)])
                        fig.update_layout(title="Expense Categories")
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Monthly expense trend
                    expense_by_month = {}
                    for exp in filtered_expenses:
                        month_key = exp.transaction_date.strftime('%Y-%m')
                        if month_key not in expense_by_month:
                            expense_by_month[month_key] = 0
                        expense_by_month[month_key] += exp.amount
                    
                    months = sorted(expense_by_month.keys())
                    amounts = [expense_by_month[month] for month in months]
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=months, y=amounts, mode='lines+markers', 
                                           name='Expenses', line=dict(color='#DC143C')))
                    fig.update_layout(title="Monthly Expense Trend", xaxis_title="Month", yaxis_title="Expenses ($)")
                    st.plotly_chart(fig, use_container_width=True)
            
            # ROI Analysis
            st.subheader("📊 ROI Analysis")
            if org_properties:
                roi_data = []
                for prop in org_properties:
                    prop_income = sum(inc.amount for inc in filtered_income if inc.property_id == prop.id)
                    prop_expenses = sum(exp.amount for exp in filtered_expenses if exp.property_id == prop.id)
                    net_profit = prop_income - prop_expenses
                    roi = (net_profit / prop.purchase_price * 100) if prop.purchase_price > 0 else 0
                    
                    roi_data.append({
                        'Property': prop.name,
                        'Purchase Price': prop.purchase_price,
                        'Net Profit': net_profit,
                        'ROI %': roi
                    })
                
                if roi_data:
                    roi_df = pd.DataFrame(roi_data)
                    st.dataframe(roi_df, use_container_width=True)
                    
                    # ROI chart
                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=roi_df['Property'], y=roi_df['ROI %'], 
                                       marker_color='#4169E1'))
                    fig.update_layout(title="Property ROI Comparison", xaxis_title="Property", yaxis_title="ROI %")
                    st.plotly_chart(fig, use_container_width=True)
    
    elif selected == "Rent Reminders":
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
                    created_count = reminder_service.create_monthly_reminders(
                        selected_org_id, st.session_state.user_id
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

    elif selected == "Reports":
        st.markdown('<h1 class="main-header">📊 Reports</h1>', unsafe_allow_html=True)
        
        # Check if demo mode
        is_demo_mode = False
        if st.session_state.user:
            if hasattr(st.session_state.user, 'email'):
                user_email = st.session_state.user.email
            else:
                user_email = st.session_state.user.get('email', 'Unknown')
            
            if user_email == 'demo@example.com':
                is_demo_mode = True
        
        if is_demo_mode:
            st.info("📊 **Demo Mode**: Showing sample reports with sample data")
            
            # Demo P&L Report
            st.markdown("### 📈 Profit & Loss Report (Demo)")
            
            # Demo report type selection
            col1, col2 = st.columns(2)
            with col1:
                demo_report_type = st.selectbox("Report Type", ["Yearly", "Monthly", "Custom"], key="demo_report_type")
            
            with col2:
                if demo_report_type == "Yearly":
                    demo_year = st.selectbox("Select Year", 
                                           options=[2023, 2024, 2025], 
                                           index=1,  # Default to 2024
                                           key="demo_year_selector")
                elif demo_report_type == "Monthly":
                    current_year = date.today().year
                    demo_month_options = [
                        f"January {current_year}", f"February {current_year}", f"March {current_year}",
                        f"April {current_year}", f"May {current_year}", f"June {current_year}",
                        f"July {current_year}", f"August {current_year}", f"September {current_year}",
                        f"October {current_year}", f"November {current_year}", f"December {current_year}"
                    ]
                    demo_selected_month = st.selectbox("Select Month", 
                                                     options=demo_month_options,
                                                     index=date.today().month - 1,
                                                     key="demo_month_selector")
                else:  # Custom
                    col_start, col_end = st.columns(2)
                    with col_start:
                        demo_start_date = st.date_input("Start Date", value=date(2024, 1, 1), key="demo_custom_start")
                    with col_end:
                        demo_end_date = st.date_input("End Date", value=date(2024, 6, 30), key="demo_custom_end")
            
            # Demo data
            demo_data = {
                'Month': ['Jan 2024', 'Feb 2024', 'Mar 2024', 'Apr 2024', 'May 2024', 'Jun 2024'],
                'Revenue': [2500, 2500, 2500, 2500, 2500, 2500],
                'Expenses': [1800, 1900, 1750, 2000, 1850, 1950],
                'Net Income': [700, 600, 750, 500, 650, 550]
            }
            
            # Create demo P&L chart
            from plotly.subplots import make_subplots
            
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Monthly Revenue vs Expenses', 'Monthly Net Income'),
                vertical_spacing=0.1
            )
            
            # Revenue and Expenses
            fig.add_trace(go.Bar(name='Revenue', x=demo_data['Month'], y=demo_data['Revenue'], 
                               marker_color='#2E8B57'), row=1, col=1)
            fig.add_trace(go.Bar(name='Expenses', x=demo_data['Month'], y=demo_data['Expenses'], 
                               marker_color='#DC143C'), row=1, col=1)
            
            # Net Income
            fig.add_trace(go.Bar(name='Net Income', x=demo_data['Month'], y=demo_data['Net Income'], 
                               marker_color='#4169E1'), row=2, col=1)
            
            fig.update_layout(height=600, showlegend=True, title_text="Demo P&L Report")
            st.plotly_chart(fig, use_container_width=True)
            
            # Demo summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Revenue", "$15,000", "5.2%")
            with col2:
                st.metric("Total Expenses", "$11,250", "3.1%")
            with col3:
                st.metric("Net Profit", "$3,750", "8.3%")
        
        else:
            # Real P&L Report
            st.markdown("### 📈 Profit & Loss Report")
            
            # Get selected organization
            if 'selected_organization' in st.session_state and st.session_state.selected_organization:
                selected_org_id = st.session_state.selected_organization
                org_name = st.session_state.get('selected_org_name', 'Unknown Organization')
                
                # Date range selection
                col1, col2 = st.columns(2)
                with col1:
                    report_type = st.selectbox("Report Type", ["Yearly", "Monthly", "Custom"], key="report_type")
                
                with col2:
                    if report_type == "Yearly":
                        selected_year = st.selectbox("Select Year", 
                                                   options=list(range(2020, date.today().year + 2)), 
                                                   index=date.today().year - 2020,
                                                   key="year_selector")
                        start_date = date(selected_year, 1, 1)
                        end_date = date(selected_year + 1, 1, 1)
                    elif report_type == "Monthly":
                        # Show months of current year
                        current_year = date.today().year
                        month_options = [
                            f"January {current_year}", f"February {current_year}", f"March {current_year}",
                            f"April {current_year}", f"May {current_year}", f"June {current_year}",
                            f"July {current_year}", f"August {current_year}", f"September {current_year}",
                            f"October {current_year}", f"November {current_year}", f"December {current_year}"
                        ]
                        selected_month = st.selectbox("Select Month", 
                                                    options=month_options,
                                                    index=date.today().month - 1,
                                                    key="month_selector")
                        # Extract month number from selection
                        month_number = month_options.index(selected_month) + 1
                        start_date = date(current_year, month_number, 1)
                        if month_number == 12:
                            end_date = date(current_year + 1, 1, 1)
                        else:
                            end_date = date(current_year, month_number + 1, 1)
                    else:  # Custom
                        col_start, col_end = st.columns(2)
                        with col_start:
                            start_date = st.date_input("Start Date", value=date.today().replace(day=1), key="custom_start")
                        with col_end:
                            end_date = st.date_input("End Date", value=date.today(), key="custom_end")
                
                # Generate P&L Report
                if st.button("Generate P&L Report", key="generate_pl"):
                    try:
                        # Get income data
                        income_result = db.supabase.table("income").select("*").eq(
                            "organization_id", selected_org_id
                        ).gte("transaction_date", start_date.isoformat()).lt(
                            "transaction_date", end_date.isoformat()
                        ).execute()
                        
                        # Get expense data
                        expense_result = db.supabase.table("expenses").select("*").eq(
                            "organization_id", selected_org_id
                        ).gte("transaction_date", start_date.isoformat()).lt(
                            "transaction_date", end_date.isoformat()
                        ).execute()
                        
                        if income_result.data or expense_result.data:
                            # Calculate totals
                            total_income = sum(float(item.get('amount', 0)) for item in income_result.data)
                            total_expenses = sum(float(item.get('amount', 0)) for item in expense_result.data)
                            net_profit = total_income - total_expenses
                            
                            # Display summary metrics
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Revenue", f"${total_income:,.2f}")
                            with col2:
                                st.metric("Total Expenses", f"${total_expenses:,.2f}")
                            with col3:
                                profit_color = "normal" if net_profit >= 0 else "inverse"
                                st.metric("Net Profit", f"${net_profit:,.2f}", delta_color=profit_color)
                            
                            # Create detailed breakdown
                            st.markdown("#### 📊 Revenue Breakdown")
                            if income_result.data:
                                income_df = pd.DataFrame(income_result.data)
                                income_summary = income_df.groupby('income_type')['amount'].sum().reset_index()
                                income_summary['amount'] = income_summary['amount'].astype(float)
                                
                                fig_income = go.Figure(data=[go.Pie(labels=income_summary['income_type'], 
                                                                  values=income_summary['amount'],
                                                                  hole=0.3)])
                                fig_income.update_layout(title="Revenue by Type")
                                st.plotly_chart(fig_income, use_container_width=True)
                            else:
                                st.info("No revenue data found for the selected period.")
                            
                            st.markdown("#### 💰 Expense Breakdown")
                            if expense_result.data:
                                expense_df = pd.DataFrame(expense_result.data)
                                expense_summary = expense_df.groupby('expense_type')['amount'].sum().reset_index()
                                expense_summary['amount'] = expense_summary['amount'].astype(float)
                                
                                fig_expense = go.Figure(data=[go.Pie(labels=expense_summary['expense_type'], 
                                                                   values=expense_summary['amount'],
                                                                   hole=0.3)])
                                fig_expense.update_layout(title="Expenses by Type")
                                st.plotly_chart(fig_expense, use_container_width=True)
                            else:
                                st.info("No expense data found for the selected period.")
                            
                            # Monthly trend if yearly report
                            if report_type == "Yearly" and (income_result.data or expense_result.data):
                                st.markdown("#### 📈 Monthly Trend")
                                
                                # Process monthly data
                                monthly_data = {}
                                for item in income_result.data:
                                    month = item['transaction_date'][:7]  # YYYY-MM
                                    if month not in monthly_data:
                                        monthly_data[month] = {'income': 0, 'expenses': 0}
                                    monthly_data[month]['income'] += float(item.get('amount', 0))
                                
                                for item in expense_result.data:
                                    month = item['transaction_date'][:7]  # YYYY-MM
                                    if month not in monthly_data:
                                        monthly_data[month] = {'income': 0, 'expenses': 0}
                                    monthly_data[month]['expenses'] += float(item.get('amount', 0))
                                
                                if monthly_data:
                                    months = sorted(monthly_data.keys())
                                    income_values = [monthly_data[month]['income'] for month in months]
                                    expense_values = [monthly_data[month]['expenses'] for month in months]
                                    profit_values = [income_values[i] - expense_values[i] for i in range(len(months))]
                                    
                                    fig_trend = go.Figure()
                                    fig_trend.add_trace(go.Scatter(x=months, y=income_values, mode='lines+markers', 
                                                                 name='Revenue', line=dict(color='#2E8B57')))
                                    fig_trend.add_trace(go.Scatter(x=months, y=expense_values, mode='lines+markers', 
                                                                 name='Expenses', line=dict(color='#DC143C')))
                                    fig_trend.add_trace(go.Scatter(x=months, y=profit_values, mode='lines+markers', 
                                                                 name='Net Profit', line=dict(color='#4169E1')))
                                    
                                    fig_trend.update_layout(title="Monthly P&L Trend", 
                                                          xaxis_title="Month", yaxis_title="Amount ($)")
                                    st.plotly_chart(fig_trend, use_container_width=True)
                        else:
                            st.info("No financial data found for the selected period.")
                            
                    except Exception as e:
                        st.error(f"Error generating P&L report: {str(e)}")
            else:
                st.warning("Please select an organization first to view reports.")

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
