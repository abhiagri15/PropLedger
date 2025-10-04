import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Environment variables loaded successfully

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Streamlit Configuration
STREAMLIT_SERVER_PORT = int(os.getenv("STREAMLIT_SERVER_PORT", 8501))

# Database Table Names
PROPERTIES_TABLE = "properties"
INCOME_TABLE = "income"
EXPENSES_TABLE = "expenses"
CATEGORIES_TABLE = "categories"
