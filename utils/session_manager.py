"""
Session Management Utility for PropLedger
Handles Supabase authentication session persistence across page reloads
"""

import streamlit as st
from database.supabase_client import get_supabase_client

class SessionManager:
    """Manages user authentication sessions"""
    
    @staticmethod
    def initialize_session():
        """Initialize session state and check for existing Supabase session"""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'auth_mode' not in st.session_state:
            st.session_state.auth_mode = 'login'
        
        # Check for existing Supabase session on page load
        if not st.session_state.authenticated:
            try:
                supabase = get_supabase_client()
                session = supabase.auth.get_session()
                
                if session and session.user:
                    st.session_state.authenticated = True
                    st.session_state.user = session.user
                    st.rerun()
            except Exception as e:
                # Session might be expired or invalid, continue with login
                pass
        else:
            # If already authenticated, verify session is still valid
            try:
                supabase = get_supabase_client()
                session = supabase.auth.get_session()
                
                if not session or not session.user:
                    # Session expired, clear authentication
                    SessionManager.clear_session()
                    st.rerun()
            except Exception as e:
                # Session verification failed, clear authentication
                SessionManager.clear_session()
                st.rerun()
    
    @staticmethod
    def clear_session():
        """Clear all session data"""
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.selected_organization = None
        st.session_state.selected_org_id = None
        st.session_state.selected_org_name = None
    
    @staticmethod
    def sign_out():
        """Sign out user from Supabase and clear session"""
        try:
            supabase = get_supabase_client()
            supabase.auth.sign_out()
        except Exception as e:
            # Continue with logout even if Supabase signout fails
            pass
        
        SessionManager.clear_session()
        st.rerun()
    
    @staticmethod
    def is_authenticated():
        """Check if user is authenticated"""
        return st.session_state.get('authenticated', False)
    
    @staticmethod
    def get_user():
        """Get current user"""
        return st.session_state.get('user', None)
    
    @staticmethod
    def get_user_id():
        """Get current user ID"""
        user = SessionManager.get_user()
        if user:
            if hasattr(user, 'id'):
                return getattr(user, 'id', None)
            elif isinstance(user, dict):
                return user.get('id', None)
        return None
    
    @staticmethod
    def get_user_email():
        """Get current user email"""
        user = SessionManager.get_user()
        if user:
            if hasattr(user, 'email'):
                return getattr(user, 'email', None)
            elif isinstance(user, dict):
                return user.get('email', None)
        return None
    
    @staticmethod
    def is_demo_mode():
        """Check if user is in demo mode"""
        email = SessionManager.get_user_email()
        return email == 'demo@example.com'
