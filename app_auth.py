import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import pytz
from streamlit_option_menu import option_menu
from database.supabase_client import get_supabase_client
from database.database_operations import DatabaseOperations
from database.models import Property, Income, Expense, PropertyType, IncomeType, ExpenseType, Organization, UserOrganization, Budget, BudgetLine, BudgetPeriod, BudgetScope
from llm.llm_insights import LLMInsights
from services.geocoding import geocoding_service
import config
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
    /* Global font and spacing improvements */
    .stApp {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Compact sidebar styling */
    .css-1d391kg {
        padding-top: 0.8rem;
        min-width: 250px !important;
        width: 250px !important;
    }
    .css-1cypcdb {
        padding-top: 0.3rem;
    }
    .css-1d391kg .stMarkdown {
        margin-bottom: 0.3rem;
    }
    .css-1d391kg .stSelectbox {
        margin-bottom: 0.3rem;
        width: 100% !important;
    }
    .css-1d391kg .stButton {
        margin-top: 0.3rem;
    }
    
    /* Ensure sidebar has enough width for organization names */
    .css-1d391kg {
        min-width: 300px !important;
        width: 300px !important;
        max-width: 300px !important;
    }
    
    /* Force sidebar width */
    .stSidebar {
        min-width: 300px !important;
        width: 300px !important;
    }
    
    /* Override Streamlit's default sidebar width */
    .css-1d391kg {
        min-width: 300px !important;
        width: 300px !important;
        max-width: 300px !important;
    }
    
    /* Improved main headers */
    .main-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.6rem;
        letter-spacing: -0.3px;
    }
    
    /* Specific header sizing for different levels */
    h1.main-header {
        font-size: 1.8rem !important;
        margin-bottom: 0.8rem !important;
    }
    
    h2.main-header {
        font-size: 1.3rem !important;
        margin-bottom: 0.6rem !important;
    }
    
    h3.main-header {
        font-size: 1.1rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Section headers */
    h1 {
        font-size: 1.8rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.6rem !important;
    }
    
    h2 {
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
    }
    
    h3 {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.4rem !important;
    }
    
    /* Streamlit specific header overrides */
    .stMarkdown h1 {
        font-size: 1.8rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.6rem !important;
    }
    
    .stMarkdown h2 {
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
    }
    
    .stMarkdown h3 {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.4rem !important;
    }
    
    /* Tighten rows and align buttons for pending items */
    .pending-actions .stButton>button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.15s ease-in-out;
        padding: 0.45rem 0.6rem;
    }
    .pending-actions .stButton:nth-child(1) > button { /* Edit */
        background: #fffaf0;
        color: #B45309;
        border: 1px solid #FBBF24;
    }
    .pending-actions .stButton:nth-child(1) > button:hover {
        background: #FEF3C7;
        border-color: #F59E0B;
    }
    .pending-actions .stButton:nth-child(2) > button { /* Delete */
        background: #FEF2F2;
        color: #B91C1C;
        border: 1px solid #FCA5A5;
    }
    .pending-actions .stButton:nth-child(2) > button:hover {
        background: #FEE2E2;
        border-color: #EF4444;
    }
    .pending-actions .stButton:nth-child(3) > button { /* Confirm */
        background: #ECFDF5;
        color: #065F46;
        border: 1px solid #6EE7B7;
    }
    .pending-actions .stButton:nth-child(3) > button:hover {
        background: #D1FAE5;
        border-color: #34D399;
    }

    /* Polished action buttons for pending items */
    .pending-actions .stButton>button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.15s ease-in-out;
        padding: 0.5rem 0.75rem;
    }
    .pending-actions .stButton:nth-child(1) > button { /* Edit */
        background: #fffaf0;
        color: #B45309;
        border: 1px solid #FBBF24;
    }
    .pending-actions .stButton:nth-child(1) > button:hover {
        background: #FEF3C7;
        border-color: #F59E0B;
    }
    .pending-actions .stButton:nth-child(2) > button { /* Delete */
        background: #FEF2F2;
        color: #B91C1C;
        border: 1px solid #FCA5A5;
    }
    .pending-actions .stButton:nth-child(2) > button:hover {
        background: #FEE2E2;
        border-color: #EF4444;
    }
    .pending-actions .stButton:nth-child(3) > button { /* Confirm */
        background: #ECFDF5;
        color: #065F46;
        border: 1px solid #6EE7B7;
    }
    .pending-actions .stButton:nth-child(3) > button:hover {
        background: #D1FAE5;
        border-color: #34D399;
    }
    
    /* Additional header styling for better proportions */
    .stMarkdown h4 {
        font-size: 1rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.3rem !important;
    }
    
    .stMarkdown h5 {
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.2rem !important;
    }
    
    /* Subheader styling */
    .stMarkdown h2:not(.main-header) {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
        color: #2c3e50 !important;
    }
    
    /* Better spacing for content sections */
    .stMarkdown p {
        margin-bottom: 0.5rem !important;
        font-size: 0.9rem !important;
    }
    
    /* Info banner styling */
    .stInfo {
        font-size: 0.85rem !important;
        padding: 0.6rem !important;
    }
    
    /* Better table styling */
    .stDataFrame {
        font-size: 0.85rem;
    }
    
    .stDataFrame table {
        border-collapse: collapse;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .stDataFrame th {
        background-color: #f8f9fa;
        font-weight: 600;
        font-size: 0.8rem;
        padding: 0.6rem 0.8rem;
        border-bottom: 2px solid #dee2e6;
    }
    
    .stDataFrame td {
        padding: 0.5rem 0.8rem;
        border-bottom: 1px solid #f1f3f4;
        font-size: 0.8rem;
    }
    
    .stDataFrame tr:hover {
        background-color: #f8f9fa;
    }
    
    /* Improved selectbox styling */
    .stSelectbox > div > div {
        font-size: 0.85rem;
        padding: 0.4rem 0.6rem;
    }
    
    /* Better metric cards */
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
        border-radius: 12px;
        border-left: 4px solid #1f77b4;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin: 0.5rem 0;
    }
    
    /* Improved info boxes */
    .info-box {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border: 1px solid #bee5eb;
        border-radius: 8px;
        padding: 0.8rem;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    
    /* Better tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-size: 0.85rem;
        font-weight: 500;
        padding: 0.5rem 1rem;
        border-radius: 6px;
    }
    
    /* Improved buttons */
    .stButton > button {
        font-size: 0.85rem;
        font-weight: 500;
        border-radius: 6px;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }
    
    /* Better form styling */
    .stForm {
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 1rem;
        background-color: #fafbfc;
    }
    
    /* Improved text inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {
        font-size: 0.85rem;
        padding: 0.5rem 0.6rem;
        border-radius: 6px;
    }
    
    /* Better date inputs */
    .stDateInput > div > div > input {
        font-size: 0.85rem;
        padding: 0.5rem 0.6rem;
    }
    
    /* Smooth transitions */
    * {
        transition: all 0.2s ease;
    }
    
    /* Better spacing for columns */
    .stColumns {
        gap: 1rem;
    }
    
    /* Improved sidebar navigation */
    .css-1d391kg .stMarkdown h3 {
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    
    /* Better option menu styling */
    .css-1d391kg .stSelectbox label {
        font-size: 0.8rem;
        font-weight: 500;
        margin-bottom: 0.2rem;
    }
    
    /* Organization dropdown styling */
    .css-1d391kg .stSelectbox {
        margin-bottom: 0.8rem;
    }
    
    .css-1d391kg .stSelectbox > div > div {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 500;
        min-height: 2.5rem;
        display: flex;
        align-items: center;
        padding: 0.5rem 0.75rem;
    }
    
    .css-1d391kg .stSelectbox > div > div:hover {
        border-color: #1f77b4;
        box-shadow: 0 2px 4px rgba(31, 119, 180, 0.1);
    }
    
    /* Fix all dropdowns to show data properly with smaller font */
    .stSelectbox > div > div > div:first-child {
        color: #1a1a1a !important;
        font-weight: 600 !important;
        font-size: 0.75rem !important;
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: unset !important;
        max-width: none !important;
        width: auto !important;
        display: block !important;
        line-height: 1.3 !important;
    }
    
    /* Ensure all selectbox text is visible */
    .stSelectbox > div > div {
        min-width: 150px !important;
        width: 100% !important;
        font-size: 0.75rem !important;
    }
    
    .stSelectbox > div > div > div:first-child {
        min-width: 120px !important;
        width: auto !important;
        max-width: none !important;
        font-size: 0.75rem !important;
    }
    
    /* Fix dropdown options font size */
    .stSelectbox > div > div > div {
        font-size: 0.75rem !important;
        color: #1a1a1a !important;
    }
    
    /* Ensure dropdown container has proper sizing */
    .stSelectbox > div > div {
        padding: 0.3rem 0.5rem !important;
        min-height: 2rem !important;
    }
    
    /* Fix dropdown options menu */
    .stSelectbox > div > div[role="combobox"] {
        font-size: 0.8rem !important;
    }
    
    /* Target the actual dropdown options */
    .stSelectbox > div > div > div[role="option"] {
        font-size: 0.8rem !important;
        color: #2c3e50 !important;
        padding: 0.3rem 0.5rem !important;
    }
    
    /* Fix for Streamlit's dropdown menu */
    div[data-baseweb="select"] > div > div {
        font-size: 0.8rem !important;
    }
    
    div[data-baseweb="select"] > div > div > div {
        font-size: 0.8rem !important;
        color: #2c3e50 !important;
    }
    
    /* Additional fix for dropdown text visibility */
    .stSelectbox label + div > div {
        font-size: 0.8rem !important;
        color: #2c3e50 !important;
    }
    
    /* Comprehensive dropdown fix */
    .stSelectbox * {
        font-size: 0.75rem !important;
    }
    
    .stSelectbox input {
        font-size: 0.75rem !important;
        color: #1a1a1a !important;
    }
    
    /* Fix for all select elements */
    select, option {
        font-size: 0.75rem !important;
        color: #1a1a1a !important;
    }
    
    /* Target Streamlit's specific dropdown classes */
    .css-1d391kg .stSelectbox > div > div > div:first-child {
        font-size: 0.75rem !important;
        color: #1a1a1a !important;
        font-weight: 600 !important;
    }
    
    /* Additional visibility fixes */
    .stSelectbox > div > div > div:first-child {
        opacity: 1 !important;
        visibility: visible !important;
        display: block !important;
    }
    
    /* Force text to be visible */
    .stSelectbox > div > div {
        background-color: #ffffff !important;
        border: 1px solid #d1d5db !important;
    }
    
    /* Dropdown arrow styling */
    .css-1d391kg .stSelectbox > div > div > div:last-child {
        color: #6c757d !important;
    }
    
    /* Reduce font size of metric numbers for better visual appeal */
    .stMetric > div > div > div {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
    }
    
    .stMetric > div > div > div[data-testid="metric-value"] {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }
    
    .stMetric > div > div > div[data-testid="metric-delta"] {
        font-size: 0.9rem !important;
    }
    
    /* Target specific metric containers */
    .stMetric {
        font-size: 0.9rem !important;
    }
    
    .stMetric > div {
        font-size: 0.9rem !important;
    }
    
    .stMetric > div > div {
        font-size: 0.9rem !important;
    }
    
    /* Reduce font size for metric labels */
    .stMetric > div > div > div[data-testid="metric-label"] {
        font-size: 0.8rem !important;
        font-weight: 500 !important;
    }
    
    /* Additional metric number styling for better visual hierarchy */
    .stMetric [data-testid="metric-value"] {
        font-size: 1.0rem !important;
        font-weight: 700 !important;
        color: #1f2937 !important;
    }
    
    .stMetric [data-testid="metric-label"] {
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        color: #6b7280 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    
    /* Target all metric containers for consistent sizing */
    .stMetric > div > div {
        padding: 0.5rem !important;
        min-height: auto !important;
    }
    
    /* Reduce spacing in metric cards */
    .stMetric {
        margin: 0.25rem 0 !important;
        padding: 0.5rem !important;
    }
    
    /* Reduce overall dashboard spacing for compact layout */
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }
    
    /* Reduce spacing between sections */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Reduce spacing in columns */
    .stColumns {
        gap: 0.5rem !important;
    }
    
    /* Compact metric containers */
    .stMetric > div {
        padding: 0.25rem !important;
        margin: 0.1rem !important;
    }
    
    /* Reduce spacing in financial overview */
    .stMetric-container {
        margin-bottom: 0.5rem !important;
    }
    
    /* Compact info boxes */
    .info-box {
        margin: 0.25rem 0 !important;
        padding: 0.5rem !important;
    }
    
    /* Reduce spacing in recent activity */
    .stMarkdown p {
        margin: 0.2rem 0 !important;
        line-height: 1.2 !important;
    }
    
    /* Compact list items */
    .stMarkdown ul, .stMarkdown ol {
        margin: 0.25rem 0 !important;
        padding-left: 1rem !important;
    }
    
    .stMarkdown li {
        margin: 0.1rem 0 !important;
        line-height: 1.2 !important;
    }
    
    /* Reduce spacing in expandable sections */
    .stExpander {
        margin: 0.25rem 0 !important;
    }
    
    .stExpander > div {
        padding: 0.25rem !important;
    }
    
    /* Compact form elements */
    .stForm {
        padding: 0.5rem !important;
        margin: 0.25rem 0 !important;
    }
    
    /* Reduce spacing in dataframes */
    .stDataFrame {
        margin: 0.25rem 0 !important;
    }
    
    /* Compact button spacing */
    .stButton {
        margin: 0.1rem 0 !important;
    }
    
    /* Reduce spacing in selectbox containers */
    .stSelectbox {
        margin: 0.1rem 0 !important;
    }
    
    /* Compact alert/error messages */
    .stAlert {
        margin: 0.25rem 0 !important;
        padding: 0.5rem !important;
    }
    
    /* Reduce spacing in tabs */
    .stTabs {
        margin: 0.25rem 0 !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.25rem 0.5rem !important;
        margin: 0.1rem !important;
    }
    
    /* Compact sidebar spacing */
    .css-1d391kg {
        padding: 0.5rem !important;
    }
    
    /* Reduce spacing in main content headers */
    .main-header {
        margin: 0.25rem 0 !important;
        padding: 0.25rem 0 !important;
    }
    
    /* Compact financial overview section */
    .stMarkdown h2 {
        margin: 0.25rem 0 !important;
        padding: 0.25rem 0 !important;
    }
    
    /* Reduce spacing in horizontal dividers */
    .stMarkdown hr {
        margin: 0.25rem 0 !important;
    }
    
    /* Ultra-compact layout for dashboard */
    .stApp {
        padding: 0 !important;
    }
    
    /* Reduce main content area padding */
    .main .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    
    /* Compact section spacing */
    .stMarkdown h2 {
        margin-top: 0.25rem !important;
        margin-bottom: 0.25rem !important;
        padding: 0.1rem 0 !important;
    }
    
    /* Reduce spacing in financial metrics grid */
    .stColumns > div {
        padding: 0.1rem !important;
    }
    
    /* Compact metric styling */
    .stMetric {
        margin: 0.1rem !important;
        padding: 0.25rem !important;
    }
    
    .stMetric > div {
        padding: 0.1rem !important;
        margin: 0 !important;
    }
    
    /* Reduce spacing in recent activity section */
    .stMarkdown h3 {
        margin: 0.2rem 0 !important;
        padding: 0.1rem 0 !important;
    }
    
    /* Compact list styling */
    .stMarkdown ul {
        margin: 0.1rem 0 !important;
        padding-left: 0.8rem !important;
    }
    
    .stMarkdown li {
        margin: 0.05rem 0 !important;
        padding: 0 !important;
    }
    
    /* Reduce spacing in columns for recent activity */
    .stColumns > div[data-testid="column"] {
        padding: 0.1rem !important;
    }
    
    /* Compact info messages */
    .stInfo, .stSuccess, .stWarning, .stError {
        margin: 0.1rem 0 !important;
        padding: 0.25rem !important;
    }
    
    /* Reduce spacing in date filter section */
    .stSelectbox {
        margin: 0.05rem 0 !important;
    }
    
    /* Compact organization banner */
    .stMarkdown p {
        margin: 0.1rem 0 !important;
        line-height: 1.1 !important;
    }
    
    /* Organization dropdown specific styling - larger size */
    [data-testid="stSelectbox"]:has([aria-label*="Organization"]) {
        margin-bottom: 1rem;
    }
    
    [data-testid="stSelectbox"]:has([aria-label*="Organization"]) > div > div {
        background-color: #ffffff;
        border: 2px solid #e9ecef;
        border-radius: 8px;
        font-size: 1rem;
        font-weight: 600;
        color: #1f77b4;
        min-height: 3.2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        padding: 0.8rem 1rem;
    }
    
    [data-testid="stSelectbox"]:has([aria-label*="Organization"]) > div > div:hover {
        border-color: #1f77b4;
        box-shadow: 0 2px 6px rgba(31, 119, 180, 0.15);
    }
    
    /* Simple fix for organization dropdown text display */
    .stSelectbox > div > div > div:first-child {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: #2c3e50 !important;
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: unset !important;
        max-width: none !important;
        width: auto !important;
    }
    
    /* Additional organization dropdown fixes */
    .stSelectbox[data-testid="stSelectbox"] label {
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        color: #1f77b4 !important;
        margin-bottom: 0.3rem !important;
    }
    
    /* Ensure the selected value is visible */
    .stSelectbox > div > div > div:first-child {
        color: #2c3e50 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    
    /* Fix for organization dropdown specifically */
    div[data-testid="stSelectbox"]:has(label:contains("Organization")) {
        margin-bottom: 1rem;
        width: 100% !important;
    }
    
    div[data-testid="stSelectbox"]:has(label:contains("Organization")) > div {
        width: 100% !important;
    }
    
    div[data-testid="stSelectbox"]:has(label:contains("Organization")) > div > div {
        background-color: #ffffff !important;
        border: 2px solid #e9ecef !important;
        border-radius: 8px !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: #1f77b4 !important;
        min-height: 2.6rem !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
        padding: 0.5rem 0.7rem !important;
        width: 100% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
    }
    
    div[data-testid="stSelectbox"]:has(label:contains("Organization")) > div > div > div {
        color: #2c3e50 !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: unset !important;
        flex: 1 !important;
        min-width: 0 !important;
        width: auto !important;
        max-width: none !important;
        display: inline-block !important;
    }
    
    /* More aggressive fix for organization dropdown */
    .stSelectbox label:contains("Organization") + div > div {
        width: 100% !important;
        min-width: 250px !important;
        max-width: none !important;
    }
    
    .stSelectbox label:contains("Organization") + div > div > div {
        width: auto !important;
        min-width: 200px !important;
        max-width: none !important;
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: unset !important;
    }
    
    /* Force organization dropdown to show full text */
    [data-testid="stSelectbox"] label[for*="sidebar_organization_selector"] + div {
        width: 100% !important;
        min-width: 250px !important;
    }
    
    [data-testid="stSelectbox"] label[for*="sidebar_organization_selector"] + div > div {
        width: 100% !important;
        min-width: 250px !important;
        max-width: none !important;
    }
    
    [data-testid="stSelectbox"] label[for*="sidebar_organization_selector"] + div > div > div {
        width: auto !important;
        min-width: 200px !important;
        max-width: none !important;
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: unset !important;
    }
    
    /* Ensure the dropdown container has enough width */
    .css-1d391kg .stSelectbox {
        width: 100% !important;
        max-width: 100% !important;
    }
    
    .css-1d391kg .stSelectbox > div {
        width: 100% !important;
        max-width: 100% !important;
    }
    
    .css-1d391kg .stSelectbox > div > div {
        width: 100% !important;
        max-width: 100% !important;
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
    
    /* Compact status indicators spacing */
    .stAlert {
        margin: 0.1rem 0 !important;
        padding: 0.4rem 0.8rem !important;
    }
    
    /* Reduce spacing for all alert boxes */
    .stInfo, .stSuccess, .stError, .stWarning {
        margin: 0.2rem 0 !important;
        padding: 0.5rem 1rem !important;
    }
    
    /* Target specific alert types for tighter spacing */
    .stSuccess, .stInfo, .stError, .stWarning {
        margin-top: 0.1rem !important;
        margin-bottom: 0.1rem !important;
    }
    
    /* Reduce spacing between consecutive alerts */
    .stAlert + .stAlert {
        margin-top: 0.1rem !important;
    }
    
    /* Dashboard column alignment */
    .stColumns {
        align-items: flex-start !important;
    }
    
    /* Ensure consistent spacing in dashboard columns */
    .stColumn > div {
        padding-top: 0 !important;
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
        st.session_state.auth_mode = 'signin'  # 'signin' or 'signup'

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
            <div style="text-align: center; padding: 2rem 0 1rem 0;">
                <h1 style="color: #1f77b4; font-size: 2.2rem; margin-bottom: 0.3rem; font-weight: 700;">
                    🏠 PropLedger
                </h1>
                <p style="color: #888; font-size: 0.95rem; margin: 0;">
                    Rental Property Management System
                </p>
            </div>
        """, unsafe_allow_html=True)

        # Tab-like buttons for switching between Sign In and Sign Up
        col_signin, col_signup = st.columns(2)
        with col_signin:
            if st.button("Sign In", use_container_width=True, type="primary" if st.session_state.auth_mode == 'signin' else "secondary"):
                st.session_state.auth_mode = 'signin'
                st.rerun()
        with col_signup:
            if st.button("Sign Up", use_container_width=True, type="primary" if st.session_state.auth_mode == 'signup' else "secondary"):
                st.session_state.auth_mode = 'signup'
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # SIGN IN FORM
        if st.session_state.auth_mode == 'signin':
            st.markdown("""
                <div style="text-align: center; padding-bottom: 1.5rem;">
                    <h2 style="color: #333; font-size: 1.6rem; margin: 0; font-weight: 600;">
                        Welcome back
                    </h2>
                    <p style="color: #666; font-size: 0.95rem; margin-top: 0.3rem;">
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
                <div style="text-align: center; padding-bottom: 1.5rem;">
                    <h2 style="color: #333; font-size: 1.6rem; margin: 0; font-weight: 600;">
                        Create your account
                    </h2>
                    <p style="color: #666; font-size: 0.95rem; margin-top: 0.3rem;">
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

        # Demo access section
        st.markdown("<br><hr><br>", unsafe_allow_html=True)

        st.markdown("""
            <div style="text-align: center; padding: 1rem 0;">
                <h3 style="color: #333; font-size: 1.2rem; margin-bottom: 0.5rem;">
                    🎯 Want to try without signing up?
                </h3>
                <p style="color: #666; font-size: 0.9rem; margin-bottom: 1.5rem;">
                    Explore all features with our interactive demo
                </p>
            </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 Try Demo Version", type="secondary", use_container_width=True):
            st.session_state.authenticated = True
            st.session_state.user = {"email": "demo@example.com", "user_metadata": {"full_name": "Demo User"}}
            st.rerun()

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

    # Sidebar navigation - Compact layout
    with st.sidebar:
        # Compact header with styling
        st.markdown("""
            <div style="background-color: #f8f9fa; padding: 12px; border-radius: 8px; margin-bottom: 15px; text-align: center;">
                <h3 style="margin: 0; color: #1f77b4;">🏠 PropLedger</h3>
            </div>
        """, unsafe_allow_html=True)


        # Navigation - Most important section (moved to top)
        selected = option_menu(
            menu_title=None,  # Remove the "Navigation" title
            options=["Organizations Dashboard", "Dashboard", "Properties", "Accounting", "Budget Planner", "Analytics", "Reminders", "Reports", "AI Insights"],
            icons=["building", "speedometer2", "house", "calculator", "calculator", "graph-up", "bell", "file-earmark-text", "robot"],
            menu_icon="cast",
            default_index=1,
            key="main_navigation",
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa", "margin": "0", "border-radius": "8px"},
                "icon": {"color": "#1f77b4", "font-size": "18px"}, 
                "nav-link": {"font-size": "13px", "text-align": "left", "margin": "2px 0", "padding": "6px 10px", "border-radius": "6px", "font-weight": "500"},
                "nav-link-selected": {"background-color": "#02ab21", "color": "white"},
                "nav-link:hover": {"background-color": "#e9ecef", "color": "#1f77b4"},
            }
        )
        
        # Compact user info section
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
            
            # User info section with styling
            user_info_html = f"""
                <div style="background-color: #f8f9fa; padding: 10px; border-radius: 8px; margin-bottom: 10px;">
                    <div style="font-size: 14px; color: #495057; margin-bottom: 5px;">👤 {user_name}</div>
            """

            # Get user organizations for display
            if user_id:
                db = DatabaseOperations()
                organizations = db.get_user_organizations(user_id)
                if organizations:
                    # Set default organization if not set
                    if 'selected_organization' not in st.session_state:
                        # Use default organization if set, otherwise first organization
                        if 'default_organization' in st.session_state:
                            st.session_state.selected_organization = st.session_state.default_organization
                        else:
                            st.session_state.selected_organization = organizations[0].id

                    # Display current organization name
                    current_org = next((org for org in organizations if org.id == st.session_state.selected_organization), organizations[0])
                    user_info_html += f'<div style="font-size: 14px; color: #495057;">🏢 {current_org.name}</div>'
                else:
                    user_info_html += '<div style="font-size: 12px; color: #856404; background-color: #fff3cd; padding: 5px; border-radius: 4px; margin-top: 5px;">No organizations found</div>'
                    if 'selected_organization' in st.session_state:
                        del st.session_state.selected_organization

            # Check if it's demo mode (only show demo mode, hide authenticated)
            if hasattr(st.session_state.user, 'email'):
                is_demo = getattr(st.session_state.user, 'email', '') == 'demo@example.com'
            else:
                is_demo = st.session_state.user.get('email', '') == 'demo@example.com'

            if is_demo:
                user_info_html += '<div style="font-size: 13px; color: #1f77b4; margin-top: 5px;">🎯 DEMO MODE</div>'

            user_info_html += '</div>'
            st.markdown(user_info_html, unsafe_allow_html=True)

        # Logout button with consistent styling
        st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()

    # Main content based on selected page
    if selected == "Organizations Dashboard":
        # Organization selector for Organizations Dashboard
        if st.session_state.user:
            # Handle both dict and User object types
            if hasattr(st.session_state.user, 'email'):
                user_id = getattr(st.session_state.user, 'id', None)
            else:
                user_id = st.session_state.user.get('id', None)
            
            if user_id:
                db = DatabaseOperations()
                organizations = db.get_user_organizations(user_id)
                if organizations:
                    org_names = [org.name for org in organizations]
                    
                    # Set default organization if not set
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
                    
                    # Organization selector and Date Filter side by side
                    filter_col1, filter_col2 = st.columns(2)

                    with filter_col1:
                        selected_org_name = st.selectbox(
                            "Select Organization",
                            options=org_names,
                            index=selected_index,
                            key="org_dashboard_organization_selector",
                            help="Selected organization will be set as default automatically"
                        )

                    with filter_col2:
                        date_filter_type = st.selectbox(
                            "Date Filter",
                            ["Current Year", "All Time", "Custom Range", "Last 3 Years", "Last 5 Years"],
                            key="org_dashboard_date_filter_type"
                        )

                    # Custom date range inputs (if Custom Range selected)
                    if date_filter_type == "Custom Range":
                        date_col1, date_col2 = st.columns(2)
                        with date_col1:
                            start_date = st.date_input(
                                "Start Date",
                                value=datetime.now().date().replace(month=1, day=1),
                                key="org_dashboard_start_date"
                            )
                        with date_col2:
                            end_date = st.date_input(
                                "End Date",
                                value=datetime.now().date(),
                                key="org_dashboard_end_date"
                            )
                    else:
                        start_date = None
                        end_date = None

                    # Automatically update selected organization and set as default
                    for org in organizations:
                        if org.name == selected_org_name:
                            st.session_state.selected_organization = org.id
                            st.session_state.default_organization = org.id  # Automatically set as default
                            break
                else:
                    st.warning("No organizations found")
                    if 'selected_organization' in st.session_state:
                        del st.session_state.selected_organization

        # Check if demo mode
        is_demo_mode = False
        if st.session_state.user:
            if hasattr(st.session_state.user, 'email'):
                is_demo_mode = getattr(st.session_state.user, 'email', '') == 'demo@example.com'
            else:
                is_demo_mode = st.session_state.user.get('email', '') == 'demo@example.com'

        if is_demo_mode:
            # Demo mode - show sample organizations
            st.info("🎯 **Demo Mode** - Showing sample organizations. Sign up to manage your own organizations!")

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
                            with st.expander(f"🏢 {org.name}", expanded=False):
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.markdown(f"**Description:** {org.description or 'No description provided'}")
                                    st.markdown(f"**Created:** {org.created_at.strftime('%Y-%m-%d') if org.created_at else 'Unknown'}")
                                
                                with col2:
                                    # Get organization stats
                                    properties = db.get_properties()
                                    org_properties = [p for p in properties if p.organization_id == org.id]

                                # Display metrics in organized layout
                                st.markdown("---")
                                st.markdown("#### 📊 Organization Metrics")

                                # Get financial data for P&L
                                if org_properties:
                                    total_value = sum(p.purchase_price for p in org_properties)
                                    total_rent = sum(p.monthly_rent for p in org_properties)

                                    all_income = db.get_all_income()
                                    all_expenses = db.get_all_expenses()

                                    org_income = [inc for inc in all_income if inc.organization_id == org.id]
                                    org_expenses = [exp for exp in all_expenses if exp.organization_id == org.id]

                                    total_income = sum(inc.amount for inc in org_income)
                                    total_expenses = sum(exp.amount for exp in org_expenses)
                                    net_income = total_income - total_expenses
                                    profit_margin = (net_income / total_income * 100) if total_income > 0 else 0
                                    roi = (net_income / total_value * 100) if total_value > 0 else 0

                                    # First row - Property metrics
                                    metric_col1, metric_col2, metric_col3 = st.columns(3)
                                    with metric_col1:
                                        st.metric("Properties", len(org_properties))
                                    with metric_col2:
                                        st.metric("Total Value", f"${total_value:,.2f}")
                                    with metric_col3:
                                        st.metric("Monthly Rent", f"${total_rent:,.2f}")

                                    # Second row - Income/Expense metrics
                                    metric_col4, metric_col5, metric_col6 = st.columns(3)
                                    with metric_col4:
                                        st.metric("Total Income", f"${total_income:,.2f}")
                                    with metric_col5:
                                        st.metric("Total Expenses", f"${total_expenses:,.2f}")
                                    with metric_col6:
                                        st.metric("Net Income", f"${net_income:,.2f}")

                                    # Third row - Performance metrics
                                    metric_col7, metric_col8, metric_col9 = st.columns(3)
                                    with metric_col7:
                                        st.metric("Profit Margin", f"{profit_margin:.1f}%")
                                    with metric_col8:
                                        st.metric("ROI", f"{roi:.1f}%")
                                else:
                                    st.metric("Properties", len(org_properties))
                            
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
        # Date filter for Dashboard
        col1, col2, col3 = st.columns([2, 2, 2])
        
        with col1:
            date_filter_type = st.selectbox(
                "Date Filter",
                ["Current Year", "All Time", "Custom Range", "Last 3 Years", "Last 5 Years"],
                key="dashboard_date_filter_type"
            )
        
        with col2:
            if date_filter_type == "Custom Range":
                start_date = st.date_input(
                    "Start Date",
                    value=datetime.now().date().replace(month=1, day=1),
                    key="dashboard_start_date"
                )
            else:
                start_date = None
        
        with col3:
            if date_filter_type == "Custom Range":
                end_date = st.date_input(
                    "End Date",
                    value=datetime.now().date(),
                    key="dashboard_end_date"
                )
            else:
                end_date = None
        
        # Get data based on authentication mode
        is_demo_mode = False
        if st.session_state.user:
            if hasattr(st.session_state.user, 'email'):
                is_demo_mode = getattr(st.session_state.user, 'email', '') == 'demo@example.com'
            else:
                is_demo_mode = st.session_state.user.get('email', '') == 'demo@example.com'
        
        if is_demo_mode:
            # Demo mode - use sample data
            st.info("🎯 **Demo Mode** - Showing sample data. Sign up to use your own data!")
            
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
                
                # Split screen: 60% (left) and 40% (right)
                left_col, right_col = st.columns([0.6, 0.4])

                with left_col:
                    # Financial Summary
                    st.markdown("#### 📊 Financial Summary")
                    # Financial metrics in 2 rows of 3 columns each
                    row1_col1, row1_col2, row1_col3 = st.columns(3)
                    with row1_col1:
                        st.metric("🏠 Properties", total_properties)
                    with row1_col2:
                        st.metric("💰 Monthly Rent", f"${total_monthly_rent:,.0f}")
                    with row1_col3:
                        st.metric("📊 Total Income", f"${total_income:,.0f}")

                    row2_col1, row2_col2, row2_col3 = st.columns(3)
                    with row2_col1:
                        st.metric("💸 Total Expenses", f"${total_expenses:,.0f}")
                    with row2_col2:
                        st.metric("📈 Net Income", f"${net_income:,.0f}")
                    with row2_col3:
                        st.metric("📊 ROI", f"{roi:.1f}%")

                    st.markdown("---")

                    # Income & Expense Breakdown
                    st.markdown("#### 💰 Income & Expense Breakdown")

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
                            type_cols = st.columns(min(len(all_types), 4))  # Max 4 columns for better fit
                            for i, (type_name, amount) in enumerate(all_types[:4]):  # Limit to 4 items
                                with type_cols[i]:
                                    icon = "💰" if type_name in [inc[0] for inc in income_by_type.items()] else "💸"
                                    st.metric(f"{icon} {type_name}", f"${amount:,.0f}")
                    else:
                        st.info("No income or expense records found")

                    st.markdown("---")

                    # Recent Activity - Last 10 Transactions
                    st.markdown("#### 📋 Recent Activity (Last 10 Transactions)")

                    # Get all transactions combined
                    all_transactions = []

                    # Add income transactions
                    for inc in org_income:
                        prop_name = next((p.name for p in org_properties if p.id == inc.property_id), "Unknown")
                        all_transactions.append({
                            'Property': prop_name,
                            'Amount': inc.amount,
                            'Amount_Display': f"${inc.amount:,.2f}",
                            'Type': inc.income_type.value.title(),
                            'Category': 'Income',
                            'Description': inc.description,
                            'Date': inc.transaction_date,
                            'Date_Display': inc.transaction_date.strftime('%Y-%m-%d')
                        })

                    # Add expense transactions
                    for exp in org_expenses:
                        prop_name = next((p.name for p in org_properties if p.id == exp.property_id), "Unknown")
                        all_transactions.append({
                            'Property': prop_name,
                            'Amount': exp.amount,
                            'Amount_Display': f"${exp.amount:,.2f}",
                            'Type': exp.expense_type.value.title(),
                            'Category': 'Expense',
                            'Description': exp.description,
                            'Date': exp.transaction_date,
                            'Date_Display': exp.transaction_date.strftime('%Y-%m-%d')
                        })

                    # Sort by date (most recent first) and take last 10
                    all_transactions.sort(key=lambda x: x['Date'], reverse=True)
                    recent_10_transactions = all_transactions[:10]

                    if recent_10_transactions:
                        # Display the table
                        df_recent = pd.DataFrame([{
                            'Property': t['Property'],
                            'Category': t['Category'],
                            'Type': t['Type'],
                            'Amount': t['Amount_Display'],
                            'Description': t['Description'],
                            'Date': t['Date_Display']
                        } for t in recent_10_transactions])
                        st.dataframe(df_recent, use_container_width=True, hide_index=True)
                    else:
                        st.info("No recent transactions found")

                with right_col:
                    # Create a financial overview chart
                    st.markdown("#### 📈 Financial Summary")
                    
                    # Prepare data for the chart
                    chart_data = {
                        'Category': ['Income', 'Expenses', 'Net Income'],
                        'Amount': [total_income, total_expenses, net_income]
                    }
                    
                    # Create a bar chart
                    fig = go.Figure(data=[
                        go.Bar(
                            x=chart_data['Category'],
                            y=chart_data['Amount'],
                            marker_color=['#2E8B57', '#DC143C', '#4169E1'],
                            text=[f"${amount:,.0f}" for amount in chart_data['Amount']],
                            textposition='auto',
                        )
                    ])
                    
                    fig.update_layout(
                        title="Financial Overview",
                        xaxis_title="Category",
                        yaxis_title="Amount ($)",
                        height=300,
                        margin=dict(l=20, r=20, t=40, b=20),
                        showlegend=False,
                        font=dict(size=10)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Add a pie chart for income breakdown
                    if org_income:
                        income_by_type = {}
                        for inc in org_income:
                            income_type = inc.income_type.value.title()
                            if income_type not in income_by_type:
                                income_by_type[income_type] = 0
                            income_by_type[income_type] += inc.amount
                        
                        if income_by_type:
                            st.markdown("#### 💰 Income Breakdown")
                            pie_fig = go.Figure(data=[go.Pie(
                                labels=list(income_by_type.keys()),
                                values=list(income_by_type.values()),
                                hole=0.3,
                                textinfo='label+percent',
                                textfont_size=10
                            )])
                            
                            pie_fig.update_layout(
                                height=250,
                                margin=dict(l=10, r=10, t=20, b=10),
                                font=dict(size=9)
                            )
                            
                            st.plotly_chart(pie_fig, use_container_width=True)
                        
                        # Add Expenses Breakdown pie chart
                        st.markdown("#### 💸 Expenses Breakdown")
                        
                        # Calculate expenses by type
                        expenses_by_type = {}
                        for exp in org_expenses:
                            expense_type = exp.expense_type.value.title()
                            if expense_type not in expenses_by_type:
                                expenses_by_type[expense_type] = 0
                            expenses_by_type[expense_type] += exp.amount
                        
                        if expenses_by_type:
                            exp_pie_fig = go.Figure(data=[go.Pie(
                                labels=list(expenses_by_type.keys()),
                                values=list(expenses_by_type.values()),
                                hole=0.3,
                                textinfo='label+percent',
                                textfont_size=10
                            )])
                            
                            exp_pie_fig.update_layout(
                                height=250,
                                margin=dict(l=10, r=10, t=20, b=10),
                                font=dict(size=9)
                            )
                            
                            st.plotly_chart(exp_pie_fig, use_container_width=True)
                        else:
                            st.info("No expense data available for breakdown")

    elif selected == "Properties":
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

            # Get organization name for display
            org = db.get_organization_by_id(selected_org_id)
            org_name = org.name if org else "Unknown Organization"

            # Real property management with organization filtering
            # Tabs for property management
            tab1, tab2, tab3 = st.tabs(["View Properties", "Add/Edit Property", "Managing Properties"])

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
            
            with tab3:
                st.subheader("🗑️ Managing Properties")
                st.markdown("Manage your properties - view details, edit, or delete properties.")
                
                # Get properties for the organization
                properties = db.get_properties()
                org_properties = [p for p in properties if p.organization_id == selected_org_id]
                
                if org_properties:
                    st.markdown(f"**Found {len(org_properties)} properties for {org_name}**")
                    
                    # Property filter section
                    st.markdown("---")
                    st.markdown("#### 🔍 Filter Properties")
                    
                    # Create filter options
                    filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])
                    
                    with filter_col1:
                        # Property name filter
                        property_names = [f"{prop.name} - {prop.address}" for prop in org_properties]
                        selected_property_filter = st.selectbox(
                            "Select Property to Manage",
                            ["All Properties"] + property_names,
                            key="managing_property_filter"
                        )
                    
                    with filter_col2:
                        # Property type filter
                        property_types = list(set([prop.property_type.value for prop in org_properties]))
                        selected_type_filter = st.selectbox(
                            "Filter by Type",
                            ["All Types"] + property_types,
                            key="managing_type_filter"
                        )
                    
                    with filter_col3:
                        # Sort options
                        sort_option = st.selectbox(
                            "Sort by",
                            ["Name A-Z", "Name Z-A", "Rent High-Low", "Rent Low-High", "Purchase Price High-Low", "Purchase Price Low-High"],
                            key="managing_sort_filter"
                        )
                    
                    # Filter and sort properties
                    filtered_properties = org_properties.copy()
                    
                    # Apply property name filter
                    if selected_property_filter != "All Properties":
                        selected_prop_name = selected_property_filter.split(" - ")[0]
                        filtered_properties = [p for p in filtered_properties if p.name == selected_prop_name]
                    
                    # Apply property type filter
                    if selected_type_filter != "All Types":
                        filtered_properties = [p for p in filtered_properties if p.property_type.value == selected_type_filter]
                    
                    # Apply sorting
                    if sort_option == "Name A-Z":
                        filtered_properties.sort(key=lambda x: x.name)
                    elif sort_option == "Name Z-A":
                        filtered_properties.sort(key=lambda x: x.name, reverse=True)
                    elif sort_option == "Rent High-Low":
                        filtered_properties.sort(key=lambda x: x.monthly_rent, reverse=True)
                    elif sort_option == "Rent Low-High":
                        filtered_properties.sort(key=lambda x: x.monthly_rent)
                    elif sort_option == "Purchase Price High-Low":
                        filtered_properties.sort(key=lambda x: x.purchase_price, reverse=True)
                    elif sort_option == "Purchase Price Low-High":
                        filtered_properties.sort(key=lambda x: x.purchase_price)
                    
                    # Display filter results
                    if selected_property_filter != "All Properties" or selected_type_filter != "All Types":
                        st.info(f"Showing {len(filtered_properties)} of {len(org_properties)} properties")
                    
                    st.markdown("---")
                    
                    # Create a more detailed property management interface
                    for i, prop in enumerate(filtered_properties):
                        with st.container():
                            st.markdown("---")
                            
                            # Property header with name and address
                            col1, col2, col3 = st.columns([3, 1, 1])
                            
                            with col1:
                                st.markdown(f"### 🏠 {prop.name}")
                                st.markdown(f"**Address:** {prop.address}")
                                st.markdown(f"**Type:** {prop.property_type.value.title()}")
                            
                            with col2:
                                st.markdown("**Monthly Rent**")
                                st.markdown(f"${prop.monthly_rent:,.0f}")
                            
                            with col3:
                                st.markdown("**Purchase Price**")
                                st.markdown(f"${prop.purchase_price:,.0f}")
                            
                            # Financial summary
                            financial_summary = db.get_property_financial_summary(prop.id)
                            
                            # Create columns for financial metrics
                            fin_col1, fin_col2, fin_col3, fin_col4 = st.columns(4)
                            
                            with fin_col1:
                                st.metric("Total Income", f"${financial_summary['total_income']:,.0f}")
                            
                            with fin_col2:
                                st.metric("Total Expenses", f"${financial_summary['total_expenses']:,.0f}")
                            
                            with fin_col3:
                                st.metric("Net Income", f"${financial_summary['net_income']:,.0f}")
                            
                            with fin_col4:
                                st.metric("ROI", f"{financial_summary['roi']:.1f}%")
                            
                            # Property details
                            if prop.description:
                                st.markdown(f"**Description:** {prop.description}")
                            
                            # Action buttons
                            action_col1, action_col2, action_col3 = st.columns([1, 1, 2])
                            
                            with action_col1:
                                if st.button(f"✏️ Edit", key=f"edit_prop_{prop.id}"):
                                    st.session_state[f"editing_property_{prop.id}"] = True
                                    st.rerun()
                            
                            with action_col2:
                                if st.button(f"🗑️ Delete", key=f"delete_prop_{prop.id}", type="secondary"):
                                    st.session_state[f"confirm_delete_{prop.id}"] = True
                                    st.rerun()
                            
                            # Confirmation dialog for deletion
                            if st.session_state.get(f"confirm_delete_{prop.id}", False):
                                st.warning(f"⚠️ Are you sure you want to delete '{prop.name}'? This action cannot be undone!")
                                
                                confirm_col1, confirm_col2, confirm_col3 = st.columns([1, 1, 2])
                                
                                with confirm_col1:
                                    if st.button("✅ Yes, Delete", key=f"confirm_yes_{prop.id}", type="primary"):
                                        try:
                                            # Delete the property
                                            success = db.delete_property(prop.id)
                                            if success:
                                                st.success(f"Property '{prop.name}' deleted successfully!")
                                                # Clear the confirmation state
                                                if f"confirm_delete_{prop.id}" in st.session_state:
                                                    del st.session_state[f"confirm_delete_{prop.id}"]
                                                st.rerun()
                                            else:
                                                st.error("Failed to delete property. Please try again.")
                                        except Exception as e:
                                            st.error(f"Error deleting property: {str(e)}")
                                
                                with confirm_col2:
                                    if st.button("❌ Cancel", key=f"confirm_no_{prop.id}"):
                                        # Clear the confirmation state
                                        if f"confirm_delete_{prop.id}" in st.session_state:
                                            del st.session_state[f"confirm_delete_{prop.id}"]
                                        st.rerun()
                            
                            # Edit property form (simplified)
                            if st.session_state.get(f"editing_property_{prop.id}", False):
                                st.markdown("#### ✏️ Edit Property")
                                
                                with st.form(f"edit_form_{prop.id}"):
                                    edit_name = st.text_input("Property Name", value=prop.name, key=f"edit_name_{prop.id}")
                                    edit_address = st.text_input("Address", value=prop.address, key=f"edit_address_{prop.id}")
                                    edit_type = st.selectbox("Property Type", 
                                                           options=["apartment", "house", "condo", "townhouse", "commercial"],
                                                           index=["apartment", "house", "condo", "townhouse", "commercial"].index(prop.property_type.value),
                                                           key=f"edit_type_{prop.id}")
                                    edit_price = st.number_input("Purchase Price", value=float(prop.purchase_price), key=f"edit_price_{prop.id}")
                                    edit_rent = st.number_input("Monthly Rent", value=float(prop.monthly_rent), key=f"edit_rent_{prop.id}")
                                    edit_description = st.text_area("Description", value=prop.description or "", key=f"edit_desc_{prop.id}")
                                    
                                    edit_col1, edit_col2 = st.columns(2)
                                    
                                    with edit_col1:
                                        if st.form_submit_button("💾 Save Changes", type="primary"):
                                            try:
                                                # Create updated property object
                                                updated_property = Property(
                                                    id=prop.id,
                                                    organization_id=prop.organization_id,
                                                    name=edit_name,
                                                    address=edit_address,
                                                    property_type=PropertyType(edit_type),
                                                    purchase_price=edit_price,
                                                    purchase_date=prop.purchase_date,  # Keep original date
                                                    monthly_rent=edit_rent,
                                                    description=edit_description
                                                )
                                                
                                                # Update the property
                                                success = db.update_property(prop.id, updated_property)
                                                if success:
                                                    st.success(f"Property '{edit_name}' updated successfully!")
                                                    # Clear the editing state
                                                    if f"editing_property_{prop.id}" in st.session_state:
                                                        del st.session_state[f"editing_property_{prop.id}"]
                                                    st.rerun()
                                                else:
                                                    st.error("Failed to update property. Please try again.")
                                            except Exception as e:
                                                st.error(f"Error updating property: {str(e)}")
                                    
                                    with edit_col2:
                                        if st.form_submit_button("❌ Cancel"):
                                            # Clear the editing state
                                            if f"editing_property_{prop.id}" in st.session_state:
                                                del st.session_state[f"editing_property_{prop.id}"]
                                            st.rerun()
                else:
                    st.info(f"No properties found for {org_name}. Add your first property in the 'Add/Edit Property' tab.")
                
                # Handle case when filters result in no properties
                if org_properties and not filtered_properties:
                    st.warning("No properties match the selected filters. Try adjusting your filter criteria.")

    # Add other sections (Income, Expenses, Analytics, AI Insights) similar to original app.py
    # For brevity, I'll add a placeholder for now
    elif selected == "Accounting":
        # Accounting sub-menu
        accounting_tabs = st.tabs(["💰 Income", "💸 Expenses"])
        
        # Get selected organization (shared by both Income and Expenses)
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
        
        with accounting_tabs[0]:  # Income
            # Check if demo mode
            is_demo_mode = False
            if st.session_state.user:
                if hasattr(st.session_state.user, 'email'):
                    is_demo_mode = getattr(st.session_state.user, 'email', '') == 'demo@example.com'
                else:
                    is_demo_mode = st.session_state.user.get('email', '') == 'demo@example.com'
        
            if is_demo_mode:
                # Demo mode - show sample income data
                st.info("🎯 **Demo Mode** - Showing sample income data. Sign up to manage your own income!")
            
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

            # Tabs for income management
            tab1, tab2, tab3, tab4 = st.tabs(["View/Edit Income", "Add Income", "Manage Income", "Recurring Income"])
        
            with tab1:
                if org_properties:
                        # Filter controls
                        col1, col2 = st.columns([2, 2])
                    
                        with col1:
                            # Filter by property
                            property_names = {prop.id: prop.name for prop in org_properties}
                            selected_property_id = st.selectbox("Filter by Property", ["All"] + list(property_names.keys()), 
                                                               format_func=lambda x: "All" if x == "All" else property_names[x],
                                                               key="income_property_filter")
                    
                        with col2:
                            # Date filter
                            date_filter_type = st.selectbox(
                                "Date Filter",
                                ["Current Month", "All Time", "Custom Range", "This Year", "Last 3 Months"],
                                key="income_date_filter_type"
                            )
                    
                        # Custom date range (only show if Custom Range is selected)
                        if date_filter_type == "Custom Range":
                            col3, col4 = st.columns(2)
                            with col3:
                                start_date = st.date_input(
                                    "Start Date",
                                    value=datetime.now().date() - timedelta(days=30),
                                    key="income_start_date"
                                )
                            with col4:
                                end_date = st.date_input(
                                    "End Date",
                                    value=datetime.now().date(),
                                    key="income_end_date"
                                )
                        else:
                            start_date = None
                            end_date = None

                        # Get income records based on filters
                        if selected_property_id == "All":
                            income_records = db.get_all_income()
                        else:
                            income_records = db.get_income_by_property(selected_property_id)

                        # Apply date filter
                        if income_records:
                            filtered_income_records = []
                            current_date = datetime.now()
                        
                            for record in income_records:
                                record_date = record.transaction_date
                            
                                if date_filter_type == "Current Month":
                                    if record_date.year == current_date.year and record_date.month == current_date.month:
                                        filtered_income_records.append(record)
                                elif date_filter_type == "This Year":
                                    if record_date.year == current_date.year:
                                        filtered_income_records.append(record)
                                elif date_filter_type == "Last 3 Months":
                                    three_months_ago = current_date - timedelta(days=90)
                                    if record_date >= three_months_ago:
                                        filtered_income_records.append(record)
                                elif date_filter_type == "Custom Range" and start_date and end_date:
                                    if start_date <= record_date.date() <= end_date:
                                        filtered_income_records.append(record)
                                elif date_filter_type == "All Time":
                                    filtered_income_records.append(record)
                        
                            income_records = filtered_income_records
                    
                        if income_records:
                            # Calculate total income
                            total_income = sum(inc.amount for inc in income_records)

                            # Display total and count
                            st.markdown(f"### 💰 Total Income: ${total_income:,.2f}")
                            st.markdown(f"**Found {len(income_records)} income transactions**")
                            st.markdown("---")

                            # Display income transactions with edit/delete buttons
                            for inc in income_records:
                                with st.container():
                                    st.markdown("---")
                                
                                    # Income header
                                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                                
                                    with col1:
                                        prop_name = property_names.get(inc.property_id, "Unknown Property")
                                        st.markdown(f"### 💰 {inc.income_type.value.title()}")
                                        st.markdown(f"**Property:** {prop_name}")
                                        st.markdown(f"**Description:** {inc.description}")
                                
                                    with col2:
                                        st.markdown("**Amount**")
                                        st.markdown(f"${inc.amount:,.2f}")
                                
                                    with col3:
                                        st.markdown("**Date**")
                                        st.markdown(inc.transaction_date.strftime('%Y-%m-%d'))
                                
                                    with col4:
                                        st.markdown("**Actions**")
                                        action_col1, action_col2 = st.columns(2)
                                    
                                        with action_col1:
                                            if st.button("✏️ Edit", key=f"edit_income_{inc.id}"):
                                                st.session_state[f"editing_income_{inc.id}"] = True
                                                st.rerun()
                                    
                                        with action_col2:
                                            if st.button("🗑️ Delete", key=f"delete_income_{inc.id}", type="secondary"):
                                                st.session_state[f"confirm_delete_income_{inc.id}"] = True
                                                st.rerun()
                            
                                # Confirmation dialog for deletion
                                if st.session_state.get(f"confirm_delete_income_{inc.id}", False):
                                    st.warning(f"⚠️ Are you sure you want to delete this income transaction? This action cannot be undone!")
                                
                                    confirm_col1, confirm_col2 = st.columns([1, 1])
                                
                                    with confirm_col1:
                                        if st.button("✅ Yes, Delete", key=f"confirm_yes_income_{inc.id}", type="primary"):
                                            try:
                                                    # Delete the income record
                                                    success = db.client.table("income").delete().eq("id", inc.id).execute()
                                                    if success.data:
                                                        st.success("Income transaction deleted successfully!")
                                                        # Clear the confirmation state
                                                        if f"confirm_delete_income_{inc.id}" in st.session_state:
                                                            del st.session_state[f"confirm_delete_income_{inc.id}"]
                                                        st.rerun()
                                                    else:
                                                        st.error("Failed to delete income transaction. Please try again.")
                                            except Exception as e:
                                                st.error(f"Error deleting income transaction: {str(e)}")
                                
                                    with confirm_col2:
                                        if st.button("❌ Cancel", key=f"confirm_no_income_{inc.id}"):
                                            # Clear the confirmation state
                                            if f"confirm_delete_income_{inc.id}" in st.session_state:
                                                del st.session_state[f"confirm_delete_income_{inc.id}"]
                                            st.rerun()
                                
                                    # Edit income form
                                    if st.session_state.get(f"editing_income_{inc.id}", False):
                                        st.markdown("#### ✏️ Edit Income Transaction")
                                    
                                        with st.form(f"edit_income_form_{inc.id}"):
                                            edit_col1, edit_col2 = st.columns(2)
                                        
                                            with edit_col1:
                                                edit_property_id = st.selectbox(
                                                    "Property",
                                                    options=[prop.id for prop in org_properties],
                                                    format_func=lambda x: property_names[x],
                                                    index=[prop.id for prop in org_properties].index(inc.property_id) if inc.property_id in [prop.id for prop in org_properties] else 0,
                                                    key=f"edit_income_property_{inc.id}"
                                                )
                                                edit_amount = st.number_input("Amount", value=float(inc.amount), key=f"edit_income_amount_{inc.id}")
                                                edit_type = st.selectbox("Income Type", [it.value for it in IncomeType], 
                                                                       index=[it.value for it in IncomeType].index(inc.income_type.value),
                                                                       key=f"edit_income_type_{inc.id}")
                                        
                                            with edit_col2:
                                                edit_description = st.text_input("Description", value=inc.description, key=f"edit_income_desc_{inc.id}")
                                                edit_date = st.date_input("Transaction Date", value=inc.transaction_date.date(), key=f"edit_income_date_{inc.id}")
                                        
                                            edit_form_col1, edit_form_col2 = st.columns(2)
                                        
                                            with edit_form_col1:
                                                if st.form_submit_button("💾 Save Changes", type="primary"):
                                                    try:
                                                        # Update the income record
                                                        update_data = {
                                                            "property_id": edit_property_id,
                                                            "amount": edit_amount,
                                                            "income_type": edit_type,
                                                            "description": edit_description,
                                                            "transaction_date": edit_date.isoformat()
                                                        }
                                                    
                                                        result = db.client.table("income").update(update_data).eq("id", inc.id).execute()
                                                        if result.data:
                                                            st.success("Income transaction updated successfully!")
                                                            # Clear the editing state
                                                            if f"editing_income_{inc.id}" in st.session_state:
                                                                del st.session_state[f"editing_income_{inc.id}"]
                                                            st.rerun()
                                                        else:
                                                            st.error("Failed to update income transaction. Please try again.")
                                                    except Exception as e:
                                                        st.error(f"Error updating income transaction: {str(e)}")
                                        
                                            with edit_form_col2:
                                                if st.form_submit_button("❌ Cancel"):
                                                    # Clear the editing state
                                                    if f"editing_income_{inc.id}" in st.session_state:
                                                        del st.session_state[f"editing_income_{inc.id}"]
                                                    st.rerun()

                            # Income summary
                            total_income = sum(inc.amount for inc in income_records)
                            st.metric("Total Income", f"${total_income:,.2f}")
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
    
                with tab3:  # Manage Income - Recurring Income Setup
                    # Check if demo mode
                    is_demo_mode = False
                    if st.session_state.user:
                        if hasattr(st.session_state.user, 'email'):
                            is_demo_mode = getattr(st.session_state.user, 'email', '') == 'demo@example.com'
                        else:
                            is_demo_mode = st.session_state.user.get('email', '') == 'demo@example.com'
                
                    if is_demo_mode:
                        st.info("🎯 Demo mode - Sign up to set up recurring income!")
                        return

                    # Get properties for the organization
                    try:
                        org_properties = db.get_properties_by_organization(selected_org_id)
                    
                        if org_properties:
                            st.markdown("---")

                            with st.form("recurring_income_form"):
                                col1, col2 = st.columns(2)
                            
                                with col1:
                                    # Property selection
                                    property_names = {prop.id: prop.name for prop in org_properties}
                                    selected_property_id = st.selectbox(
                                        "Property *",
                                        options=[prop.id for prop in org_properties],
                                        format_func=lambda x: property_names[x],
                                        key="recurring_income_property"
                                    )
                                
                                    # Income type
                                    income_type = st.selectbox(
                                        "Income Type *",
                                        [it.value for it in IncomeType],
                                        key="recurring_income_type"
                                    )
                                
                                    # Amount
                                    amount = st.number_input(
                                        "Amount *",
                                        min_value=0.01,
                                        step=0.01,
                                        format="%.2f",
                                        key="recurring_income_amount"
                                    )
                            
                                with col2:
                                    # Description
                                    description = st.text_input(
                                        "Description *",
                                        placeholder="e.g., Monthly Rent",
                                        key="recurring_income_description"
                                    )
                                
                                    # Interval
                                    from database.models import RecurringInterval
                                    interval = st.selectbox(
                                        "Recurring Interval *",
                                        [interval.value for interval in RecurringInterval],
                                        key="recurring_income_interval"
                                    )
                                
                                    # Start date
                                    start_date = st.date_input(
                                        "Start Date *",
                                        value=date.today(),
                                        key="recurring_income_start_date"
                                    )
                            
                                # End date (optional)
                                end_date = st.date_input(
                                    "End Date (Optional)",
                                    value=None,
                                    key="recurring_income_end_date"
                                )
                            
                                # Submit button
                                if st.form_submit_button("🔄 Create Recurring Income", type="primary"):
                                    if selected_property_id and income_type and amount and description and interval and start_date:
                                        try:
                                            # Create recurring transaction
                                            recurring_data = {
                                                "organization_id": selected_org_id,
                                                "property_id": selected_property_id,
                                                "transaction_type": "income",
                                                "income_type": income_type,
                                                "amount": amount,
                                                "description": description,
                                                "interval": interval,
                                                "start_date": start_date.isoformat(),
                                                "end_date": end_date.isoformat() if end_date else None,
                                                "is_active": True
                                            }
                                        
                                            result = db.client.table("recurring_transactions").insert(recurring_data).execute()
                                            if result.data:
                                                st.success("✅ Recurring income setup created successfully!")
                                                st.rerun()
                                            else:
                                                st.error("Failed to create recurring income setup. Please try again.")
                                        except Exception as e:
                                            st.error(f"Error creating recurring income: {str(e)}")
                                    else:
                                        st.error("Please fill in all required fields.")

                            st.markdown("---")

                            # Display existing recurring income
                            try:
                                recurring_income = db.client.table("recurring_transactions").select("*").eq("organization_id", selected_org_id).eq("transaction_type", "income").eq("is_active", True).execute()
                            
                                if recurring_income.data:
                                    for recurring in recurring_income.data:
                                        with st.expander(f"🔄 {recurring['description']} - {property_names.get(recurring['property_id'], 'Unknown Property')}"):
                                            col1, col2, col3 = st.columns(3)
                                        
                                            with col1:
                                                st.write(f"**Amount:** ${recurring['amount']:,.2f}")
                                                st.write(f"**Type:** {recurring['income_type'].title()}")
                                        
                                            with col2:
                                                st.write(f"**Interval:** {recurring['interval'].title()}")
                                                st.write(f"**Start:** {recurring['start_date']}")
                                        
                                            with col3:
                                                st.write(f"**End:** {recurring['end_date'] if recurring['end_date'] else 'No end date'}")
                                            
                                                # Action buttons
                                                action_col1, action_col2 = st.columns(2)
                                            
                                                with action_col1:
                                                    if st.button("✏️ Edit", key=f"edit_recurring_income_{recurring['id']}"):
                                                        st.session_state[f"editing_recurring_income_{recurring['id']}"] = True
                                                        st.rerun()
                                            
                                                with action_col2:
                                                    if st.button("🗑️ Delete", key=f"delete_recurring_income_{recurring['id']}", type="secondary"):
                                                        st.session_state[f"confirm_delete_recurring_income_{recurring['id']}"] = True
                                                        st.rerun()
                                        
                                            # Confirmation dialog for deletion
                                            if st.session_state.get(f"confirm_delete_recurring_income_{recurring['id']}", False):
                                                st.warning("⚠️ Are you sure you want to delete this recurring income setup?")
                                            
                                                confirm_col1, confirm_col2 = st.columns(2)
                                            
                                                with confirm_col1:
                                                    if st.button("✅ Yes, Delete", key=f"confirm_yes_recurring_income_{recurring['id']}", type="primary"):
                                                        try:
                                                            # Deactivate recurring transaction
                                                            db.client.table("recurring_transactions").update({"is_active": False}).eq("id", recurring['id']).execute()
                                                            st.success("Recurring income setup deleted successfully!")
                                                            if f"confirm_delete_recurring_income_{recurring['id']}" in st.session_state:
                                                                del st.session_state[f"confirm_delete_recurring_income_{recurring['id']}"]
                                                            st.rerun()
                                                        except Exception as e:
                                                            st.error(f"Error deleting recurring income: {str(e)}")
                                            
                                                with confirm_col2:
                                                    if st.button("❌ Cancel", key=f"confirm_no_recurring_income_{recurring['id']}"):
                                                        if f"confirm_delete_recurring_income_{recurring['id']}" in st.session_state:
                                                            del st.session_state[f"confirm_delete_recurring_income_{recurring['id']}"]
                                                        st.rerun()
                                        
                                            # Edit form
                                            if st.session_state.get(f"editing_recurring_income_{recurring['id']}", False):
                                                st.markdown("#### ✏️ Edit Recurring Income")
                                            
                                                with st.form(f"edit_recurring_income_form_{recurring['id']}"):
                                                    edit_col1, edit_col2 = st.columns(2)
                                                
                                                    with edit_col1:
                                                        edit_property_id = st.selectbox(
                                                            "Property",
                                                            options=[prop.id for prop in org_properties],
                                                            format_func=lambda x: property_names[x],
                                                            index=[prop.id for prop in org_properties].index(recurring['property_id']) if recurring['property_id'] in [prop.id for prop in org_properties] else 0,
                                                            key=f"edit_recurring_property_{recurring['id']}"
                                                        )
                                                        edit_amount = st.number_input("Amount", value=float(recurring['amount']), key=f"edit_recurring_amount_{recurring['id']}")
                                                        edit_type = st.selectbox("Income Type", [it.value for it in IncomeType], 
                                                                               index=[it.value for it in IncomeType].index(recurring['income_type']),
                                                                               key=f"edit_recurring_type_{recurring['id']}")
                                                
                                                    with edit_col2:
                                                        edit_description = st.text_input("Description", value=recurring['description'], key=f"edit_recurring_desc_{recurring['id']}")
                                                        edit_interval = st.selectbox("Interval", [interval.value for interval in RecurringInterval], 
                                                                                    index=[interval.value for interval in RecurringInterval].index(recurring['interval']),
                                                                                    key=f"edit_recurring_interval_{recurring['id']}")
                                                        edit_start_date = st.date_input("Start Date", value=datetime.fromisoformat(recurring['start_date']).date(), key=f"edit_recurring_start_{recurring['id']}")
                                                
                                                    edit_end_date = st.date_input("End Date (Optional)", value=datetime.fromisoformat(recurring['end_date']).date() if recurring['end_date'] else None, key=f"edit_recurring_end_{recurring['id']}")
                                                
                                                    edit_form_col1, edit_form_col2 = st.columns(2)
                                                
                                                    with edit_form_col1:
                                                        if st.form_submit_button("💾 Save Changes", type="primary"):
                                                            try:
                                                                update_data = {
                                                                    "property_id": edit_property_id,
                                                                    "amount": edit_amount,
                                                                    "income_type": edit_type,
                                                                    "description": edit_description,
                                                                    "interval": edit_interval,
                                                                    "start_date": edit_start_date.isoformat(),
                                                                    "end_date": edit_end_date.isoformat() if edit_end_date else None
                                                                }
                                                            
                                                                result = db.client.table("recurring_transactions").update(update_data).eq("id", recurring['id']).execute()
                                                                if result.data:
                                                                    st.success("Recurring income updated successfully!")
                                                                    if f"editing_recurring_income_{recurring['id']}" in st.session_state:
                                                                        del st.session_state[f"editing_recurring_income_{recurring['id']}"]
                                                                    st.rerun()
                                                                else:
                                                                    st.error("Failed to update recurring income. Please try again.")
                                                            except Exception as e:
                                                                st.error(f"Error updating recurring income: {str(e)}")
                                                
                                                    with edit_form_col2:
                                                        if st.form_submit_button("❌ Cancel"):
                                                            if f"editing_recurring_income_{recurring['id']}" in st.session_state:
                                                                del st.session_state[f"editing_recurring_income_{recurring['id']}"]
                                                            st.rerun()
                                else:
                                    st.info("No recurring income setups found. Create your first one above.")
                                
                            except Exception as e:
                                st.error(f"Error loading recurring income: {str(e)}")
                    
                        else:
                            st.info(f"No properties found for {org_name}. Please add a property first.")
                    
                    except Exception as e:
                        st.error(f"Error loading properties: {str(e)}")
            
                with tab4:  # Recurring Income - Pending Transactions
                    # Generate pending transactions button
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        if st.button("🔄 Generate Pending Transactions", help="Generate pending transactions from recurring income schedules"):
                            if 'selected_organization' in st.session_state:
                                generated = generate_pending_transactions_for_organization(st.session_state.selected_organization)
                                if generated > 0:
                                    st.success(f"Generated {generated} new pending transactions!")
                                else:
                                    st.info("No new pending transactions to generate.")
                            else:
                                st.error("Please select an organization first.")
                    with col2:
                        st.info("💡 Pending transactions are automatically generated from your recurring income schedules. Click the button to generate them manually.")
                
                    # Check if demo mode
                    is_demo_mode = False
                    if st.session_state.user:
                        if hasattr(st.session_state.user, 'email'):
                            is_demo_mode = getattr(st.session_state.user, 'email', '') == 'demo@example.com'
                        else:
                            is_demo_mode = st.session_state.user.get('email', '') == 'demo@example.com'
                
                    if is_demo_mode:
                        st.info("🎯 Demo mode - Sign up to view recurring income!")
                        return

                    # Date filter (default to current month)
                    col1, col2 = st.columns([2, 1])
                
                    with col1:
                        date_filter_type = st.selectbox(
                            "Date Filter",
                            ["Current Month", "All Time", "Custom Range", "Last 3 Months", "Last 6 Months", "Last Year"],
                            key="recurring_income_date_filter"
                        )
                
                    with col2:
                        if date_filter_type == "Custom Range":
                            start_date = st.date_input("Start Date", value=date.today().replace(day=1), key="recurring_income_start_date")
                            end_date = st.date_input("End Date", value=date.today(), key="recurring_income_end_date")
                        else:
                            start_date = None
                            end_date = None
                
                    # Get pending income transactions
                    try:
                        pending_income = db.client.table("pending_transactions").select("*").eq("organization_id", selected_org_id).eq("transaction_type", "income").eq("is_confirmed", False).execute()
                    
                        if pending_income.data:
                            # Apply date filter
                            filtered_pending = []
                            current_date = datetime.now()
                        
                            for pending in pending_income.data:
                                pending_date = datetime.fromisoformat(pending['transaction_date'].replace('Z', '+00:00'))
                            
                                if date_filter_type == "Current Month":
                                    if pending_date.year == current_date.year and pending_date.month == current_date.month:
                                        filtered_pending.append(pending)
                                elif date_filter_type == "This Year":
                                    if pending_date.year == current_date.year:
                                        filtered_pending.append(pending)
                                elif date_filter_type == "Last 3 Months":
                                    three_months_ago = current_date - timedelta(days=90)
                                    if pending_date >= three_months_ago:
                                        filtered_pending.append(pending)
                                elif date_filter_type == "Last 6 Months":
                                    six_months_ago = current_date - timedelta(days=180)
                                    if pending_date >= six_months_ago:
                                        filtered_pending.append(pending)
                                elif date_filter_type == "Last Year":
                                    one_year_ago = current_date - timedelta(days=365)
                                    if pending_date >= one_year_ago:
                                        filtered_pending.append(pending)
                                elif date_filter_type == "Custom Range" and start_date and end_date:
                                    if start_date <= pending_date.date() <= end_date:
                                        filtered_pending.append(pending)
                                elif date_filter_type == "All Time":
                                    filtered_pending.append(pending)
                        
                            st.markdown(f"**Found {len(filtered_pending)} pending income transactions**")
                        
                            # Display pending transactions
                            for pending in filtered_pending:
                                with st.container():
                                    st.markdown("---")
                                
                                    # Transaction header - adjusted columns for better spacing
                                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1.5])

                                    with col1:
                                        # Get property name
                                        try:
                                            prop = db.client.table("properties").select("name").eq("id", pending['property_id']).execute()
                                            prop_name = prop.data[0]['name'] if prop.data else "Unknown Property"
                                        except:
                                            prop_name = "Unknown Property"

                                        st.markdown(f"### 💰 {pending['income_type'].title()}")
                                        st.markdown(f"**Property:** {prop_name}")
                                        st.markdown(f"**Description:** {pending['description']}")

                                    with col2:
                                        st.markdown("**Amount**")
                                        st.markdown(f"${pending['amount']:,.2f}")

                                    with col3:
                                        st.markdown("**Date**")
                                        pending_date = datetime.fromisoformat(pending['transaction_date'].replace('Z', '+00:00'))
                                        st.markdown(pending_date.strftime('%Y-%m-%d'))

                                    with col4:
                                        st.markdown("**Actions**")
                                        # Wrapper to target action buttons with CSS
                                        st.markdown('<div class="pending-actions">', unsafe_allow_html=True)
                                        action_col1, action_col2, action_col3 = st.columns(3)
                                    
                                        with action_col1:
                                            if st.button("✏️ Edit", key=f"edit_pending_income_{pending['id']}"):
                                                st.session_state[f"editing_pending_income_{pending['id']}"] = True
                                                st.rerun()
                                    
                                        with action_col2:
                                            if st.button("🗑️ Delete", key=f"delete_pending_income_{pending['id']}", type="secondary"):
                                                st.session_state[f"confirm_delete_pending_income_{pending['id']}"] = True
                                                st.rerun()
                                    
                                        with action_col3:
                                            if st.button("✅ Confirm", key=f"confirm_pending_income_{pending['id']}", type="primary"):
                                                st.session_state[f"confirm_move_pending_income_{pending['id']}"] = True
                                                st.rerun()
                                        st.markdown('</div>', unsafe_allow_html=True)
                                
                                    # Confirmation dialog for deletion
                                    if st.session_state.get(f"confirm_delete_pending_income_{pending['id']}", False):
                                        st.warning("⚠️ Are you sure you want to delete this pending transaction?")
                                    
                                        confirm_col1, confirm_col2 = st.columns(2)
                                    
                                        with confirm_col1:
                                            if st.button("✅ Yes, Delete", key=f"confirm_yes_pending_income_{pending['id']}", type="primary"):
                                                try:
                                                    # Delete the pending transaction
                                                    db.client.table("pending_transactions").delete().eq("id", pending['id']).execute()
                                                    st.success("Pending transaction deleted successfully!")
                                                    if f"confirm_delete_pending_income_{pending['id']}" in st.session_state:
                                                        del st.session_state[f"confirm_delete_pending_income_{pending['id']}"]
                                                    st.rerun()
                                                except Exception as e:
                                                    st.error(f"Error deleting pending transaction: {str(e)}")
                                    
                                        with confirm_col2:
                                            if st.button("❌ Cancel", key=f"confirm_no_pending_income_{pending['id']}"):
                                                if f"confirm_delete_pending_income_{pending['id']}" in st.session_state:
                                                    del st.session_state[f"confirm_delete_pending_income_{pending['id']}"]
                                                st.rerun()
                                
                                    # Confirmation dialog for moving to regular transactions
                                    if st.session_state.get(f"confirm_move_pending_income_{pending['id']}", False):
                                        st.warning("⚠️ This will move this transaction to regular income records. Continue?")
                                    
                                        confirm_col1, confirm_col2 = st.columns(2)
                                    
                                        with confirm_col1:
                                            if st.button("✅ Yes, Move", key=f"confirm_yes_move_income_{pending['id']}", type="primary"):
                                                try:
                                                    # Move to regular income table
                                                    # Include user_id to satisfy RLS insert policy
                                                    current_user_id = None
                                                    try:
                                                        current_user_id = getattr(st.session_state.user, 'id', None)
                                                    except Exception:
                                                        try:
                                                            current_user_id = st.session_state.user.get('id', None)
                                                        except Exception:
                                                            current_user_id = None
                                                    income_data = {
                                                        "user_id": current_user_id,
                                                        "organization_id": pending['organization_id'],
                                                        "property_id": pending['property_id'],
                                                        "amount": pending['amount'],
                                                        "income_type": pending['income_type'],
                                                        "description": pending['description'],
                                                        "transaction_date": pending['transaction_date']
                                                    }
                                                
                                                    # Insert into income table
                                                    result = db.client.table("income").insert(income_data).execute()
                                                    if result.data:
                                                        # Delete from pending table
                                                        db.client.table("pending_transactions").delete().eq("id", pending['id']).execute()
                                                        st.success("Transaction confirmed and moved to regular income!")
                                                        if f"confirm_move_pending_income_{pending['id']}" in st.session_state:
                                                            del st.session_state[f"confirm_move_pending_income_{pending['id']}"]
                                                        st.rerun()
                                                    else:
                                                        st.error("Failed to move transaction. Please try again.")
                                                except Exception as e:
                                                    st.error(f"Error moving transaction: {str(e)}")
                                    
                                        with confirm_col2:
                                            if st.button("❌ Cancel", key=f"confirm_no_move_income_{pending['id']}"):
                                                if f"confirm_move_pending_income_{pending['id']}" in st.session_state:
                                                    del st.session_state[f"confirm_move_pending_income_{pending['id']}"]
                                                st.rerun()
                                
                                    # Edit form
                                    if st.session_state.get(f"editing_pending_income_{pending['id']}", False):
                                        st.markdown("#### ✏️ Edit Pending Transaction")
                                    
                                        with st.form(f"edit_pending_income_form_{pending['id']}"):
                                            edit_col1, edit_col2 = st.columns(2)
                                        
                                            with edit_col1:
                                                # Get properties for dropdown
                                                org_properties = db.get_properties_by_organization(selected_org_id)
                                                property_names = {prop.id: prop.name for prop in org_properties}
                                            
                                                edit_property_id = st.selectbox(
                                                    "Property",
                                                    options=[prop.id for prop in org_properties],
                                                    format_func=lambda x: property_names[x],
                                                    index=[prop.id for prop in org_properties].index(pending['property_id']) if pending['property_id'] in [prop.id for prop in org_properties] else 0,
                                                    key=f"edit_pending_property_{pending['id']}"
                                                )
                                                edit_amount = st.number_input("Amount", value=float(pending['amount']), key=f"edit_pending_amount_{pending['id']}")
                                                edit_type = st.selectbox("Income Type", [it.value for it in IncomeType], 
                                                                       index=[it.value for it in IncomeType].index(pending['income_type']),
                                                                       key=f"edit_pending_type_{pending['id']}")
                                        
                                            with edit_col2:
                                                edit_description = st.text_input("Description", value=pending['description'], key=f"edit_pending_desc_{pending['id']}")
                                                pending_date = datetime.fromisoformat(pending['transaction_date'].replace('Z', '+00:00'))
                                                edit_date = st.date_input("Transaction Date", value=pending_date.date(), key=f"edit_pending_date_{pending['id']}")
                                        
                                            edit_form_col1, edit_form_col2 = st.columns(2)
                                        
                                            with edit_form_col1:
                                                if st.form_submit_button("💾 Save Changes", type="primary"):
                                                    try:
                                                        update_data = {
                                                            "property_id": edit_property_id,
                                                            "amount": edit_amount,
                                                            "income_type": edit_type,
                                                            "description": edit_description,
                                                            "transaction_date": edit_date.isoformat()
                                                        }
                                                    
                                                        result = db.client.table("pending_transactions").update(update_data).eq("id", pending['id']).execute()
                                                        if result.data:
                                                            st.success("Pending transaction updated successfully!")
                                                            if f"editing_pending_income_{pending['id']}" in st.session_state:
                                                                del st.session_state[f"editing_pending_income_{pending['id']}"]
                                                            st.rerun()
                                                        else:
                                                            st.error("Failed to update pending transaction. Please try again.")
                                                    except Exception as e:
                                                        st.error(f"Error updating pending transaction: {str(e)}")
                                        
                                            with edit_form_col2:
                                                if st.form_submit_button("❌ Cancel"):
                                                    if f"editing_pending_income_{pending['id']}" in st.session_state:
                                                        del st.session_state[f"editing_pending_income_{pending['id']}"]
                                                    st.rerun()
                        
                            # Summary
                            total_pending = sum(pending['amount'] for pending in filtered_pending)
                            st.metric("Total Pending Income", f"${total_pending:,.2f}")
                        else:
                            st.info("No pending recurring income transactions found.")
                        
                    except Exception as e:
                        st.error(f"Error loading pending transactions: {str(e)}")
        
        with accounting_tabs[1]:  # Expenses
            # Check if demo mode
            is_demo_mode = False
            if st.session_state.user:
                if hasattr(st.session_state.user, 'email'):
                    is_demo_mode = getattr(st.session_state.user, 'email', '') == 'demo@example.com'
                else:
                    is_demo_mode = st.session_state.user.get('email', '') == 'demo@example.com'
        
            if is_demo_mode:
                # Demo mode - show sample expense data
                st.info("🎯 **Demo Mode** - Showing sample expense data. Sign up to manage your own expenses!")
            
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

            # Tabs for expense management
            tab1, tab2, tab3, tab4 = st.tabs(["View/Edit Expenses", "Add Expense", "Manage Expenses", "Recurring Expenses"])

            with tab1:
                if org_properties:
                    # Filter controls
                    col1, col2 = st.columns([2, 2])

                    with col1:
                        # Filter by property
                        property_names = {prop.id: prop.name for prop in org_properties}
                        selected_property_id = st.selectbox("Filter by Property", ["All"] + list(property_names.keys()),
                                                                   format_func=lambda x: "All" if x == "All" else property_names[x],
                                                                   key="expense_property_filter")

                    with col2:
                        # Date filter
                        date_filter_type = st.selectbox(
                            "Date Filter",
                            ["Current Month", "All Time", "Custom Range", "This Year", "Last 3 Months"],
                            key="expense_date_filter_type"
                        )

                    # Custom date range (only show if Custom Range is selected)
                    if date_filter_type == "Custom Range":
                        col3, col4 = st.columns(2)
                        with col3:
                            start_date = st.date_input(
                                "Start Date",
                                value=datetime.now().date() - timedelta(days=30),
                                key="expense_start_date"
                            )
                        with col4:
                            end_date = st.date_input(
                                "End Date",
                                value=datetime.now().date(),
                                key="expense_end_date"
                            )
                    else:
                        start_date = None
                        end_date = None

                    # Get expense records based on filters
                    if selected_property_id == "All":
                        expense_records = db.get_all_expenses()
                    else:
                        expense_records = db.get_expenses_by_property(selected_property_id)

                    # Apply date filter
                    if expense_records:
                        filtered_expense_records = []
                        current_date = datetime.now()

                        for record in expense_records:
                            record_date = record.transaction_date

                            if date_filter_type == "Current Month":
                                if record_date.year == current_date.year and record_date.month == current_date.month:
                                    filtered_expense_records.append(record)
                            elif date_filter_type == "This Year":
                                if record_date.year == current_date.year:
                                    filtered_expense_records.append(record)
                            elif date_filter_type == "Last 3 Months":
                                three_months_ago = current_date - timedelta(days=90)
                                if record_date >= three_months_ago:
                                    filtered_expense_records.append(record)
                            elif date_filter_type == "Custom Range" and start_date and end_date:
                                if start_date <= record_date.date() <= end_date:
                                    filtered_expense_records.append(record)
                            elif date_filter_type == "All Time":
                                filtered_expense_records.append(record)

                        expense_records = filtered_expense_records

                    if expense_records:
                        # Calculate total expenses
                        total_expenses = sum(exp.amount for exp in expense_records)

                        # Display total and count
                        st.markdown(f"### 💸 Total Expenses: ${total_expenses:,.2f}")
                        st.markdown(f"**Found {len(expense_records)} expense transactions**")
                        st.markdown("---")

                        # Display expense transactions with edit/delete buttons
                        for exp in expense_records:
                            with st.container():
                                    st.markdown("---")
                                
                                    # Expense header
                                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                                
                                    with col1:
                                        prop_name = property_names.get(exp.property_id, "Unknown Property")
                                        st.markdown(f"### 💸 {exp.expense_type.value.title()}")
                                        st.markdown(f"**Property:** {prop_name}")
                                        st.markdown(f"**Description:** {exp.description}")
                                
                                    with col2:
                                        st.markdown("**Amount**")
                                        st.markdown(f"${exp.amount:,.2f}")
                                
                                    with col3:
                                        st.markdown("**Date**")
                                        st.markdown(exp.transaction_date.strftime('%Y-%m-%d'))
                                
                                    with col4:
                                        st.markdown("**Actions**")
                                        action_col1, action_col2 = st.columns(2)
                                    
                                        with action_col1:
                                            if st.button("✏️ Edit", key=f"edit_expense_{exp.id}"):
                                                st.session_state[f"editing_expense_{exp.id}"] = True
                                                st.rerun()
                                    
                                        with action_col2:
                                            if st.button("🗑️ Delete", key=f"delete_expense_{exp.id}", type="secondary"):
                                                st.session_state[f"confirm_delete_expense_{exp.id}"] = True
                                                st.rerun()
                                
                                    # Confirmation dialog for deletion
                                    if st.session_state.get(f"confirm_delete_expense_{exp.id}", False):
                                        st.warning(f"⚠️ Are you sure you want to delete this expense transaction? This action cannot be undone!")
                                    
                                        confirm_col1, confirm_col2 = st.columns([1, 1])
                                    
                                        with confirm_col1:
                                            if st.button("✅ Yes, Delete", key=f"confirm_yes_expense_{exp.id}", type="primary"):
                                                try:
                                                    # Delete the expense record
                                                    success = db.client.table("expenses").delete().eq("id", exp.id).execute()
                                                    if success.data:
                                                        st.success("Expense transaction deleted successfully!")
                                                        # Clear the confirmation state
                                                        if f"confirm_delete_expense_{exp.id}" in st.session_state:
                                                            del st.session_state[f"confirm_delete_expense_{exp.id}"]
                                                        st.rerun()
                                                    else:
                                                        st.error("Failed to delete expense transaction. Please try again.")
                                                except Exception as e:
                                                    st.error(f"Error deleting expense transaction: {str(e)}")
                                    
                                        with confirm_col2:
                                            if st.button("❌ Cancel", key=f"confirm_no_expense_{exp.id}"):
                                                # Clear the confirmation state
                                                if f"confirm_delete_expense_{exp.id}" in st.session_state:
                                                    del st.session_state[f"confirm_delete_expense_{exp.id}"]
                                                st.rerun()
                                
                                    # Edit expense form
                                    if st.session_state.get(f"editing_expense_{exp.id}", False):
                                        st.markdown("#### ✏️ Edit Expense Transaction")
                                    
                                        with st.form(f"edit_expense_form_{exp.id}"):
                                            edit_col1, edit_col2 = st.columns(2)
                                        
                                            with edit_col1:
                                                edit_property_id = st.selectbox(
                                                    "Property",
                                                    options=[prop.id for prop in org_properties],
                                                    format_func=lambda x: property_names[x],
                                                    index=[prop.id for prop in org_properties].index(exp.property_id) if exp.property_id in [prop.id for prop in org_properties] else 0,
                                                    key=f"edit_expense_property_{exp.id}"
                                                )
                                                edit_amount = st.number_input("Amount", value=float(exp.amount), key=f"edit_expense_amount_{exp.id}")
                                                edit_type = st.selectbox("Expense Type", [et.value for et in ExpenseType], 
                                                                       index=[et.value for et in ExpenseType].index(exp.expense_type.value),
                                                                       key=f"edit_expense_type_{exp.id}")
                                        
                                            with edit_col2:
                                                edit_description = st.text_input("Description", value=exp.description, key=f"edit_expense_desc_{exp.id}")
                                                edit_date = st.date_input("Transaction Date", value=exp.transaction_date.date(), key=f"edit_expense_date_{exp.id}")
                                        
                                            edit_form_col1, edit_form_col2 = st.columns(2)
                                        
                                            with edit_form_col1:
                                                if st.form_submit_button("💾 Save Changes", type="primary"):
                                                    try:
                                                        # Update the expense record
                                                        update_data = {
                                                            "property_id": edit_property_id,
                                                            "amount": edit_amount,
                                                            "expense_type": edit_type,
                                                            "description": edit_description,
                                                            "transaction_date": edit_date.isoformat()
                                                        }
                                                    
                                                        result = db.client.table("expenses").update(update_data).eq("id", exp.id).execute()
                                                        if result.data:
                                                            st.success("Expense transaction updated successfully!")
                                                            # Clear the editing state
                                                            if f"editing_expense_{exp.id}" in st.session_state:
                                                                del st.session_state[f"editing_expense_{exp.id}"]
                                                            st.rerun()
                                                        else:
                                                            st.error("Failed to update expense transaction. Please try again.")
                                                    except Exception as e:
                                                        st.error(f"Error updating expense transaction: {str(e)}")
                                        
                                            with edit_form_col2:
                                                if st.form_submit_button("❌ Cancel"):
                                                    # Clear the editing state
                                                    if f"editing_expense_{exp.id}" in st.session_state:
                                                        del st.session_state[f"editing_expense_{exp.id}"]
                                                    st.rerun()
                    
                        # Expense summary
                        total_expenses = sum(exp.amount for exp in expense_records)
                        st.metric("Total Expenses", f"${total_expenses:,.2f}")
                    else:
                        st.info("No expense records found.")
                else:
                    st.info(f"No properties found for {org_name}. Please add a property first.")
        
            with tab2:
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
            
                with tab3:  # Manage Expenses - Recurring Expense Setup
                    # Check if demo mode
                    is_demo_mode = False
                    if st.session_state.user:
                        if hasattr(st.session_state.user, 'email'):
                            is_demo_mode = getattr(st.session_state.user, 'email', '') == 'demo@example.com'
                        else:
                            is_demo_mode = st.session_state.user.get('email', '') == 'demo@example.com'
                
                    if is_demo_mode:
                        st.info("🎯 Demo mode - Sign up to set up recurring expenses!")
                        return

                    # Get properties for the organization
                    try:
                        org_properties = db.get_properties_by_organization(selected_org_id)
                    
                        if org_properties:
                            st.markdown("---")

                            with st.form("recurring_expense_form"):
                                col1, col2 = st.columns(2)
                            
                                with col1:
                                    # Property selection
                                    property_names = {prop.id: prop.name for prop in org_properties}
                                    selected_property_id = st.selectbox(
                                        "Property *",
                                        options=[prop.id for prop in org_properties],
                                        format_func=lambda x: property_names[x],
                                        key="recurring_expense_property"
                                    )
                                
                                    # Expense type
                                    expense_type = st.selectbox(
                                        "Expense Type *",
                                        [et.value for et in ExpenseType],
                                        key="recurring_expense_type"
                                    )
                                
                                    # Amount
                                    amount = st.number_input(
                                        "Amount *",
                                        min_value=0.01,
                                        step=0.01,
                                        format="%.2f",
                                        key="recurring_expense_amount"
                                    )
                            
                                with col2:
                                    # Description
                                    description = st.text_input(
                                        "Description *",
                                        placeholder="e.g., Monthly HOA Fee",
                                        key="recurring_expense_description"
                                    )
                                
                                    # Interval
                                    from database.models import RecurringInterval
                                    interval = st.selectbox(
                                        "Recurring Interval *",
                                        [interval.value for interval in RecurringInterval],
                                        key="recurring_expense_interval"
                                    )
                                
                                    # Start date
                                    start_date = st.date_input(
                                        "Start Date *",
                                        value=date.today(),
                                        key="recurring_expense_start_date"
                                    )
                            
                                # End date (optional)
                                end_date = st.date_input(
                                    "End Date (Optional)",
                                    value=None,
                                    key="recurring_expense_end_date"
                                )
                            
                                # Submit button
                                if st.form_submit_button("🔄 Create Recurring Expense", type="primary"):
                                    if selected_property_id and expense_type and amount and description and interval and start_date:
                                        try:
                                            # Create recurring transaction
                                            recurring_data = {
                                                "organization_id": selected_org_id,
                                                "property_id": selected_property_id,
                                                "transaction_type": "expense",
                                                "expense_type": expense_type,
                                                "amount": amount,
                                                "description": description,
                                                "interval": interval,
                                                "start_date": start_date.isoformat(),
                                                "end_date": end_date.isoformat() if end_date else None,
                                                "is_active": True
                                            }
                                        
                                            result = db.client.table("recurring_transactions").insert(recurring_data).execute()
                                            if result.data:
                                                st.success("✅ Recurring expense setup created successfully!")
                                                st.rerun()
                                            else:
                                                st.error("Failed to create recurring expense setup. Please try again.")
                                        except Exception as e:
                                            st.error(f"Error creating recurring expense: {str(e)}")
                                    else:
                                        st.error("Please fill in all required fields.")

                            st.markdown("---")

                            # Display existing recurring expenses
                            try:
                                recurring_expenses = db.client.table("recurring_transactions").select("*").eq("organization_id", selected_org_id).eq("transaction_type", "expense").eq("is_active", True).execute()
                            
                                if recurring_expenses.data:
                                    for recurring in recurring_expenses.data:
                                        with st.expander(f"🔄 {recurring['description']} - {property_names.get(recurring['property_id'], 'Unknown Property')}"):
                                            col1, col2, col3 = st.columns(3)
                                        
                                            with col1:
                                                st.write(f"**Amount:** ${recurring['amount']:,.2f}")
                                                st.write(f"**Type:** {recurring['expense_type'].title()}")
                                        
                                            with col2:
                                                st.write(f"**Interval:** {recurring['interval'].title()}")
                                                st.write(f"**Start:** {recurring['start_date']}")
                                        
                                            with col3:
                                                st.write(f"**End:** {recurring['end_date'] if recurring['end_date'] else 'No end date'}")
                                            
                                                # Action buttons
                                                action_col1, action_col2 = st.columns(2)
                                            
                                                with action_col1:
                                                    if st.button("✏️ Edit", key=f"edit_recurring_expense_{recurring['id']}"):
                                                        st.session_state[f"editing_recurring_expense_{recurring['id']}"] = True
                                                        st.rerun()
                                            
                                                with action_col2:
                                                    if st.button("🗑️ Delete", key=f"delete_recurring_expense_{recurring['id']}", type="secondary"):
                                                        st.session_state[f"confirm_delete_recurring_expense_{recurring['id']}"] = True
                                                        st.rerun()
                                        
                                            # Confirmation dialog for deletion
                                            if st.session_state.get(f"confirm_delete_recurring_expense_{recurring['id']}", False):
                                                st.warning("⚠️ Are you sure you want to delete this recurring expense setup?")
                                            
                                                confirm_col1, confirm_col2 = st.columns(2)
                                            
                                                with confirm_col1:
                                                    if st.button("✅ Yes, Delete", key=f"confirm_yes_recurring_expense_{recurring['id']}", type="primary"):
                                                        try:
                                                            # Deactivate recurring transaction
                                                            db.client.table("recurring_transactions").update({"is_active": False}).eq("id", recurring['id']).execute()
                                                            st.success("Recurring expense setup deleted successfully!")
                                                            if f"confirm_delete_recurring_expense_{recurring['id']}" in st.session_state:
                                                                del st.session_state[f"confirm_delete_recurring_expense_{recurring['id']}"]
                                                            st.rerun()
                                                        except Exception as e:
                                                            st.error(f"Error deleting recurring expense: {str(e)}")
                                            
                                                with confirm_col2:
                                                    if st.button("❌ Cancel", key=f"confirm_no_recurring_expense_{recurring['id']}"):
                                                        if f"confirm_delete_recurring_expense_{recurring['id']}" in st.session_state:
                                                            del st.session_state[f"confirm_delete_recurring_expense_{recurring['id']}"]
                                                        st.rerun()
                                        
                                            # Edit form
                                            if st.session_state.get(f"editing_recurring_expense_{recurring['id']}", False):
                                                st.markdown("#### ✏️ Edit Recurring Expense")
                                            
                                                with st.form(f"edit_recurring_expense_form_{recurring['id']}"):
                                                    edit_col1, edit_col2 = st.columns(2)
                                                
                                                    with edit_col1:
                                                        edit_property_id = st.selectbox(
                                                            "Property",
                                                            options=[prop.id for prop in org_properties],
                                                            format_func=lambda x: property_names[x],
                                                            index=[prop.id for prop in org_properties].index(recurring['property_id']) if recurring['property_id'] in [prop.id for prop in org_properties] else 0,
                                                            key=f"edit_recurring_expense_property_{recurring['id']}"
                                                        )
                                                        edit_amount = st.number_input("Amount", value=float(recurring['amount']), key=f"edit_recurring_expense_amount_{recurring['id']}")
                                                        edit_type = st.selectbox("Expense Type", [et.value for et in ExpenseType], 
                                                                               index=[et.value for et in ExpenseType].index(recurring['expense_type']),
                                                                               key=f"edit_recurring_expense_type_{recurring['id']}")
                                                
                                                    with edit_col2:
                                                        edit_description = st.text_input("Description", value=recurring['description'], key=f"edit_recurring_expense_desc_{recurring['id']}")
                                                        edit_interval = st.selectbox("Interval", [interval.value for interval in RecurringInterval], 
                                                                                    index=[interval.value for interval in RecurringInterval].index(recurring['interval']),
                                                                                    key=f"edit_recurring_expense_interval_{recurring['id']}")
                                                        edit_start_date = st.date_input("Start Date", value=datetime.fromisoformat(recurring['start_date']).date(), key=f"edit_recurring_expense_start_{recurring['id']}")
                                                
                                                    edit_end_date = st.date_input("End Date (Optional)", value=datetime.fromisoformat(recurring['end_date']).date() if recurring['end_date'] else None, key=f"edit_recurring_expense_end_{recurring['id']}")
                                                
                                                    edit_form_col1, edit_form_col2 = st.columns(2)
                                                
                                                    with edit_form_col1:
                                                        if st.form_submit_button("💾 Save Changes", type="primary"):
                                                            try:
                                                                update_data = {
                                                                    "property_id": edit_property_id,
                                                                    "amount": edit_amount,
                                                                    "expense_type": edit_type,
                                                                    "description": edit_description,
                                                                    "interval": edit_interval,
                                                                    "start_date": edit_start_date.isoformat(),
                                                                    "end_date": edit_end_date.isoformat() if edit_end_date else None
                                                                }
                                                            
                                                                result = db.client.table("recurring_transactions").update(update_data).eq("id", recurring['id']).execute()
                                                                if result.data:
                                                                    st.success("Recurring expense updated successfully!")
                                                                    if f"editing_recurring_expense_{recurring['id']}" in st.session_state:
                                                                        del st.session_state[f"editing_recurring_expense_{recurring['id']}"]
                                                                    st.rerun()
                                                                else:
                                                                    st.error("Failed to update recurring expense. Please try again.")
                                                            except Exception as e:
                                                                st.error(f"Error updating recurring expense: {str(e)}")
                                                
                                                    with edit_form_col2:
                                                        if st.form_submit_button("❌ Cancel"):
                                                            if f"editing_recurring_expense_{recurring['id']}" in st.session_state:
                                                                del st.session_state[f"editing_recurring_expense_{recurring['id']}"]
                                                            st.rerun()
                                else:
                                    st.info("No recurring expense setups found. Create your first one above.")
                                
                            except Exception as e:
                                st.error(f"Error loading recurring expenses: {str(e)}")
                    
                        else:
                            st.info(f"No properties found for {org_name}. Please add a property first.")
                    
                    except Exception as e:
                        st.error(f"Error loading properties: {str(e)}")
            
                with tab4:  # Recurring Expenses - Pending Transactions
                    # Generate pending transactions button
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        if st.button("🔄 Generate Pending Transactions", key="generate_expense_pending", help="Generate pending transactions from recurring expense schedules"):
                            if 'selected_organization' in st.session_state:
                                generated = generate_pending_transactions_for_organization(st.session_state.selected_organization)
                                if generated > 0:
                                    st.success(f"Generated {generated} new pending transactions!")
                                else:
                                    st.info("No new pending transactions to generate.")
                            else:
                                st.error("Please select an organization first.")
                    with col2:
                        st.info("💡 Pending transactions are automatically generated from your recurring expense schedules. Click the button to generate them manually.")
                
                    # Check if demo mode
                    is_demo_mode = False
                    if st.session_state.user:
                        if hasattr(st.session_state.user, 'email'):
                            is_demo_mode = getattr(st.session_state.user, 'email', '') == 'demo@example.com'
                        else:
                            is_demo_mode = st.session_state.user.get('email', '') == 'demo@example.com'
                
                    if is_demo_mode:
                        st.info("🎯 Demo mode - Sign up to view recurring expenses!")
                        return

                    # Date filter (default to current month)
                    col1, col2 = st.columns([2, 1])
                
                    with col1:
                        date_filter_type = st.selectbox(
                            "Date Filter",
                            ["Current Month", "All Time", "Custom Range", "Last 3 Months", "Last 6 Months", "Last Year"],
                            key="recurring_expense_date_filter"
                        )
                
                    with col2:
                        if date_filter_type == "Custom Range":
                            start_date = st.date_input("Start Date", value=date.today().replace(day=1), key="recurring_expense_start_date")
                            end_date = st.date_input("End Date", value=date.today(), key="recurring_expense_end_date")
                        else:
                            start_date = None
                            end_date = None
                
                    # Get pending expense transactions
                    try:
                        pending_expenses = db.client.table("pending_transactions").select("*").eq("organization_id", selected_org_id).eq("transaction_type", "expense").eq("is_confirmed", False).execute()
                    
                        if pending_expenses.data:
                            # Apply date filter
                            filtered_pending = []
                            current_date = datetime.now()
                        
                            for pending in pending_expenses.data:
                                pending_date = datetime.fromisoformat(pending['transaction_date'].replace('Z', '+00:00'))
                            
                                if date_filter_type == "Current Month":
                                    if pending_date.year == current_date.year and pending_date.month == current_date.month:
                                        filtered_pending.append(pending)
                                elif date_filter_type == "This Year":
                                    if pending_date.year == current_date.year:
                                        filtered_pending.append(pending)
                                elif date_filter_type == "Last 3 Months":
                                    three_months_ago = current_date - timedelta(days=90)
                                    if pending_date >= three_months_ago:
                                        filtered_pending.append(pending)
                                elif date_filter_type == "Last 6 Months":
                                    six_months_ago = current_date - timedelta(days=180)
                                    if pending_date >= six_months_ago:
                                        filtered_pending.append(pending)
                                elif date_filter_type == "Last Year":
                                    one_year_ago = current_date - timedelta(days=365)
                                    if pending_date >= one_year_ago:
                                        filtered_pending.append(pending)
                                elif date_filter_type == "Custom Range" and start_date and end_date:
                                    if start_date <= pending_date.date() <= end_date:
                                        filtered_pending.append(pending)
                                elif date_filter_type == "All Time":
                                    filtered_pending.append(pending)
                        
                            st.markdown(f"**Found {len(filtered_pending)} pending expense transactions**")
                        
                            # Display pending transactions
                            for pending in filtered_pending:
                                with st.container():
                                    st.markdown("---")
                                
                                    # Transaction header
                                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                                
                                    with col1:
                                        # Get property name
                                        try:
                                            prop = db.client.table("properties").select("name").eq("id", pending['property_id']).execute()
                                            prop_name = prop.data[0]['name'] if prop.data else "Unknown Property"
                                        except:
                                            prop_name = "Unknown Property"
                                    
                                        st.markdown(f"### 💸 {pending['expense_type'].title()}")
                                        st.markdown(f"**Property:** {prop_name}")
                                        st.markdown(f"**Description:** {pending['description']}")
                                
                                    with col2:
                                        st.markdown("**Amount**")
                                        st.markdown(f"${pending['amount']:,.2f}")
                                
                                    with col3:
                                        st.markdown("**Date**")
                                        pending_date = datetime.fromisoformat(pending['transaction_date'].replace('Z', '+00:00'))
                                        st.markdown(pending_date.strftime('%Y-%m-%d'))
                                
                                    with col4:
                                        st.markdown("**Actions**")
                                        st.markdown('<div class="pending-actions">', unsafe_allow_html=True)
                                        action_col1, action_col2, action_col3 = st.columns([1,1,1])
                                    
                                        with action_col1:
                                            if st.button("✏️ Edit", key=f"edit_pending_expense_{pending['id']}"):
                                                st.session_state[f"editing_pending_expense_{pending['id']}"] = True
                                                st.rerun()
                                    
                                        with action_col2:
                                            if st.button("🗑️ Delete", key=f"delete_pending_expense_{pending['id']}", type="secondary"):
                                                st.session_state[f"confirm_delete_pending_expense_{pending['id']}"] = True
                                                st.rerun()
                                    
                                        with action_col3:
                                            if st.button("✅ Confirm", key=f"confirm_pending_expense_{pending['id']}", type="primary"):
                                                st.session_state[f"confirm_move_pending_expense_{pending['id']}"] = True
                                                st.rerun()
                                        st.markdown('</div>', unsafe_allow_html=True)
                                
                                    # Confirmation dialog for deletion
                                    if st.session_state.get(f"confirm_delete_pending_expense_{pending['id']}", False):
                                        st.warning("⚠️ Are you sure you want to delete this pending transaction?")
                                    
                                        confirm_col1, confirm_col2 = st.columns(2)
                                    
                                        with confirm_col1:
                                            if st.button("✅ Yes, Delete", key=f"confirm_yes_pending_expense_{pending['id']}", type="primary"):
                                                try:
                                                    # Delete the pending transaction
                                                    db.client.table("pending_transactions").delete().eq("id", pending['id']).execute()
                                                    st.success("Pending transaction deleted successfully!")
                                                    if f"confirm_delete_pending_expense_{pending['id']}" in st.session_state:
                                                        del st.session_state[f"confirm_delete_pending_expense_{pending['id']}"]
                                                    st.rerun()
                                                except Exception as e:
                                                    st.error(f"Error deleting pending transaction: {str(e)}")
                                    
                                        with confirm_col2:
                                            if st.button("❌ Cancel", key=f"confirm_no_pending_expense_{pending['id']}"):
                                                if f"confirm_delete_pending_expense_{pending['id']}" in st.session_state:
                                                    del st.session_state[f"confirm_delete_pending_expense_{pending['id']}"]
                                                st.rerun()
                                
                                    # Confirmation dialog for moving to regular transactions
                                    if st.session_state.get(f"confirm_move_pending_expense_{pending['id']}", False):
                                        st.warning("⚠️ This will move this transaction to regular expense records. Continue?")
                                    
                                        confirm_col1, confirm_col2 = st.columns(2)
                                    
                                        with confirm_col1:
                                            if st.button("✅ Yes, Move", key=f"confirm_yes_move_expense_{pending['id']}", type="primary"):
                                                try:
                                                    # Move to regular expense table
                                                    # Include user_id to satisfy RLS insert policy
                                                    current_user_id = None
                                                    try:
                                                        current_user_id = getattr(st.session_state.user, 'id', None)
                                                    except Exception:
                                                        try:
                                                            current_user_id = st.session_state.user.get('id', None)
                                                        except Exception:
                                                            current_user_id = None
                                                    expense_data = {
                                                        "user_id": current_user_id,
                                                        "organization_id": pending['organization_id'],
                                                        "property_id": pending['property_id'],
                                                        "amount": pending['amount'],
                                                        "expense_type": pending['expense_type'],
                                                        "description": pending['description'],
                                                        "transaction_date": pending['transaction_date']
                                                    }
                                                
                                                    # Insert into expense table
                                                    result = db.client.table("expenses").insert(expense_data).execute()
                                                    if result.data:
                                                        # Delete from pending table
                                                        db.client.table("pending_transactions").delete().eq("id", pending['id']).execute()
                                                        st.success("Transaction confirmed and moved to regular expenses!")
                                                        if f"confirm_move_pending_expense_{pending['id']}" in st.session_state:
                                                            del st.session_state[f"confirm_move_pending_expense_{pending['id']}"]
                                                        st.rerun()
                                                    else:
                                                        st.error("Failed to move transaction. Please try again.")
                                                except Exception as e:
                                                    st.error(f"Error moving transaction: {str(e)}")
                                    
                                        with confirm_col2:
                                            if st.button("❌ Cancel", key=f"confirm_no_move_expense_{pending['id']}"):
                                                if f"confirm_move_pending_expense_{pending['id']}" in st.session_state:
                                                    del st.session_state[f"confirm_move_pending_expense_{pending['id']}"]
                                                st.rerun()
                                
                                    # Edit form
                                    if st.session_state.get(f"editing_pending_expense_{pending['id']}", False):
                                        st.markdown("#### ✏️ Edit Pending Transaction")
                                    
                                        with st.form(f"edit_pending_expense_form_{pending['id']}"):
                                            edit_col1, edit_col2 = st.columns(2)
                                        
                                            with edit_col1:
                                                # Get properties for dropdown
                                                org_properties = db.get_properties_by_organization(selected_org_id)
                                                property_names = {prop.id: prop.name for prop in org_properties}
                                            
                                                edit_property_id = st.selectbox(
                                                    "Property",
                                                    options=[prop.id for prop in org_properties],
                                                    format_func=lambda x: property_names[x],
                                                    index=[prop.id for prop in org_properties].index(pending['property_id']) if pending['property_id'] in [prop.id for prop in org_properties] else 0,
                                                    key=f"edit_pending_expense_property_{pending['id']}"
                                                )
                                                edit_amount = st.number_input("Amount", value=float(pending['amount']), key=f"edit_pending_expense_amount_{pending['id']}")
                                                edit_type = st.selectbox("Expense Type", [et.value for et in ExpenseType], 
                                                                       index=[et.value for et in ExpenseType].index(pending['expense_type']),
                                                                       key=f"edit_pending_expense_type_{pending['id']}")
                                        
                                            with edit_col2:
                                                edit_description = st.text_input("Description", value=pending['description'], key=f"edit_pending_expense_desc_{pending['id']}")
                                                pending_date = datetime.fromisoformat(pending['transaction_date'].replace('Z', '+00:00'))
                                                edit_date = st.date_input("Transaction Date", value=pending_date.date(), key=f"edit_pending_expense_date_{pending['id']}")
                                        
                                            edit_form_col1, edit_form_col2 = st.columns(2)
                                        
                                            with edit_form_col1:
                                                if st.form_submit_button("💾 Save Changes", type="primary"):
                                                    try:
                                                        update_data = {
                                                            "property_id": edit_property_id,
                                                            "amount": edit_amount,
                                                            "expense_type": edit_type,
                                                            "description": edit_description,
                                                            "transaction_date": edit_date.isoformat()
                                                        }
                                                    
                                                        result = db.client.table("pending_transactions").update(update_data).eq("id", pending['id']).execute()
                                                        if result.data:
                                                            st.success("Pending transaction updated successfully!")
                                                            if f"editing_pending_expense_{pending['id']}" in st.session_state:
                                                                del st.session_state[f"editing_pending_expense_{pending['id']}"]
                                                            st.rerun()
                                                        else:
                                                            st.error("Failed to update pending transaction. Please try again.")
                                                    except Exception as e:
                                                        st.error(f"Error updating pending transaction: {str(e)}")
                                        
                                            with edit_form_col2:
                                                if st.form_submit_button("❌ Cancel"):
                                                    if f"editing_pending_expense_{pending['id']}" in st.session_state:
                                                        del st.session_state[f"editing_pending_expense_{pending['id']}"]
                                                    st.rerun()
                        
                            # Summary
                            total_pending = sum(pending['amount'] for pending in filtered_pending)
                            st.metric("Total Pending Expenses", f"${total_pending:,.2f}")
                        else:
                            st.info("No pending recurring expense transactions found.")
                        
                    except Exception as e:
                        st.error(f"Error loading pending transactions: {str(e)}")
    
    elif selected == "Budget Planner":
        # Check if demo mode
        is_demo_mode = False
        if st.session_state.user:
            if hasattr(st.session_state.user, 'email'):
                is_demo_mode = getattr(st.session_state.user, 'email', '') == 'demo@example.com'
            else:
                is_demo_mode = st.session_state.user.get('email', '') == 'demo@example.com'

        if is_demo_mode:
            st.info("🎯 **Demo Mode** - Showing sample budget data. Sign up to create and manage your own budgets!")

            # Demo budget tabs
            budget_tabs = st.tabs(["📈 Budget Analysis", "➕ Create Budget", "⚙️ Manage Budgets"])

            with budget_tabs[0]:
                st.markdown("### 📊 Sample Budget Analysis")
                st.write("**Monthly Budget for Downtown Apartment**")

                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("Total Budgeted", "$5,000")
                with col2:
                    st.metric("Total Spent", "$3,250")
                with col3:
                    st.metric("Remaining", "$1,750")
                with col4:
                    st.metric("Utilization", "65%")
                with col5:
                    st.metric("Status", "On Track", delta="Good")

                st.info("Sign up to see detailed budget analysis with charts and insights!")

            with budget_tabs[1]:
                st.markdown("### ➕ Create Sample Budget")
                st.write("In the full version, you can create budgets with:")
                st.write("• Monthly, Quarterly, or Yearly budgets")
                st.write("• Property-specific or organization-wide budgets")
                st.write("• Category-based expense tracking")
                st.info("Sign up to create real budgets!")

            with budget_tabs[2]:
                st.markdown("### ⚙️ Sample Budgets")
                st.write("**Active Budgets:**")
                st.write("• Downtown Apartment - Monthly: $5,000")
                st.write("• Suburban House - Monthly: $6,500")
                st.info("Sign up to manage your actual budgets!")
            return

        # Get current organization and properties
        selected_org_id = st.session_state.get('selected_organization')
        if not selected_org_id:
            st.warning("Please select an organization first.")
            return
        
        # Get organization name
        org = db.get_organization_by_id(selected_org_id)
        org_name = org.name if org else "Unknown Organization"
        
        # Get organization properties
        org_properties = db.get_properties_by_organization(selected_org_id)
        
        # Budget Planner sub-menu
        budget_tabs = st.tabs(["📈 Budget Analysis", "➕ Create Budget", "⚙️ Manage Budgets"])

        with budget_tabs[0]:  # Budget Analysis
            if org_properties:
                # Get all budgets for analysis
                budgets = db.get_budgets_by_organization(selected_org_id)

                if budgets:
                    # Budget selector and filters
                    col1, col2, col3 = st.columns([2, 1, 1])

                    with col1:
                        budget_options = {f"{b.name} ({b.period.title()})": b for b in budgets}
                        selected_budget_name = st.selectbox("Select Budget for Analysis", list(budget_options.keys()))

                    with col2:
                        analysis_period = st.selectbox("Analysis Period", ["Current Period", "Custom Range"], key="analysis_period")

                    with col3:
                        if analysis_period == "Custom Range":
                            custom_start = st.date_input("Start Date", value=date.today(), key="custom_analysis_start")
                            custom_end = st.date_input("End Date", value=date.today(), key="custom_analysis_end")
                        else:
                            custom_start = custom_end = None

                    if selected_budget_name:
                        selected_budget = budget_options[selected_budget_name]

                        # Determine analysis date range
                        if analysis_period == "Current Period":
                            analysis_start = selected_budget.start_date
                            analysis_end = selected_budget.end_date
                        else:
                            analysis_start = datetime.combine(custom_start, datetime.min.time())
                            analysis_end = datetime.combine(custom_end, datetime.max.time())

                        # Get budget analysis
                        try:
                            analysis = db.get_budget_analysis(selected_budget.id, analysis_start, analysis_end)
                        except Exception as e:
                            st.error(f"Error loading budget analysis: {str(e)}")
                            analysis = None

                        if analysis:
                            # Key Metrics Dashboard
                            st.markdown("### 📈 Key Metrics")
                            col1, col2, col3, col4, col5 = st.columns(5)

                            with col1:
                                st.metric("Total Budgeted", f"${analysis['total_budgeted']:,.2f}",
                                        delta=None, delta_color="normal")

                            with col2:
                                st.metric("Total Actual", f"${analysis['total_actual']:,.2f}",
                                        delta=f"{analysis['variance_percentage']:+.1f}%",
                                        delta_color="inverse" if analysis['is_over_budget'] else "normal")

                            with col3:
                                st.metric("Variance", f"${analysis['variance']:,.2f}",
                                        delta=f"{analysis['variance_percentage']:+.1f}%",
                                        delta_color="inverse" if analysis['is_over_budget'] else "normal")

                            with col4:
                                remaining_budget = analysis['total_budgeted'] - analysis['total_actual']
                                st.metric("Remaining Budget", f"${remaining_budget:,.2f}",
                                        delta=None, delta_color="normal")

                            with col5:
                                status = "Over Budget" if analysis['is_over_budget'] else "Under Budget"
                                st.metric("Status", status, delta=None, delta_color="normal")


                            # Budget Performance Summary with better layout
                            st.markdown("### 📋 Budget Performance Summary")

                            # Create two-column layout for better space utilization
                            col1, col2 = st.columns([1, 1])

                            with col1:
                                st.markdown("#### 💰 Financial Overview")
                                performance_data = {
                                    'Metric': [
                                        'Total Budget Allocated',
                                        'Actual Spending to Date',
                                        'Remaining Budget',
                                        'Budget Utilization',
                                        'Variance Amount',
                                        'Budget Status'
                                    ],
                                    'Value': [
                                        f"${analysis['total_budgeted']:,.2f}",
                                        f"${analysis['total_actual']:,.2f}",
                                        f"${analysis['total_budgeted'] - analysis['total_actual']:,.2f}",
                                        f"{(analysis['total_actual'] / analysis['total_budgeted'] * 100):.1f}%" if analysis['total_budgeted'] > 0 else "0%",
                                        f"${analysis['variance']:+,.2f}",
                                        '⚠️ Over Budget' if analysis['is_over_budget'] else '✅ On Track'
                                    ]
                                }

                                df_performance = pd.DataFrame(performance_data)
                                st.dataframe(df_performance, use_container_width=True, hide_index=True)

                            with col2:
                                st.markdown("#### 📊 Quick Insights")

                                # Calculate some quick insights
                                utilization_percent = (analysis['total_actual'] / analysis['total_budgeted'] * 100) if analysis['total_budgeted'] > 0 else 0
                                remaining_percent = 100 - utilization_percent

                                # Progress bar for budget utilization
                                st.markdown("**Budget Utilization Progress:**")
                                st.progress(utilization_percent / 100)
                                st.caption(f"{utilization_percent:.1f}% used, {remaining_percent:.1f}% remaining")

                                # Status indicators - compact layout
                                st.markdown("**Status Indicators:**")

                                # Create a container to reduce spacing
                                status_col1, status_col2 = st.columns(2)

                                with status_col1:
                                    if analysis['is_over_budget']:
                                        st.error(f"⚠️ **Over Budget by ${abs(analysis['variance']):,.2f}**")
                                    else:
                                        st.success(f"✅ **Under Budget by ${abs(analysis['variance']):,.2f}**")

                                    # Budget health
                                    if utilization_percent < 50:
                                        st.success("🟢 **Budget Health: Excellent**")
                                    elif utilization_percent < 80:
                                        st.warning("🟡 **Budget Health: Good**")
                                    else:
                                        st.error("🔴 **Budget Health: Needs Attention**")

                                with status_col2:
                                    # Spending rate
                                    if analysis['total_actual'] > 0:
                                        daily_average = analysis['total_actual'] / 30  # Assuming 30 days
                                        st.info(f"📈 **Daily Average Spending: ${daily_average:,.2f}**")

                            # Category Breakdown (if available)
                            if analysis['actual_by_category']:
                                st.markdown("### 🏷️ Spending by Category")

                                category_data = []
                                for category, amount in analysis['actual_by_category'].items():
                                    category_data.append({
                                        'Category': category.title(),
                                        'Amount': f"${amount:,.2f}",
                                        'Percentage': f"{(amount / analysis['total_actual'] * 100):.1f}%" if analysis['total_actual'] > 0 else "0%"
                                    })

                                if category_data:
                                    df_categories = pd.DataFrame(category_data)
                                    st.dataframe(df_categories, use_container_width=True, hide_index=True)

                                    # Category pie chart
                                    fig_pie = go.Figure(data=[go.Pie(
                                        labels=[item['Category'] for item in category_data],
                                        values=[float(item['Amount'].replace('$', '').replace(',', '')) for item in category_data],
                                        hole=0.3
                                    )])

                                    fig_pie.update_layout(
                                        title="Spending Distribution by Category",
                                        height=400
                                    )

                                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("No budgets available for analysis. Create a budget first.")
            else:
                st.info(f"No properties found for {org_name}. Please add a property first.")
        
        with budget_tabs[1]:  # Create Budget
            if org_properties:
                # Initialize session state for form
                if 'budget_period' not in st.session_state:
                    st.session_state.budget_period = "monthly"
                
                # Check if form was just submitted
                if 'budget_created' in st.session_state and st.session_state.budget_created:
                    st.success("✅ Budget created successfully!")
                    st.session_state.budget_created = False
                    st.rerun()
                
                with st.form("create_budget_form", clear_on_submit=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        budget_name = st.text_input("Budget Name", placeholder="e.g., Q1 2024 Maintenance Budget", key="budget_name")
                        budget_description = st.text_area("Description", placeholder="Optional description", key="budget_description")
                        budget_amount = st.number_input("Total Budget Amount", min_value=0.0, step=100.0, format="%.2f", key="budget_amount")
                    
                    with col2:
                        # Merged Property selection with "All Properties" option
                        property_options = ["All Properties"] + [f"{prop.name} ({prop.address})" for prop in org_properties]
                        selected_property_option = st.selectbox("Properties", property_options, key="selected_property")
                        
                        if selected_property_option == "All Properties":
                            budget_scope = "organization"
                            property_id = None
                        else:
                            budget_scope = "property"
                            # Find the selected property
                            selected_property = next((prop for prop in org_properties if f"{prop.name} ({prop.address})" == selected_property_option), None)
                            property_id = selected_property.id if selected_property else None
                        
                        budget_period = st.selectbox("Budget Period", ["monthly", "yearly", "custom"], 
                                                   format_func=lambda x: x.title(),
                                                   key="budget_period_select")
                    
                    # Date range selection based on period
                    current_date = datetime.now()
                    current_year = current_date.year
                    current_month = current_date.month
                    
                    st.markdown("### 📅 Date Range")
                    
                    if budget_period == "monthly":
                        # Show year and month for monthly budgets
                        col_year, col_month = st.columns(2)
                        with col_year:
                            budget_year = st.selectbox("Year", range(2020, 2030), index=current_year - 2020, key="monthly_year")
                        with col_month:
                            month_names = ["January", "February", "March", "April", "May", "June",
                                         "July", "August", "September", "October", "November", "December"]
                            budget_month = st.selectbox("Month", month_names, index=current_month - 1, key="monthly_month")
                            budget_month_num = month_names.index(budget_month) + 1  # Convert month name to number
                        start_date = datetime(budget_year, budget_month_num, 1)
                        # Get last day of the month
                        if budget_month_num == 12:
                            end_date = datetime(budget_year + 1, 1, 1) - timedelta(days=1)
                        else:
                            end_date = datetime(budget_year, budget_month_num + 1, 1) - timedelta(days=1)
                    elif budget_period == "yearly":
                        # Show only year for yearly budgets
                        budget_year = st.selectbox("Year", range(2020, 2030), index=current_year - 2020, key="yearly_year")
                        start_date = datetime(budget_year, 1, 1)
                        end_date = datetime(budget_year, 12, 31)
                    else:  # custom
                        # Show date range picker for custom budgets
                        col_start, col_end = st.columns(2)
                        with col_start:
                            start_date = st.date_input("Start Date", value=current_date.date(), key="custom_start")
                        with col_end:
                            end_date = st.date_input("End Date", value=current_date.date(), key="custom_end")
                        start_date = datetime.combine(start_date, datetime.min.time())
                        end_date = datetime.combine(end_date, datetime.max.time())
                    
                    # Display selected date range
                    if budget_period == "monthly":
                        month_names = ["January", "February", "March", "April", "May", "June",
                                     "July", "August", "September", "October", "November", "December"]
                        st.info(f"📅 **Selected Period:** {month_names[budget_month_num-1]} {budget_year}")
                    elif budget_period == "yearly":
                        st.info(f"📅 **Selected Period:** {budget_year} (Full Year)")
                    else:
                        st.info(f"📅 **Selected Period:** {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
                    
                    # Create Budget button
                    submitted = st.form_submit_button("Create Budget", type="primary", use_container_width=True)
                    
                    if submitted:
                        if budget_name and budget_amount > 0:
                            # Create budget
                            budget = Budget(
                                organization_id=selected_org_id,
                                property_id=property_id,
                                user_id=st.session_state.user.id,
                                name=budget_name,
                                description=budget_description,
                                budget_amount=budget_amount,
                                period=budget_period,
                                scope=budget_scope,
                                start_date=start_date,
                                end_date=end_date
                            )
                            
                            created_budget = db.create_budget(budget)
                            if created_budget:
                                st.session_state.budget_created = True
                                st.rerun()
                            else:
                                st.error("Failed to create budget. Please try again.")
                        else:
                            st.error("Please fill in all required fields.")
            else:
                st.info(f"No properties found for {org_name}. Please add a property first.")

        with budget_tabs[2]:  # Manage Budgets
            if org_properties:
                # Filter controls
                col1, col2, col3 = st.columns([2, 2, 2])
                
                with col1:
                    # Property filter
                    property_options = ["All Properties"] + [prop.name for prop in org_properties]
                    selected_property_filter = st.selectbox(
                        "Select Property",
                        property_options,
                        key="manage_budget_property_filter"
                    )
                
                with col2:
                    # Date range filter
                    date_filter_type = st.selectbox(
                        "Date Filter Type",
                        ["All Time", "Custom Range", "This Year", "This Month"],
                        key="manage_budget_date_filter_type"
                    )
                
                with col3:
                    # Custom date range (only show if Custom Range is selected)
                    if date_filter_type == "Custom Range":
                        start_date_filter = st.date_input(
                            "Start Date",
                            value=datetime.now().date() - timedelta(days=365),
                            key="manage_budget_start_date"
                        )
                        end_date_filter = st.date_input(
                            "End Date",
                            value=datetime.now().date(),
                            key="manage_budget_end_date"
                        )
                    else:
                        start_date_filter = None
                        end_date_filter = None
                
                # Get all budgets
                all_budgets = db.get_budgets_by_organization(selected_org_id)
                
                if all_budgets:
                    # Apply filters
                    filtered_budgets = []
                    
                    for budget in all_budgets:
                        # Property filter
                        if selected_property_filter != "All Properties":
                            if budget.property_id:
                                property_name = next((p.name for p in org_properties if p.id == budget.property_id), "Unknown Property")
                                if property_name != selected_property_filter:
                                    continue
                            else:
                                continue  # Organization-wide budget doesn't match property filter
                        elif budget.property_id is None and selected_property_filter != "All Properties":
                            continue  # Organization-wide budget when specific property is selected
                        
                        # Date filter
                        if date_filter_type == "All Time":
                            pass  # Include all budgets
                        elif date_filter_type == "This Year":
                            current_year = datetime.now().year
                            if budget.start_date.year != current_year:
                                continue
                        elif date_filter_type == "This Month":
                            current_date = datetime.now()
                            if budget.start_date.year != current_date.year or budget.start_date.month != current_date.month:
                                continue
                        elif date_filter_type == "Custom Range" and start_date_filter and end_date_filter:
                            budget_start = budget.start_date.date()
                            budget_end = budget.end_date.date()
                            if not (budget_start <= end_date_filter and budget_end >= start_date_filter):
                                continue
                        
                        filtered_budgets.append(budget)
                    
                    # Display filtered budgets
                    if filtered_budgets:
                        st.markdown(f"### 📋 Found {len(filtered_budgets)} Budget(s)")
                        
                        for budget in filtered_budgets:
                            with st.expander(f"📋 {budget.name} - {budget.period.title()}", expanded=False):
                                col1, col2, col3 = st.columns([2, 2, 1])
                                
                                with col1:
                                    st.write(f"**Amount:** ${budget.budget_amount:,.2f}")
                                    st.write(f"**Period:** {budget.start_date.strftime('%Y-%m-%d')} to {budget.end_date.strftime('%Y-%m-%d')}")
                                    st.write(f"**Scope:** {budget.scope.title()}")
                                
                                with col2:
                                    if budget.property_id:
                                        property_name = next((p.name for p in org_properties if p.id == budget.property_id), "Unknown Property")
                                        st.write(f"**Property:** {property_name}")
                                    else:
                                        st.write(f"**Property:** All Properties")
                                    
                                    # Show budget status
                                    analysis = db.get_budget_analysis(budget.id, budget.start_date, budget.end_date)
                                    if analysis:
                                        status_color = "🔴" if analysis['is_over_budget'] else "🟢"
                                        utilization = (analysis['total_actual'] / analysis['total_budgeted'] * 100) if analysis['total_budgeted'] > 0 else 0
                                        st.write(f"**Status:** {status_color} {utilization:.1f}% utilized")
                                        st.write(f"**Actual:** ${analysis['total_actual']:,.2f} / ${analysis['total_budgeted']:,.2f}")
                                
                                with col3:
                                    if st.button(f"🗑️ Delete", key=f"delete_budget_{budget.id}", type="secondary"):
                                        if db.delete_budget(budget.id):
                                            st.success("Budget deleted successfully!")
                                            st.rerun()
                                        else:
                                            st.error("Failed to delete budget.")
                                    
                                    if st.button(f"✏️ Edit", key=f"edit_budget_{budget.id}", type="primary"):
                                        st.session_state[f"edit_budget_{budget.id}"] = True
                                        st.rerun()
                        
                        # Summary statistics
                        if len(filtered_budgets) > 1:
                            st.markdown("### 📊 Summary Statistics")
                            
                            total_budgeted = sum(budget.budget_amount for budget in filtered_budgets)
                            total_actual = 0
                            over_budget_count = 0
                            
                            for budget in filtered_budgets:
                                analysis = db.get_budget_analysis(budget.id, budget.start_date, budget.end_date)
                                if analysis:
                                    total_actual += analysis['total_actual']
                                    if analysis['is_over_budget']:
                                        over_budget_count += 1
                            
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("Total Budgets", len(filtered_budgets))
                            
                            with col2:
                                st.metric("Total Budgeted", f"${total_budgeted:,.2f}")
                            
                            with col3:
                                st.metric("Total Actual", f"${total_actual:,.2f}")
                            
                            with col4:
                                st.metric("Over Budget", f"{over_budget_count}")
                    else:
                        st.info("No budgets match the selected filter criteria.")
                else:
                    st.info("No budgets to manage. Create a budget first.")
            else:
                st.info(f"No properties found for {org_name}. Please add a property first.")
    
    elif selected == "Analytics":
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
                st.info("🎯 **Demo Mode** - Showing sample analytics data. Sign up to see your own analytics!")
                
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
                st.info("🎯 **Demo Mode** - Showing sample analytics data")
                
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
            
            # Real analytics for selected organization
            # Fetch data
            income_result = db.supabase.table("income").select("*").eq("organization_id", selected_org_id).order("transaction_date").execute()
            expense_result = db.supabase.table("expenses").select("*").eq("organization_id", selected_org_id).order("transaction_date").execute()
            properties_result = db.supabase.table("properties").select("*").eq("organization_id", selected_org_id).execute()

            income_rows = income_result.data or []
            expense_rows = expense_result.data or []
            properties = properties_result.data or []

            inc_df = pd.DataFrame(income_rows)
            exp_df = pd.DataFrame(expense_rows)

            if inc_df.empty and exp_df.empty:
                st.info("No financial data found for this organization.")
                return

            # Calculate metrics
            total_income = float(inc_df['amount'].sum()) if not inc_df.empty else 0.0
            total_expenses = float(exp_df['amount'].sum()) if not exp_df.empty else 0.0
            net_profit = total_income - total_expenses

            # Calculate deltas (compare current month to previous month)
            current_month = datetime.now().strftime('%Y-%m')
            prev_month = (datetime.now().replace(day=1) - timedelta(days=1)).strftime('%Y-%m')

            # Current month income/expenses
            current_income = float(inc_df[inc_df['transaction_date'].str.startswith(current_month)]['amount'].sum()) if not inc_df.empty else 0.0
            current_expenses = float(exp_df[exp_df['transaction_date'].str.startswith(current_month)]['amount'].sum()) if not exp_df.empty else 0.0

            # Previous month income/expenses
            prev_income = float(inc_df[inc_df['transaction_date'].str.startswith(prev_month)]['amount'].sum()) if not inc_df.empty else 0.0
            prev_expenses = float(exp_df[exp_df['transaction_date'].str.startswith(prev_month)]['amount'].sum()) if not exp_df.empty else 0.0

            # Calculate percentage changes
            income_delta = ((current_income - prev_income) / prev_income * 100) if prev_income > 0 else 0
            expense_delta = ((current_expenses - prev_expenses) / prev_expenses * 100) if prev_expenses > 0 else 0

            prev_net = prev_income - prev_expenses
            current_net = current_income - current_expenses
            net_delta = ((current_net - prev_net) / prev_net * 100) if prev_net != 0 else 0

            # Financial Overview - 4 metrics in a row
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Properties", len(properties))
            with col2:
                st.metric("Monthly Revenue", f"${current_income:,.2f}", f"{income_delta:.1f}%")
            with col3:
                st.metric("Total Expenses", f"${current_expenses:,.2f}", f"{expense_delta:.1f}%")
            with col4:
                st.metric("Net Profit", f"${net_profit:,.2f}", f"{net_delta:.1f}%")

            st.markdown("---")

            # Charts in two columns
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📈 Revenue Trend")
                # Group income by date for revenue trend
                if not inc_df.empty:
                    inc_df['date'] = pd.to_datetime(inc_df['transaction_date'])
                    daily_income = inc_df.groupby('date')['amount'].sum().reset_index()

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=daily_income['date'],
                        y=daily_income['amount'],
                        mode='lines+markers',
                        name='Revenue',
                        line=dict(color='#2E8B57')
                    ))
                    fig.update_layout(title="Revenue Trend", xaxis_title="Date", yaxis_title="Revenue ($)")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No income data available for revenue trend.")

            with col2:
                st.subheader("🏠 Property Performance")
                # Property-wise income vs expenses
                if properties:
                    property_names = []
                    property_income = []
                    property_expenses = []

                    for prop in properties:
                        property_names.append(prop.get('name', 'Unknown'))
                        prop_id = prop.get('id')

                        # Get income for this property
                        prop_inc = float(inc_df[inc_df['property_id'] == prop_id]['amount'].sum()) if not inc_df.empty and 'property_id' in inc_df.columns else 0.0
                        property_income.append(prop_inc)

                        # Get expenses for this property
                        prop_exp = float(exp_df[exp_df['property_id'] == prop_id]['amount'].sum()) if not exp_df.empty and 'property_id' in exp_df.columns else 0.0
                        property_expenses.append(prop_exp)

                    fig = go.Figure()
                    fig.add_trace(go.Bar(name='Income', x=property_names, y=property_income, marker_color='#2E8B57'))
                    fig.add_trace(go.Bar(name='Expenses', x=property_names, y=property_expenses, marker_color='#DC143C'))
                    fig.update_layout(title="Property Income vs Expenses", barmode='group')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No properties found.")

            # Expense Breakdown
            st.subheader("💰 Expense Breakdown")
            col1, col2 = st.columns(2)

            with col1:
                # Pie chart for expense categories
                if not exp_df.empty and 'expense_type' in exp_df.columns:
                    exp_cat = exp_df.groupby('expense_type')['amount'].sum().reset_index()

                    fig = go.Figure(data=[go.Pie(
                        labels=exp_cat['expense_type'],
                        values=exp_cat['amount'],
                        hole=0.3
                    )])
                    fig.update_layout(title="Expense Categories")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No expense data available for category breakdown.")

            with col2:
                # Monthly expense trend
                if not exp_df.empty:
                    exp_df['month'] = exp_df['transaction_date'].apply(lambda x: str(x)[:7])
                    monthly_exp = exp_df.groupby('month')['amount'].sum().reset_index()

                    # Convert month to short format (Jan, Feb, etc.)
                    monthly_exp['month_label'] = monthly_exp['month'].apply(
                        lambda x: datetime.strptime(x + '-01', '%Y-%m-%d').strftime('%b')
                    )

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=monthly_exp['month_label'],
                        y=monthly_exp['amount'],
                        mode='lines+markers',
                        name='Monthly Expenses',
                        line=dict(color='#DC143C')
                    ))
                    fig.update_layout(title="Monthly Expense Trend", xaxis_title="Month", yaxis_title="Expenses ($)")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No expense data available for monthly trend.")
            
            return
        except UnboundLocalError as e:
            st.error("Analytics error: please refresh the page. If it persists, reselect your organization.")
        except Exception as e:
            st.error(f"Analytics error: {str(e)}")
    
    elif selected == "Reminders":
        # Check if demo mode
        is_demo_mode = False
        if st.session_state.user:
            if hasattr(st.session_state.user, 'email'):
                is_demo_mode = getattr(st.session_state.user, 'email', '') == 'demo@example.com'
            else:
                is_demo_mode = st.session_state.user.get('email', '') == 'demo@example.com'
        
        if is_demo_mode:
            # Demo mode - show sample rent reminder data
            st.info("🎯 **Demo Mode** - Showing sample rent reminder data. Sign up to manage your own reminders!")
            
            # Demo reminders
            st.markdown("### Sample Reminders")
            
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
                st.error("❌ **Reminders table not found in database!**")
                st.markdown("""
                **To set up the Reminders feature, you need to:**
                
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

        # Create monthly reminders button
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if st.button("🔄 Create Monthly Reminders", type="primary"):
                with st.spinner("Creating reminders for all properties..."):
                    # Get user ID from session state user object
                    user_id = None
                    if st.session_state.user:
                        if hasattr(st.session_state.user, 'id'):
                            user_id = st.session_state.user.id
                        elif isinstance(st.session_state.user, dict):
                            user_id = st.session_state.user.get('id')
                    
                    if not user_id:
                        st.error("Unable to get user ID. Please log out and log back in.")
                        return
                    
                    created_count = reminder_service.create_monthly_reminders(
                        selected_org_id, user_id
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
        # Get selected organization for all reports
        selected_org_id = st.session_state.get('selected_organization')
        if not selected_org_id:
            st.error("Please select an organization first.")
            return

        # Create tabs for Reports
        report_tabs = st.tabs(["📊 P&L", "📑 Transactions", "🏠 Properties Performance"])

        with report_tabs[0]:
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
                st.info("🎯 **Demo Mode** - Showing sample reports with sample data")
                
                # Demo P&L Report
                st.markdown("### 📈 Profit & Loss Report (Demo)")
                
                # Demo report type selection
                demo_report_type = st.selectbox("Report Type", ["Yearly", "Monthly", "Custom"], key="demo_report_type")
                if demo_report_type == "Yearly":
                    st.selectbox("Select Year", options=list(range(2020, date.today().year + 2)), index=date.today().year - 2020, key="demo_year_selector")
                elif demo_report_type == "Monthly":
                    current_year = date.today().year
                    month_options = [
                        f"January {current_year}", f"February {current_year}", f"March {current_year}",
                        f"April {current_year}", f"May {current_year}", f"June {current_year}",
                        f"July {current_year}", f"August {current_year}", f"September {current_year}",
                        f"October {current_year}", f"November {current_year}", f"December {current_year}"
                    ]
                    st.selectbox("Select Month", options=month_options, index=date.today().month - 1, key="demo_month_selector")
                else:
                    st.date_input("Start Date", value=date.today().replace(day=1), key="demo_custom_start")
                    st.date_input("End Date", value=date.today(), key="demo_custom_end")
                
                # Demo data and charts
                demo_data = {
                    'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    'Revenue': [2500, 2300, 2800, 2200, 2500, 2400],
                    'Expenses': [1800, 1900, 1750, 2000, 1850, 1950],
                    'Net Income': [700, 600, 750, 500, 650, 550]
                }
                from plotly.subplots import make_subplots
                fig = make_subplots(rows=2, cols=1, subplot_titles=('Monthly Revenue vs Expenses', 'Monthly Net Income'), vertical_spacing=0.1)
                fig.add_trace(go.Bar(name='Revenue', x=demo_data['Month'], y=demo_data['Revenue'], marker_color='#2E8B57'), row=1, col=1)
                fig.add_trace(go.Bar(name='Expenses', x=demo_data['Month'], y=demo_data['Expenses'], marker_color='#DC143C'), row=1, col=1)
                fig.add_trace(go.Bar(name='Net Income', x=demo_data['Month'], y=demo_data['Net Income'], marker_color='#4169E1'), row=2, col=1)
                fig.update_layout(height=600, showlegend=True, title_text="Demo P&L Report")
                st.plotly_chart(fig, use_container_width=True)
                m1, m2, m3 = st.columns(3)
                with m1: st.metric("Total Revenue", "$15,000", "5.2%")
                with m2: st.metric("Total Expenses", "$11,250", "3.1%")
                with m3: st.metric("Net Profit", "$3,750", "8.3%")
            else:
                # Real P&L Report
                st.markdown("### 📈 Profit & Loss Report")
                
                # Get selected organization
                if 'selected_organization' in st.session_state and st.session_state.selected_organization:
                    selected_org_id = st.session_state.selected_organization
                    org_name = st.session_state.get('selected_org_name')
                    if not org_name:
                        try:
                            org_obj = db.get_organization_by_id(selected_org_id)
                            org_name = org_obj.name if org_obj else 'Unknown Organization'
                        except Exception:
                            org_name = 'Unknown Organization'
                    
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
                            period_text = f"Year: {selected_year}"
                        elif report_type == "Monthly":
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
                            month_number = month_options.index(selected_month) + 1
                            start_date = date(current_year, month_number, 1)
                            end_date = date(current_year + 1, 1, 1) if month_number == 12 else date(current_year, month_number + 1, 1)
                            period_text = f"Month: {selected_month}"
                        else:  # Custom
                            col_start, col_end = st.columns(2)
                            with col_start:
                                start_date = st.date_input("Start Date", value=date.today().replace(day=1), key="custom_start")
                            with col_end:
                                end_date = st.date_input("End Date", value=date.today(), key="custom_end")
                            period_text = f"Period: {start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}"
                    
                    # Generate P&L Report
                    # Generate P&L Report + Downloads row
                    col_gen, col_pdf, col_xls = st.columns([2,1,1])
                    with col_gen:
                        generate_clicked = st.button("Generate P&L Report", key="generate_pl")
                    with col_pdf:
                        download_pdf_clicked = st.button("📄 Download PDF", key="download_pl_pdf")
                    with col_xls:
                        download_xls_clicked = st.button("📊 Download Excel", key="download_pl_xls")

                    # Auto-trigger report generation once on first load of Reports
                    auto_trigger = False
                    if 'pl_auto_generated' not in st.session_state:
                        st.session_state.pl_auto_generated = False
                    if not st.session_state.pl_auto_generated:
                        auto_trigger = True
                        st.session_state.pl_auto_generated = True

                    if generate_clicked or download_pdf_clicked or download_xls_clicked or auto_trigger:
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
                            
                            org_title = org_name if org_name else "Organization"
                            # Determine friendly period text
                            if report_type == "Yearly":
                                period_text = f"Year: {selected_year}"
                            elif report_type == "Monthly":
                                period_text = f"Month: {selected_month}"
                            else:
                                period_text = f"Period: {start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}"

                            if income_result.data or expense_result.data:
                                # Calculate totals
                                total_income = sum(float(item.get('amount', 0)) for item in income_result.data)
                                total_expenses = sum(float(item.get('amount', 0)) for item in expense_result.data)
                                net_profit = total_income - total_expenses

                                # Show heading with org + period
                                st.markdown(f"### 📈 {org_title} P&L — {period_text}")

                                # Summary metrics
                                m1, m2, m3 = st.columns(3)
                                with m1:
                                    st.metric("Total Income", f"${total_income:,.2f}")
                                with m2:
                                    st.metric("Total Expenses", f"${total_expenses:,.2f}")
                                with m3:
                                    margin = (net_profit / total_income * 100) if total_income else 0
                                    st.metric("Net Profit", f"${net_profit:,.2f}", f"{margin:.1f}%")

                                # Charts
                                from plotly.subplots import make_subplots
                                
                                # Build monthly trend if Yearly report
                                if report_type == "Yearly":
                                    def to_month(row):
                                        return str(row.get('transaction_date', '') or '')[:7]
                                    income_df = pd.DataFrame(income_result.data)
                                    expense_df = pd.DataFrame(expense_result.data)
                                    income_monthly = income_df.assign(month=income_df.apply(to_month, axis=1)).groupby('month')['amount'].sum() if not income_df.empty else pd.Series(dtype=float)
                                    expense_monthly = expense_df.assign(month=expense_df.apply(to_month, axis=1)).groupby('month')['amount'].sum() if not expense_df.empty else pd.Series(dtype=float)
                                    months = sorted(set(income_monthly.index).union(expense_monthly.index))
                                    y_income = [float(income_monthly.get(m, 0)) for m in months]
                                    y_exp = [float(expense_monthly.get(m, 0)) for m in months]
                                    fig = make_subplots(rows=1, cols=1)
                                    fig.add_trace(go.Scatter(x=months, y=y_income, mode='lines+markers', name='Income', line=dict(color='#2E8B57')))
                                    fig.add_trace(go.Scatter(x=months, y=y_exp, mode='lines+markers', name='Expenses', line=dict(color='#DC143C')))
                                    fig.update_layout(title_text="Monthly P&L Trend", height=400)
                                    st.plotly_chart(fig, use_container_width=True)

                                # Category breakdown pies
                                if income_result.data:
                                    inc_df = pd.DataFrame(income_result.data)
                                    inc_by_cat = inc_df.groupby('income_type')['amount'].sum().reset_index() if 'income_type' in inc_df.columns else pd.DataFrame()
                                else:
                                    inc_by_cat = pd.DataFrame()
                                if expense_result.data:
                                    exp_df = pd.DataFrame(expense_result.data)
                                    exp_by_cat = exp_df.groupby('expense_type')['amount'].sum().reset_index() if 'expense_type' in exp_df.columns else pd.DataFrame()
                                else:
                                    exp_by_cat = pd.DataFrame()
                                c1, c2 = st.columns(2)
                                if not inc_by_cat.empty:
                                    c1.plotly_chart(go.Figure(data=[go.Pie(labels=inc_by_cat['income_type'], values=inc_by_cat['amount'])]).update_layout(title_text="Income by Type"), use_container_width=True)
                                if not exp_by_cat.empty:
                                    c2.plotly_chart(go.Figure(data=[go.Pie(labels=exp_by_cat['expense_type'], values=exp_by_cat['amount'])]).update_layout(title_text="Expenses by Type"), use_container_width=True)

                                # If download was clicked, return files
                                if download_pdf_clicked:
                                    from reportlab.lib.pagesizes import letter
                                    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
                                    from reportlab.platypus import Image as RLImage
                                    from reportlab.lib.styles import getSampleStyleSheet
                                    from reportlab.lib import colors
                                    import io, base64
                                    buffer = io.BytesIO()
                                    doc = SimpleDocTemplate(buffer, pagesize=letter)
                                    styles = getSampleStyleSheet()
                                    story = []
                                    story.append(Paragraph(f"{org_title} P&L — {period_text}", styles['Title']))
                                    story.append(Spacer(1, 12))
                                    summary_data = [
                                        ['Metric', 'Amount'],
                                        ['Total Income', f"${total_income:,.2f}"],
                                        ['Total Expenses', f"${total_expenses:,.2f}"],
                                        ['Net Profit', f"${net_profit:,.2f}"]
                                    ]
                                    t = Table(summary_data)
                                    t.setStyle(TableStyle([
                                        ('BACKGROUND', (0,0), (-1,0), colors.grey),
                                        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                                        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                                        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                                        ('GRID', (0,0), (-1,-1), 1, colors.black)
                                    ]))
                                    story.append(t)
                                    story.append(Spacer(1, 16))

                                    # Try to embed the same charts as images
                                    try:
                                        import plotly.io as pio
                                        # Rebuild dataframes for this run
                                        income_df = pd.DataFrame(income_result.data)
                                        expense_df = pd.DataFrame(expense_result.data)

                                        # Monthly trend (only for Yearly and when data present)
                                        if report_type == "Yearly" and (not income_df.empty or not expense_df.empty):
                                            def to_month_str(ts):
                                                return str(ts)[:7]
                                            if not income_df.empty:
                                                income_df['month'] = income_df['transaction_date'].map(to_month_str)
                                                income_monthly = income_df.groupby('month')['amount'].sum()
                                            else:
                                                income_monthly = pd.Series(dtype=float)
                                            if not expense_df.empty:
                                                expense_df['month'] = expense_df['transaction_date'].map(to_month_str)
                                                expense_monthly = expense_df.groupby('month')['amount'].sum()
                                            else:
                                                expense_monthly = pd.Series(dtype=float)
                                            months = sorted(set(income_monthly.index).union(expense_monthly.index))
                                            y_income = [float(income_monthly.get(m, 0)) for m in months]
                                            y_exp = [float(expense_monthly.get(m, 0)) for m in months]
                                            trend_fig = make_subplots(rows=1, cols=1)
                                            trend_fig.add_trace(go.Scatter(x=months, y=y_income, mode='lines+markers', name='Income', line=dict(color='#2E8B57')))
                                            trend_fig.add_trace(go.Scatter(x=months, y=y_exp, mode='lines+markers', name='Expenses', line=dict(color='#DC143C')))
                                            trend_fig.update_layout(title_text="Monthly P&L Trend", height=400, width=700, margin=dict(l=20,r=20,t=40,b=20))
                                            img_bytes = pio.to_image(trend_fig, format='png', width=700, height=400)
                                            story.append(RLImage(io.BytesIO(img_bytes), width=500, height=285))
                                            story.append(Spacer(1, 12))

                                        # Income pie
                                        if not income_df.empty and 'income_type' in income_df.columns:
                                            inc_by_cat = income_df.groupby('income_type')['amount'].sum().reset_index()
                                            inc_fig = go.Figure(data=[go.Pie(labels=inc_by_cat['income_type'], values=inc_by_cat['amount'])])
                                            inc_fig.update_layout(title_text="Income by Type", height=350, width=350, margin=dict(l=10,r=10,t=30,b=10))
                                            inc_img = pio.to_image(inc_fig, format='png', width=350, height=350)
                                            story.append(RLImage(io.BytesIO(inc_img), width=260, height=260))
                                            story.append(Spacer(1, 8))

                                        # Expenses pie
                                        if not expense_df.empty and 'expense_type' in expense_df.columns:
                                            exp_by_cat = expense_df.groupby('expense_type')['amount'].sum().reset_index()
                                            exp_fig = go.Figure(data=[go.Pie(labels=exp_by_cat['expense_type'], values=exp_by_cat['amount'])])
                                            exp_fig.update_layout(title_text="Expenses by Type", height=350, width=350, margin=dict(l=10,r=10,t=30,b=10))
                                            exp_img = pio.to_image(exp_fig, format='png', width=350, height=350)
                                            story.append(RLImage(io.BytesIO(exp_img), width=260, height=260))
                                            story.append(Spacer(1, 8))
                                    except Exception as export_err:
                                        story.append(Paragraph("Note: Charts omitted in PDF (install with: pip install kaleido).", styles['Italic']))
                                        story.append(Spacer(1, 8))

                                    doc.build(story)
                                    buffer.seek(0)
                                    b64 = base64.b64encode(buffer.getvalue()).decode()
                                    filename = f"{org_title.replace(' ', '_')}_PL_{period_text.replace(' ', '_').replace(':','')}.pdf"
                                    st.markdown(f'<a href="data:application/pdf;base64,{b64}" download="{filename}">📄 Click to download PDF</a>', unsafe_allow_html=True)

                                if download_xls_clicked:
                                    import io
                                    output = io.BytesIO()
                                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                        pd.DataFrame([
                                            ['Total Income', total_income],
                                            ['Total Expenses', total_expenses],
                                            ['Net Profit', net_profit]
                                        ], columns=['Metric','Amount']).to_excel(writer, sheet_name='Summary', index=False)
                                    output.seek(0)
                                    import base64
                                    b64 = base64.b64encode(output.getvalue()).decode()
                                    filename = f"{org_title.replace(' ', '_')}_PL_{period_text.replace(' ', '_').replace(':','')}.xlsx"
                                    st.markdown(f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">📊 Click to download Excel</a>', unsafe_allow_html=True)

                            else:
                                st.info("No financial data found for the selected period.")
                                
                        except Exception as e:
                            st.error(f"Error generating P&L report: {str(e)}")

        with report_tabs[1]:
            # Check if demo mode
            is_demo_mode = False
            if st.session_state.user:
                if hasattr(st.session_state.user, 'email'):
                    is_demo_mode = getattr(st.session_state.user, 'email', '') == 'demo@example.com'
                else:
                    is_demo_mode = st.session_state.user.get('email', '') == 'demo@example.com'

            if is_demo_mode:
                st.info("🎯 **Demo Mode** - Showing sample transaction data. Sign up to view your actual transactions!")

                st.markdown("### Sample Transactions - January 2025")

                # Sample transaction data
                sample_data = [
                    {'S.No.': '1', 'Date': '2025-01-05', 'Category': 'Income', 'Type': 'Rent', 'Amount': '$1,800.00', 'Description': 'Monthly rent - Downtown Apt', 'Property': 'Downtown Apartment'},
                    {'S.No.': '2', 'Date': '2025-01-10', 'Category': 'Expense', 'Type': 'Maintenance', 'Amount': '$150.00', 'Description': 'Plumbing repair', 'Property': 'Downtown Apartment'},
                    {'S.No.': '3', 'Date': '2025-01-15', 'Category': 'Income', 'Type': 'Rent', 'Amount': '$2,200.00', 'Description': 'Monthly rent - Suburban House', 'Property': 'Suburban House'},
                    {'S.No.': '4', 'Date': '2025-01-20', 'Category': 'Expense', 'Type': 'Utilities', 'Amount': '$200.00', 'Description': 'Electric and water', 'Property': 'Suburban House'},
                    {'S.No.': '5', 'Date': '2025-01-25', 'Category': 'Expense', 'Type': 'Insurance', 'Amount': '$300.00', 'Description': 'Property insurance', 'Property': 'All Properties'},
                    {'S.No.': '', 'Date': '', 'Category': '', 'Type': '', 'Amount': '', 'Description': '**TOTAL (Income: $4,000.00 - Expenses: $650.00)**', 'Property': '$3,350.00'},
                ]

                df_demo = pd.DataFrame(sample_data)
                st.dataframe(df_demo, use_container_width=True, hide_index=True)

                st.info("Sign up to generate detailed transaction reports with filters and export options!")
                return

            if 'selected_organization' in st.session_state and st.session_state.selected_organization:
                selected_org_id = st.session_state.selected_organization
                org_name_txn = st.session_state.get('selected_org_name')
                if not org_name_txn:
                    try:
                        org_obj = db.get_organization_by_id(selected_org_id)
                        org_name_txn = org_obj.name if org_obj else 'Unknown Organization'
                    except Exception:
                        org_name_txn = 'Unknown Organization'

                # Preload properties for this organization for filter and name lookup
                props_res = db.supabase.table("properties").select("id,name,address").eq("organization_id", selected_org_id).execute()
                properties_list = props_res.data or []
                prop_map = {p['id']: (p.get('name') or p.get('address') or f"Property {p['id']}") for p in properties_list}
                prop_options = ["All"] + [prop_map[p['id']] for p in properties_list]

                # Filters row
                c1, c2, c3, c4 = st.columns([1,1,1,1])
                with c1:
                    txn_report_type = st.selectbox("Report Type", ["Yearly", "Monthly", "Custom"], key="txn_report_type")
                with c2:
                    # Date type filter (Year/Month/Custom)
                    if txn_report_type == "Yearly":
                        txn_year = st.selectbox("Select Year", 
                                             options=list(range(2020, date.today().year + 2)),
                                             index=date.today().year - 2020,
                                             key="txn_year_selector")
                        txn_start = date(txn_year, 1, 1)
                        txn_end = date(txn_year + 1, 1, 1)
                        txn_period_text = f"Year: {txn_year}"
                    elif txn_report_type == "Monthly":
                        cur_year = date.today().year
                        month_opts = [
                            f"January {cur_year}", f"February {cur_year}", f"March {cur_year}",
                            f"April {cur_year}", f"May {cur_year}", f"June {cur_year}",
                            f"July {cur_year}", f"August {cur_year}", f"September {cur_year}",
                            f"October {cur_year}", f"November {cur_year}", f"December {cur_year}"
                        ]
                        txn_month_label = st.selectbox("Select Month", month_opts, index=date.today().month - 1, key="txn_month_selector")
                        m_num = month_opts.index(txn_month_label) + 1
                        txn_start = date(cur_year, m_num, 1)
                        txn_end = date(cur_year + 1, 1, 1) if m_num == 12 else date(cur_year, m_num + 1, 1)
                        txn_period_text = f"Month: {txn_month_label}"
                    else:
                        d1, d2 = st.columns(2)
                        with d1:
                            txn_start = st.date_input("Start Date", value=date.today().replace(day=1), key="txn_start")
                        with d2:
                            txn_end = st.date_input("End Date", value=date.today(), key="txn_end")
                        txn_period_text = f"Period: {txn_start.strftime('%b %d, %Y')} - {txn_end.strftime('%b %d, %Y')}"
                with c3:
                    selected_property_label = st.selectbox("Property", options=prop_options, index=0, key="txn_property_filter")
                    # Resolve selected property id (None means All)
                    selected_property_id = None
                    if selected_property_label != "All":
                        # reverse lookup by label
                        for pid, pname in prop_map.items():
                            if pname == selected_property_label:
                                selected_property_id = pid
                                break
                with c4:
                    txn_type_filter = st.selectbox("Transaction Type", ["All", "Income", "Expenses"], key="txn_type_filter")

                # Generate button
                gen_txn = st.button("Generate Transactions Report", key="generate_txn")
                if gen_txn:
                    try:
                        rows = []

                        # Helper to apply property filter
                        def apply_common_filters(builder):
                            builder = builder.eq("organization_id", selected_org_id).gte("transaction_date", txn_start.isoformat()).lt("transaction_date", txn_end.isoformat())
                            if selected_property_id is not None:
                                builder = builder.eq("property_id", selected_property_id)
                            return builder

                        if txn_type_filter in ("All", "Income"):
                            inc_builder = db.supabase.table("income").select("*")
                            inc_res = apply_common_filters(inc_builder).execute()
                            for r in inc_res.data or []:
                                rows.append({
                                    'S.No.': 0,  # will fill after sort
                                    'Date': r.get('transaction_date'),
                                    'Type': 'Income',
                                    'Property': prop_map.get(r.get('property_id'), 'Unknown'),
                                    'Description': r.get('description') or r.get('income_type') or '',
                                    'Amount': float(r.get('amount', 0))
                                })

                        if txn_type_filter in ("All", "Expenses"):
                            exp_builder = db.supabase.table("expenses").select("*")
                            exp_res = apply_common_filters(exp_builder).execute()
                            for r in exp_res.data or []:
                                rows.append({
                                    'S.No.': 0,  # will fill after sort
                                    'Date': r.get('transaction_date'),
                                    'Type': 'Expense',
                                    'Property': prop_map.get(r.get('property_id'), 'Unknown'),
                                    'Description': r.get('description') or r.get('expense_type') or '',
                                    'Amount': float(r.get('amount', 0))
                                })

                        if rows:
                            df = pd.DataFrame(rows)
                            df.sort_values(by=['Date', 'Type'], inplace=True)
                            # Add serial number starting at 1
                            df['S.No.'] = range(1, len(df) + 1)
                            # Reorder columns: S.No., Date, Type, Property, Description, Amount
                            df = df[['S.No.', 'Date', 'Type', 'Property', 'Description', 'Amount']]
                            # Explicitly drop any id column if present
                            if 'id' in df.columns:
                                df = df.drop(columns=['id'])

                            # Calculate totals: Income (positive) and Expenses (negative)
                            total_income = df[df['Type'] == 'Income']['Amount'].sum()
                            total_expenses = df[df['Type'] == 'Expense']['Amount'].sum()
                            final_total = total_income - total_expenses

                            # Convert S.No. to string to allow empty string in total row
                            df['S.No.'] = df['S.No.'].astype(str)

                            # Add Total row with net calculation
                            total_row = pd.DataFrame({
                                'S.No.': [''],
                                'Date': [''],
                                'Type': [''],
                                'Property': [''],
                                'Description': [f'**TOTAL (Income: ${total_income:,.2f} - Expenses: ${total_expenses:,.2f})**'],
                                'Amount': [final_total]
                            })
                            df_with_total = pd.concat([df, total_row], ignore_index=True)

                            st.markdown(f"#### {org_name_txn} — {txn_period_text}")

                            # Configure column alignment to left
                            column_config = {
                                'S.No.': st.column_config.TextColumn('S.No.', width='small'),
                                'Date': st.column_config.TextColumn('Date', width='small'),
                                'Type': st.column_config.TextColumn('Type', width='medium'),
                                'Property': st.column_config.TextColumn('Property', width='medium'),
                                'Description': st.column_config.TextColumn('Description', width='large'),
                                'Amount': st.column_config.NumberColumn('Amount', format='$%.2f', width='small')
                            }

                            st.dataframe(df_with_total, use_container_width=True, hide_index=True, column_config=column_config)
                            
                            # Download buttons for Transactions Report
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                # PDF Download
                                if st.button("📄 Download PDF", key="download_txn_pdf"):
                                    try:
                                        from reportlab.lib.pagesizes import letter
                                        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
                                        from reportlab.lib.styles import getSampleStyleSheet
                                        from reportlab.lib import colors
                                        import io
                                        import base64
                                        
                                        buffer = io.BytesIO()
                                        doc = SimpleDocTemplate(buffer, pagesize=letter)
                                        story = []
                                        styles = getSampleStyleSheet()
                                        
                                        # Title
                                        title = Paragraph(f"<b>Transactions Report - {org_name_txn}</b>", styles['Title'])
                                        story.append(title)
                                        story.append(Spacer(1, 12))
                                        
                                        # Period
                                        period = Paragraph(f"<b>Period:</b> {txn_period_text}", styles['Normal'])
                                        story.append(period)
                                        story.append(Spacer(1, 12))
                                        
                                        # Convert dataframe to table data
                                        table_data = [df_with_total.columns.tolist()]
                                        for _, row in df_with_total.iterrows():
                                            table_data.append(row.tolist())
                                        
                                        # Create table
                                        table = Table(table_data)
                                        table.setStyle(TableStyle([
                                            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                            ('FONTSIZE', (0, 0), (-1, 0), 12),
                                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                                        ]))
                                        
                                        story.append(table)
                                        doc.build(story)
                                        
                                        buffer.seek(0)
                                        b64 = base64.b64encode(buffer.getvalue()).decode()
                                        filename = f"{org_name_txn.replace(' ', '_')}_Transactions_{txn_period_text.replace(' ', '_').replace(':', '')}.pdf"
                                        st.markdown(f'<a href="data:application/pdf;base64,{b64}" download="{filename}">📄 Click to download PDF</a>', unsafe_allow_html=True)
                                        
                                    except Exception as e:
                                        st.error(f"Error generating PDF: {str(e)}")
                            
                            with col2:
                                # Excel Download
                                if st.button("📊 Download Excel", key="download_txn_excel"):
                                    try:
                                        import io
                                        output = io.BytesIO()
                                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                            # Summary sheet
                                            summary_data = pd.DataFrame([
                                                ['Total Transactions', len(df)],
                                                ['Total Amount', f"${total_amount:,.2f}"],
                                                ['Period', txn_period_text]
                                            ], columns=['Metric', 'Value'])
                                            summary_data.to_excel(writer, sheet_name='Summary', index=False)
                                            
                                            # Transactions sheet
                                            df_with_total.to_excel(writer, sheet_name='Transactions', index=False)
                                        
                                        output.seek(0)
                                        b64 = base64.b64encode(output.getvalue()).decode()
                                        filename = f"{org_name_txn.replace(' ', '_')}_Transactions_{txn_period_text.replace(' ', '_').replace(':', '')}.xlsx"
                                        st.markdown(f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">📊 Click to download Excel</a>', unsafe_allow_html=True)
                                        
                                    except Exception as e:
                                        st.error(f"Error generating Excel: {str(e)}")
                        else:
                            st.info("No transactions found for the selected criteria.")
                    except Exception as e:
                        st.error(f"Error generating Transactions report: {str(e)}")
        
        with report_tabs[2]:
            # Check if demo mode
            is_demo_mode = False
            if st.session_state.user:
                if hasattr(st.session_state.user, 'email'):
                    is_demo_mode = getattr(st.session_state.user, 'email', '') == 'demo@example.com'

            if is_demo_mode:
                st.info("🎯 **Demo Mode** - Showing sample property performance data.")

                # Demo property performance data
                demo_properties = [
                    {
                        'name': '182 Magellan Dr',
                        'address': '182 Magellan Dr, Martinsburg, WV 25404',
                        'monthly_rent': 1850,
                        'total_income': 4070,
                        'total_expenses': 2495,
                        'net_income': 1575,
                        'roi': 0.9,
                        'occupancy_rate': 95.0
                    },
                    {
                        'name': '248 Magellan Dr',
                        'address': '248 Magellan Dr, Martinsburg, WV 25404',
                        'monthly_rent': 1900,
                        'total_income': 1837,
                        'total_expenses': 1997,
                        'net_income': -160,
                        'roi': -0.1,
                        'occupancy_rate': 95.0
                    },
                    {
                        'name': '46 Furlong Way',
                        'address': '46 Furlong Way, Martinsburg, WV 25404',
                        'monthly_rent': 1875,
                        'total_income': 3750,
                        'total_expenses': 839,
                        'net_income': 2911,
                        'roi': 1.5,
                        'occupancy_rate': 95.0
                    }
                ]

                # Display demo properties in columns
                st.markdown(f"**Report for: ABVA Holdings LLC**")

                prop_cols = st.columns(3)

                for i, prop in enumerate(demo_properties):
                    with prop_cols[i]:
                        with st.container():
                            st.markdown(f"**{prop['name']}**")
                            st.markdown(f"*{prop['address']}*")

                            # Key metrics
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Monthly Rent", f"${prop['monthly_rent']:,}")
                                st.metric("Total Income", f"${prop['total_income']:,}")
                            with col2:
                                st.metric("Total Expenses", f"${prop['total_expenses']:,}")
                                st.metric("Net Income", f"${prop['net_income']:,}")

                            # Performance metrics
                            st.metric("ROI", f"{prop['roi']:.1f}%")
                            st.metric("Occupancy Rate", f"{prop['occupancy_rate']:.1f}%")

                            # Property details expander
                            with st.expander("Property Details"):
                                st.write(f"**Purchase Price:** $170,000")
                                st.write(f"**Property Type:** Residential")
                                st.write(f"**Purchase Date:** January 15, 2023")
                                st.write(f"**Description:** Single-family home in excellent condition")

                            st.markdown("---")

                return

            if 'selected_organization' in st.session_state and st.session_state.selected_organization:
                selected_org_id = st.session_state.selected_organization
                org_name_perf = st.session_state.get('selected_org_name')
                if not org_name_perf:
                    try:
                        org_obj = db.get_organization_by_id(selected_org_id)
                        org_name_perf = org_obj.name if org_obj else 'Unknown Organization'
                    except Exception:
                        org_name_perf = 'Unknown Organization'

                # Get properties for this organization
                try:
                    org_properties = db.get_properties_by_organization(selected_org_id)
                    property_names = {prop.id: prop.name for prop in org_properties}
                except Exception as e:
                    st.error(f"Error fetching properties: {str(e)}")
                    org_properties = []
                    property_names = {}

                # Filters row
                col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
                
                with col1:
                    # Property filter
                    selected_property_id = st.selectbox(
                        "Filter by Property", 
                        ["All"] + list(property_names.keys()), 
                        format_func=lambda x: "All" if x == "All" else property_names[x],
                        key="properties_performance_property_filter"
                    )
                
                with col2:
                    # Date filter type
                    date_filter_type = st.selectbox(
                        "Date Filter", 
                        ["Current Year", "All Time", "Custom Range", "Last 3 Years", "Last 5 Years"],
                        key="properties_performance_date_filter_type"
                    )
                
                with col3:
                    if date_filter_type == "Custom Range":
                        start_date = st.date_input("Start Date", value=date.today().replace(month=1, day=1), key="properties_performance_start_date")
                    else:
                        start_date = None
                
                with col4:
                    if date_filter_type == "Custom Range":
                        end_date = st.date_input("End Date", value=date.today(), key="properties_performance_end_date")
                    else:
                        end_date = None

                # Calculate date range
                if date_filter_type == "Current Year":
                    start_date = date.today().replace(month=1, day=1)
                    end_date = date.today()
                elif date_filter_type == "All Time":
                    start_date = None
                    end_date = None
                elif date_filter_type == "Last 3 Years":
                    start_date = date.today().replace(year=date.today().year - 3)
                    end_date = date.today()
                elif date_filter_type == "Last 5 Years":
                    start_date = date.today().replace(year=date.today().year - 5)
                    end_date = date.today()

                # Filter properties based on selection
                if selected_property_id != "All":
                    filtered_properties = [prop for prop in org_properties if prop.id == selected_property_id]
                else:
                    filtered_properties = org_properties

                if filtered_properties:
                    st.markdown(f"**Report for: {org_name_perf}**")
                    if selected_property_id != "All":
                        st.markdown(f"**Property: {property_names[selected_property_id]}**")
                    
                    # Get all income and expenses once for efficiency
                    try:
                        all_income = db.get_all_income()
                        all_expenses = db.get_all_expenses()
                    except Exception as e:
                        st.error(f"Error fetching financial data: {str(e)}")
                        all_income = []
                        all_expenses = []
                    
                    # Create property performance cards
                    prop_cols = st.columns(min(len(filtered_properties), 3))  # Max 3 properties per row
                    
                    for i, prop in enumerate(filtered_properties):
                        with prop_cols[i % 3]:
                            try:
                                
                                # Filter by organization and property
                                prop_income = [inc for inc in all_income if inc.organization_id == selected_org_id and inc.property_id == prop.id]
                                prop_expenses = [exp for exp in all_expenses if exp.organization_id == selected_org_id and exp.property_id == prop.id]
                                
                                # Apply date filters if specified
                                if start_date:
                                    # Convert date to datetime for comparison
                                    start_datetime = datetime.combine(start_date, datetime.min.time())
                                    prop_income = [inc for inc in prop_income if inc.transaction_date >= start_datetime]
                                    prop_expenses = [exp for exp in prop_expenses if exp.transaction_date >= start_datetime]
                                if end_date:
                                    # Convert date to datetime for comparison
                                    end_datetime = datetime.combine(end_date, datetime.max.time())
                                    prop_income = [inc for inc in prop_income if inc.transaction_date <= end_datetime]
                                    prop_expenses = [exp for exp in prop_expenses if exp.transaction_date <= end_datetime]
                                
                                prop_total_income = sum(inc.amount for inc in prop_income)
                                prop_total_expenses = sum(exp.amount for exp in prop_expenses)
                                prop_net_income = prop_total_income - prop_total_expenses
                                prop_roi = (prop_net_income / prop.purchase_price * 100) if prop.purchase_price > 0 else 0
                                
                                # Calculate occupancy rate (simplified)
                                total_days = (end_date - start_date).days if start_date and end_date else 365
                                occupancy_rate = 95.0  # Placeholder - would need actual occupancy data
                                
                                with st.container():
                                    st.markdown(f"**{prop.name}**")
                                    st.markdown(f"*{prop.address}*")
                                    
                                    # Key metrics
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.metric("Monthly Rent", f"${prop.monthly_rent:,.0f}")
                                        st.metric("Total Income", f"${prop_total_income:,.0f}")
                                    with col2:
                                        st.metric("Total Expenses", f"${prop_total_expenses:,.0f}")
                                        st.metric("Net Income", f"${prop_net_income:,.0f}")
                                    
                                    # Performance metrics
                                    st.metric("ROI", f"{prop_roi:.1f}%")
                                    st.metric("Occupancy Rate", f"{occupancy_rate:.1f}%")
                                    
                                    # Property details
                                    with st.expander("Property Details"):
                                        st.write(f"**Purchase Price:** ${prop.purchase_price:,.0f}")
                                        st.write(f"**Property Type:** {prop.property_type.value.title()}")
                                        st.write(f"**Purchase Date:** {prop.purchase_date.strftime('%B %d, %Y')}")
                                        st.write(f"**Description:** {prop.description or 'No description available'}")
                                    
                                    st.markdown("---")
                                    
                            except Exception as e:
                                st.error(f"Error loading data for {prop.name}: {str(e)}")
                    
                    # Summary statistics
                    if len(filtered_properties) > 1:
                        st.markdown("### 📊 Summary Statistics")
                        
                        # Calculate totals for all filtered properties
                        total_income = 0
                        total_expenses = 0
                        roi_sum = 0
                        
                        for prop in filtered_properties:
                            # Get property-specific income and expenses
                            prop_income = [inc for inc in all_income if inc.organization_id == selected_org_id and inc.property_id == prop.id]
                            prop_expenses = [exp for exp in all_expenses if exp.organization_id == selected_org_id and exp.property_id == prop.id]
                            
                            # Apply date filters if specified
                            if start_date:
                                # Convert date to datetime for comparison
                                start_datetime = datetime.combine(start_date, datetime.min.time())
                                prop_income = [inc for inc in prop_income if inc.transaction_date >= start_datetime]
                                prop_expenses = [exp for exp in prop_expenses if exp.transaction_date >= start_datetime]
                            if end_date:
                                # Convert date to datetime for comparison
                                end_datetime = datetime.combine(end_date, datetime.max.time())
                                prop_income = [inc for inc in prop_income if inc.transaction_date <= end_datetime]
                                prop_expenses = [exp for exp in prop_expenses if exp.transaction_date <= end_datetime]
                            
                            prop_total_income = sum(inc.amount for inc in prop_income)
                            prop_total_expenses = sum(exp.amount for exp in prop_expenses)
                            
                            total_income += prop_total_income
                            total_expenses += prop_total_expenses
                            
                            # Calculate ROI for this property
                            prop_net_income = prop_total_income - prop_total_expenses
                            prop_roi = (prop_net_income / prop.purchase_price * 100) if prop.purchase_price > 0 else 0
                            roi_sum += prop_roi
                        
                        total_net = total_income - total_expenses
                        avg_roi = roi_sum / len(filtered_properties)
                        
                        summary_cols = st.columns(4)
                        with summary_cols[0]:
                            st.metric("Total Properties", len(filtered_properties))
                        with summary_cols[1]:
                            st.metric("Total Income", f"${total_income:,.0f}")
                        with summary_cols[2]:
                            st.metric("Total Expenses", f"${total_expenses:,.0f}")
                        with summary_cols[3]:
                            st.metric("Average ROI", f"{avg_roi:.1f}%")
                
                else:
                    if selected_property_id != "All":
                        st.info(f"No properties found matching the selected criteria.")
                    else:
                        st.info("No properties found for this organization.")
                        
            else:
                st.warning("Please select an organization first to view properties performance.")

    elif selected == "AI Insights":
        st.info("AI insights functionality - Sign up to use with your own data!")

def generate_pending_transactions_for_organization(organization_id: int):
    """Generate pending transactions for a specific organization"""
    from datetime import datetime, timedelta, date
    from database.models import RecurringTransaction, PendingTransaction, RecurringInterval
    
    db = DatabaseOperations()
    current_date = date.today()
    
    # Get all active recurring transactions for this organization
    recurring_transactions = db.get_recurring_transactions_by_organization(organization_id)
    
    generated_count = 0
    
    for recurring in recurring_transactions:
        # Check if we should generate a pending transaction
        if not recurring.is_active:
            continue
            
        # Check if we've passed the end date
        if recurring.end_date and current_date > recurring.end_date.date():
            continue
        
        # Calculate the latest due date on or before today
        start_date = recurring.start_date.date()
        next_due_date = start_date
        if current_date > start_date:
            if recurring.interval == RecurringInterval.WEEKLY:
                weeks = (current_date - start_date).days // 7
                next_due_date = start_date + timedelta(weeks=weeks)
            elif recurring.interval == RecurringInterval.MONTHLY:
                years = current_date.year - start_date.year
                months = years * 12 + (current_date.month - start_date.month)
                months = max(0, months)
                y = start_date.year + (start_date.month - 1 + months) // 12
                m = (start_date.month - 1 + months) % 12 + 1
                dim = [31,29 if (y%4==0 and (y%100!=0 or y%400==0)) else 28,31,30,31,30,31,31,30,31,30,31][m-1]
                d = min(start_date.day, dim)
                next_due_date = date(y, m, d)
            elif recurring.interval == RecurringInterval.QUARTERLY:
                years = current_date.year - start_date.year
                months = years * 12 + (current_date.month - start_date.month)
                quarters = max(0, months // 3)
                y = start_date.year + (start_date.month - 1 + quarters*3) // 12
                m = (start_date.month - 1 + quarters*3) % 12 + 1
                dim = [31,29 if (y%4==0 and (y%100!=0 or y%400==0)) else 28,31,30,31,30,31,31,30,31,30,31][m-1]
                d = min(start_date.day, dim)
                next_due_date = date(y, m, d)
            elif recurring.interval == RecurringInterval.YEARLY:
                y = current_date.year
                m = start_date.month
                dim = [31,29 if (y%4==0 and (y%100!=0 or y%400==0)) else 28,31,30,31,30,31,31,30,31,30,31][m-1]
                d = min(start_date.day, dim)
                next_due_date = date(y, m, d)
        
        # If next due date is today or in the past, generate pending transaction
        if next_due_date <= current_date:
            # Check if pending transaction already exists
            existing_pending = db.get_pending_transactions_by_organization(organization_id)
            already_pending = any(
                pt.recurring_transaction_id == recurring.id and
                pt.transaction_date.date() == next_due_date
                for pt in existing_pending
            )

            # Also check if this transaction was already confirmed and exists in regular income/expense tables
            already_confirmed = False
            try:
                if recurring.transaction_type == 'income':
                    # Check income table for same property, amount, and date
                    income_check = db.client.table("income").select("id").eq("organization_id", organization_id).eq("property_id", recurring.property_id).eq("amount", recurring.amount).eq("transaction_date", datetime.combine(next_due_date, datetime.min.time()).isoformat()).execute()
                    already_confirmed = len(income_check.data) > 0
                elif recurring.transaction_type == 'expense':
                    # Check expense table for same property, amount, and date
                    expense_check = db.client.table("expenses").select("id").eq("organization_id", organization_id).eq("property_id", recurring.property_id).eq("amount", recurring.amount).eq("transaction_date", datetime.combine(next_due_date, datetime.min.time()).isoformat()).execute()
                    already_confirmed = len(expense_check.data) > 0
            except Exception:
                # If check fails, assume not confirmed
                already_confirmed = False

            if not already_pending and not already_confirmed:
                # Create pending transaction
                pending_transaction = PendingTransaction(
                    organization_id=recurring.organization_id,
                    property_id=recurring.property_id,
                    transaction_type=recurring.transaction_type,
                    income_type=recurring.income_type,
                    expense_type=recurring.expense_type,
                    amount=recurring.amount,
                    description=recurring.description,
                    transaction_date=datetime.combine(next_due_date, datetime.min.time()),
                    recurring_transaction_id=recurring.id,
                    is_confirmed=False
                )

                if db.create_pending_transaction(pending_transaction):
                    generated_count += 1
    
    return generated_count

def main():
    """Main application function"""
    initialize_session_state()
    
    if st.session_state.authenticated:
        show_main_app()
    else:
        show_auth_page()

if __name__ == "__main__":
    main()
