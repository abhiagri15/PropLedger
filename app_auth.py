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
from utils.session_manager import SessionManager
import config
import os
from dotenv import load_dotenv

# Import page modules
from modules import dashboard, properties, accounting, analytics, rent_reminders, reports, budgets, capex, vendors, ai_insights

# Load environment variables
load_dotenv()

# Ensure pandas is available globally
try:
    import pandas as pd
    # Make sure pandas is available in global scope
    globals()['pd'] = pd
except ImportError:
    st.error("Pandas is not installed. Please install it with: pip install pandas")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="PropLedger - Rental Property Management",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Set default navigation state
def set_default_navigation():
    """Set default navigation state to ensure proper page alignment"""
    # Initialize default navigation state if not set
    if 'default_navigation_set' not in st.session_state:
        st.session_state.default_navigation_set = True
        # Force the app to show the Dashboard by default
        st.session_state.force_dashboard = True
        # Set the selected navigation to Dashboard
        st.session_state.main_navigation = "Dashboard"

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

    /* Global compact font sizes for all metrics and numbers */
    [data-testid="stMetricValue"] {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;
        font-weight: 500 !important;
    }

    [data-testid="stMetricDelta"] {
        font-size: 0.7rem !important;
    }

    /* Reduce dataframe text size */
    .dataframe {
        font-size: 0.85rem !important;
    }

    /* Reduce heading sizes */
    h1 {
        font-size: 1.8rem !important;
    }

    h2 {
        font-size: 1.4rem !important;
    }

    h3 {
        font-size: 1.2rem !important;
    }

    /* Reduce chart title sizes */
    .plotly .gtitle {
        font-size: 0.9rem !important;
    }

    /* Auto-highlight Dashboard on page load */
    .stOptionMenu [data-testid="stOptionMenu"] [role="menuitem"]:nth-child(2) {
        background-color: #02ab21 !important;
        color: white !important;
    }
    
    /* Ensure Dashboard is always visible and highlighted */
    .stOptionMenu [data-testid="stOptionMenu"] [role="menuitem"]:nth-child(2):hover {
        background-color: #02ab21 !important;
        color: white !important;
    }
</style>

<script>
// Auto-click Dashboard on page load
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        // Find the Dashboard option (index 1) and click it
        const dashboardOption = document.querySelector('[data-testid="stOptionMenu"] [role="menuitem"]:nth-child(2)');
        if (dashboardOption && !dashboardOption.classList.contains('stOptionMenu-selected')) {
            dashboardOption.click();
        }
    }, 500);
});

// Also try to click Dashboard when the page is fully loaded
window.addEventListener('load', function() {
    setTimeout(function() {
        const dashboardOption = document.querySelector('[data-testid="stOptionMenu"] [role="menuitem"]:nth-child(2)');
        if (dashboardOption && !dashboardOption.classList.contains('stOptionMenu-selected')) {
            dashboardOption.click();
        }
    }, 1000);
});
</script>

""", unsafe_allow_html=True)


def show_auth_page():
    """Display authentication page"""

    # Initialize auth mode in session state
    if 'auth_mode' not in st.session_state:
        st.session_state.auth_mode = 'signin'  # 'signin' or 'signup'

    # Create a centered layout with narrower form
    left_spacer, main_col, right_spacer = st.columns([2, 1, 2])

    with main_col:
        # App branding
        st.markdown("""
            <div style="text-align: center; padding: 1rem 0 0.5rem 0;">
                <h1 style="color: #1f77b4; font-size: 1.8rem; margin-bottom: 0.2rem; font-weight: 700;">
                    🏠 PropLedger
                </h1>
                <p style="color: #888; font-size: 0.85rem; margin: 0;">
                    Rental Property Management System
                </p>
            </div>
        """, unsafe_allow_html=True)

        # Tab-like buttons for switching between Sign In and Sign Up
        col_signin, col_signup = st.columns(2)
        with col_signin:
            if st.button("Sign In", use_container_width=True, key="signin_button", type="primary" if st.session_state.auth_mode == 'signin' else "secondary"):
                st.session_state.auth_mode = 'signin'
                st.rerun()
        with col_signup:
            if st.button("Sign Up", use_container_width=True, key="signup_button", type="primary" if st.session_state.auth_mode == 'signup' else "secondary"):
                st.session_state.auth_mode = 'signup'
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # SIGN IN FORM
        if st.session_state.auth_mode == 'signin':
            st.markdown("""
                <div style="text-align: center; padding-bottom: 0.8rem;">
                    <h2 style="color: #333; font-size: 1.3rem; margin: 0; font-weight: 600;">
                        Welcome back
                    </h2>
                    <p style="color: #666; font-size: 0.85rem; margin-top: 0.2rem;">
                        Sign in to continue managing your portfolio
                    </p>
                </div>
            """, unsafe_allow_html=True)

            # Use a key to reset form after successful submission
            login_form_key = f"login_form_{st.session_state.get('login_form_reset_counter', 0)}"

            with st.form(login_form_key):
                email = st.text_input("Email Address", key=f"login_email_{st.session_state.get('login_form_reset_counter', 0)}", placeholder="name@example.com")
                password = st.text_input("Password", type="password", key=f"login_password_{st.session_state.get('login_form_reset_counter', 0)}", placeholder="Enter your password")

                st.markdown("<br>", unsafe_allow_html=True)
                login_submitted = st.form_submit_button("Sign in to your account", type="primary", use_container_width=True)

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
                            st.session_state.login_form_reset_counter = st.session_state.get('login_form_reset_counter', 0) + 1
                            st.rerun()
                        else:
                            st.error("❌ Invalid email or password")
                    except Exception as e:
                        st.error(f"❌ Login failed: {str(e)}")
                else:
                    st.error("❌ Please fill in all fields")

        # SIGN UP FORM
        else:
            st.markdown("""
                <div style="text-align: center; padding-bottom: 0.8rem;">
                    <h2 style="color: #333; font-size: 1.3rem; margin: 0; font-weight: 600;">
                        Create your account
                    </h2>
                    <p style="color: #666; font-size: 0.85rem; margin-top: 0.2rem;">
                        Get started with PropLedger today
                    </p>
                </div>
            """, unsafe_allow_html=True)

            # Use a key to reset form after successful submission
            signup_form_key = f"signup_form_{st.session_state.get('signup_form_reset_counter', 0)}"

            with st.form(signup_form_key):
                signup_email = st.text_input("Email Address", key=f"signup_email_{st.session_state.get('signup_form_reset_counter', 0)}", placeholder="name@example.com")
                signup_password = st.text_input("Password", type="password", key=f"signup_password_{st.session_state.get('signup_form_reset_counter', 0)}", placeholder="Create a password (min 6 characters)")
                confirm_password = st.text_input("Confirm Password", type="password", key=f"confirm_password_{st.session_state.get('signup_form_reset_counter', 0)}", placeholder="Confirm your password")
                signup_organization = st.text_input("Organization Name", key=f"signup_organization_{st.session_state.get('signup_form_reset_counter', 0)}", placeholder="Your company/organization name")

                st.markdown("<br>", unsafe_allow_html=True)
                signup_submitted = st.form_submit_button("Create free account", type="primary", use_container_width=True)

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

                                st.session_state.signup_form_reset_counter = st.session_state.get('signup_form_reset_counter', 0) + 1
                                st.rerun()
                            else:
                                st.error("❌ Failed to create account. Email might already be in use.")
                        except Exception as e:
                            st.error(f"❌ Sign up failed: {str(e)}")
                else:
                    st.error("❌ Please fill in all fields")

        # Demo access section
        st.markdown("<hr style='margin: 1rem 0;'>", unsafe_allow_html=True)
        st.markdown("""
            <div style="text-align: center; padding: 0.5rem 0;">
                <p style="color: #666; font-size: 0.85rem;">
                    🎯 <strong>Want to try without signing up?</strong>
                </p>
                <p style="color: #888; font-size: 0.75rem; margin-top: 0.2rem;">
                    Explore all features with our interactive demo
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 Try Demo Version", use_container_width=True):
            st.session_state.authenticated = True
            st.session_state.user = {"email": "demo@example.com", "user_metadata": {"full_name": "Demo User"}}
            st.rerun()


def show_auth_page_old():
    """Display authentication page - OLD VERSION"""
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
                            # Session is automatically stored in Supabase
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
                                            st.session_state.selected_org_id = org_id
                                            st.session_state.selected_org_name = signup_organization
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

        st.markdown("---")

        # Navigation - Most important section at top
        # Force Dashboard selection on first load
        if st.session_state.get('force_dashboard', False):
            st.session_state.force_dashboard = False
            # Force rerun to ensure Dashboard is selected
            st.rerun()

        # Ensure Dashboard is always selected on first load
        if 'main_navigation' not in st.session_state:
            st.session_state.main_navigation = "Dashboard"

        selected = option_menu(
            menu_title=None,  # Remove Navigation header
            options=["My Org", "Dashboard", "Properties", "Accounting", "Analytics", "Rent Reminders", "Reports", "📊 Budgets", "🏗️ CapEx", "👥 Vendors", "AI Insights"],
            icons=["building", "speedometer2", "house", "wallet2", "graph-up", "bell", "file-earmark-text", "calculator", "tools", "people", "robot"],
            menu_icon="cast",
            default_index=1,  # Dashboard is default
            key="main_navigation",
            styles={
                "container": {"padding": "0!important", "background-color": "#f8f9fa"},
                "icon": {"color": "#6c757d", "font-size": "20px"},
                "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px", "--hover-color": "#e9ecef", "color": "#495057"},
                "nav-link-selected": {"background-color": "#d4edda", "color": "#155724"},
            }
        )

        st.markdown("---")

        # User info and organization at bottom
        if SessionManager.get_user():
            # Get user info using session manager
            user_email = SessionManager.get_user_email() or 'Unknown'
            user_id = SessionManager.get_user_id()

            # Get user name from metadata
            user = SessionManager.get_user()
            if user:
                if hasattr(user, 'user_metadata'):
                    user_metadata = getattr(user, 'user_metadata', {})
                    user_name = user_metadata.get('full_name', user_email) if isinstance(user_metadata, dict) else user_email
                elif isinstance(user, dict):
                    user_name = user.get('user_metadata', {}).get('full_name', user_email)
                else:
                    user_name = user_email
            else:
                user_name = user_email

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
                        index=selected_index,
                        label_visibility="collapsed"
                    )

                    # Update selected organization
                    for org in organizations:
                        if org.name == selected_org_name:
                            st.session_state.selected_organization = org.id
                            break
                else:
                    st.info("No organizations")
                    # Clear selected organization if user has no organizations
                    if 'selected_organization' in st.session_state:
                        del st.session_state.selected_organization

            # User info at bottom
            st.markdown(f"👤 {user_name}")

            # Authentication status - Compact
            if SessionManager.is_demo_mode():
                st.caption('🎯 Demo Mode')

        # Logout button - Compact at very bottom
        if st.button("🚪 Logout", use_container_width=True):
            SessionManager.sign_out()

    # Main content based on selected page
    if selected == "My Org" or selected == "Organizations Dashboard":
        # My Org page (renamed from Organizations Dashboard)
        
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
        dashboard.render_dashboard()

    elif selected == "Properties":
        properties.render_properties()

    elif selected == "Accounting" or selected == "Income" or selected == "Expenses":
        # Unified Accounting page with Income and Expenses tabs
        accounting.render_accounting()

    elif selected == "Analytics":
        analytics.render_analytics()

    elif selected == "Rent Reminders":
        rent_reminders.render_rent_reminders()

    elif selected == "Reports":
        reports.render_reports()

    elif selected == "📊 Budgets":
        budgets.render_budgets()

    elif selected == "🏗️ CapEx":
        capex.render_capex()

    elif selected == "👥 Vendors":
        vendors.render_vendors()

    elif selected == "AI Insights":
        ai_insights.render_ai_insights()


def main():
    """Main application function"""
    # Set default navigation state
    set_default_navigation()

    # Initialize auth mode BEFORE anything else to ensure Sign In is default
    if 'auth_mode' not in st.session_state:
        st.session_state.auth_mode = 'signin'

    # Initialize session management
    SessionManager.initialize_session()

    if SessionManager.is_authenticated():
        show_main_app()
    else:
        show_auth_page()

if __name__ == "__main__":
    main()
