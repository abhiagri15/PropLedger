#!/usr/bin/env python3
"""
PropLedger Setup Script
This script helps set up the PropLedger application
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file with template values"""
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return
    
    env_content = """# PropLedger Environment Configuration
# Copy this file and update with your actual values

# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file template")
    print("📝 Please update .env with your actual API keys and database credentials")

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import streamlit
        import supabase
        import openai
        import pandas
        import plotly
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return False

def main():
    """Main setup function"""
    print("🏠 PropLedger Setup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Update .env file with your API keys")
    print("2. Set up your Supabase database using database/schema.sql")
    print("3. Run: streamlit run app.py")
    print("\nFor detailed instructions, see README.md")

if __name__ == "__main__":
    main()
