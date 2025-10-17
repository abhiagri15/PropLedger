"""
AI Insights page for PropLedger
Extracted from app_auth.py for better maintainability
"""

import streamlit as st

def render_ai_insights():
    """Render the AI Insights page"""
    st.markdown('<h1 class="main-header">🤖 AI-Powered Insights</h1>', unsafe_allow_html=True)
    st.info("AI insights functionality - Sign up to use with your own data!")
