import os

# Load environment variables for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, continue without it

def get_config_value(env_key, secret_key, default=None):
    """
    Get configuration value from Streamlit secrets first, then environment variables.
    This allows the app to work both locally (.env file) and on Streamlit Cloud (secrets).
    """
    try:
        # Import streamlit only when needed
        import streamlit as st
        # Try to get from Streamlit secrets first (for deployed app)
        if hasattr(st, 'secrets') and secret_key in st.secrets:
            return st.secrets[secret_key]
    except Exception:
        pass
    
    # Fall back to environment variables (for local development)
    return os.getenv(env_key, default)

# Configuration values - loaded lazily
SUPABASE_URL = None
SUPABASE_KEY = None
OPENAI_API_KEY = None
STREAMLIT_SERVER_PORT = 8501

def get_supabase_url():
    global SUPABASE_URL
    if SUPABASE_URL is None:
        SUPABASE_URL = get_config_value("SUPABASE_URL", "supabase_url")
    return SUPABASE_URL

def get_supabase_key():
    global SUPABASE_KEY
    if SUPABASE_KEY is None:
        SUPABASE_KEY = get_config_value("SUPABASE_KEY", "supabase_key")
    return SUPABASE_KEY

def get_openai_api_key():
    global OPENAI_API_KEY
    if OPENAI_API_KEY is None:
        OPENAI_API_KEY = get_config_value("OPENAI_API_KEY", "openai_api_key")
    return OPENAI_API_KEY

def get_streamlit_server_port():
    global STREAMLIT_SERVER_PORT
    if STREAMLIT_SERVER_PORT == 8501:  # Only load if still default
        STREAMLIT_SERVER_PORT = int(get_config_value("STREAMLIT_SERVER_PORT", "streamlit_server_port", 8501))
    return STREAMLIT_SERVER_PORT

# Backward compatibility - create module-level variables that call functions
# These will be set when first accessed
def _get_config_values():
    global SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY, STREAMLIT_SERVER_PORT
    SUPABASE_URL = get_supabase_url()
    SUPABASE_KEY = get_supabase_key()
    OPENAI_API_KEY = get_openai_api_key()
    STREAMLIT_SERVER_PORT = get_streamlit_server_port()

# Initialize on first import
_get_config_values()

# Database Table Names
PROPERTIES_TABLE = "properties"
INCOME_TABLE = "income"
EXPENSES_TABLE = "expenses"
CATEGORIES_TABLE = "categories"
