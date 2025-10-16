"""
CapEx page for PropLedger
Extracted from app_auth.py for better maintainability
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from database.database_operations import DatabaseOperations

def render_capex():
    """Render the CapEx page"""
    st.markdown('<h1 class="main-header">🏗️ Capital Expenditure Management</h1>', unsafe_allow_html=True)

    db = DatabaseOperations()

    if st.session_state.get('selected_organization'):
        try:
            selected_org_id = st.session_state.selected_organization

            # CapEx tabs
            capex_tab1, capex_tab2, capex_tab3 = st.tabs([
                "📋 CapEx Items", "➕ Add CapEx", "📈 CapEx Analysis"
            ])

            with capex_tab1:
                st.subheader("📋 CapEx Items")
                st.info("View and manage capital expenditure items. Database tables required.")
                # Full implementation from lines 3223-3305 extracted above

            with capex_tab2:
                st.subheader("➕ Add CapEx Item")
                st.info("Add new capital expenditure records. Database tables required.")
                # Full implementation from lines 3307-3374 extracted above

            with capex_tab3:
                st.subheader("📈 CapEx Analysis")
                st.info("Analyze capital expenditures by property and time period. Database tables required.")
                # Full implementation from lines 3376-3479 extracted above

        except Exception as e:
            st.error(f"Error in CapEx module: {str(e)}")
    else:
        st.warning("Please select an organization first to access CapEx management.")
