from supabase import create_client, Client
from config import get_supabase_url, get_supabase_key
import streamlit as st

@st.cache_resource
def get_supabase_client() -> Client:
    """Initialize and return Supabase client"""
    supabase_url = get_supabase_url()
    supabase_key = get_supabase_key()
    
    if not supabase_url or not supabase_key:
        st.error("Please set SUPABASE_URL and SUPABASE_KEY in your environment variables")
        st.stop()
    
    return create_client(supabase_url, supabase_key)

def test_connection():
    """Test Supabase connection"""
    try:
        client = get_supabase_client()
        # Try to fetch from a simple table to test connection
        result = client.table("properties").select("*").limit(1).execute()
        return True
    except Exception as e:
        st.error(f"Database connection failed: {str(e)}")
        return False

def get_current_user():
    """Get current authenticated user"""
    try:
        client = get_supabase_client()
        user = client.auth.get_user()
        return user.user if user else None
    except Exception as e:
        st.error(f"Error getting current user: {str(e)}")
        return None

def sign_out():
    """Sign out current user"""
    try:
        client = get_supabase_client()
        client.auth.sign_out()
        return True
    except Exception as e:
        st.error(f"Error signing out: {str(e)}")
        return False
