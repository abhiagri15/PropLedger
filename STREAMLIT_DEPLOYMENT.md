# Streamlit Cloud Deployment Guide

## 🚀 Deploying PropLedger to Streamlit Cloud

### Prerequisites
- GitHub repository with your PropLedger code
- Streamlit Cloud account (free at https://share.streamlit.io)

### Step 1: Prepare Your Repository
1. **Ensure your code is pushed to GitHub** (main branch)
2. **Verify your `config.py` is updated** to use Streamlit secrets
3. **Make sure `.gitignore` excludes sensitive files**

### Step 2: Deploy to Streamlit Cloud
1. **Go to Streamlit Cloud**: https://share.streamlit.io
2. **Sign in with GitHub**
3. **Click "New app"**
4. **Fill in the details**:
   - **Repository**: `abhiagri15/PropLedger`
   - **Branch**: `main`
   - **Main file path**: `app_auth.py`
   - **App URL**: Choose a unique name (e.g., `prop-ledger`)

### Step 3: Configure Secrets
1. **Click "Advanced settings"**
2. **Add the following secrets**:

```toml
[secrets]
# Supabase Configuration
supabase_url = "your_actual_supabase_url"
supabase_key = "your_actual_supabase_anon_key"

# OpenAI Configuration  
openai_api_key = "your_actual_openai_api_key"

# Streamlit Configuration
streamlit_server_port = 8501
```

### Step 4: Deploy
1. **Click "Deploy!"**
2. **Wait for deployment** (usually 2-3 minutes)
3. **Your app will be available at**: `https://prop-ledger.streamlit.app`

## 🔧 Configuration Details

### Local Development
- Uses `.env` file for configuration
- Run with: `streamlit run app_auth.py`

### Streamlit Cloud
- Uses Streamlit secrets for configuration
- Automatically detects and uses secrets from the web interface

### Configuration Priority
1. **Streamlit secrets** (for deployed apps)
2. **Environment variables** (for local development)
3. **Default values** (fallback)

## 📋 Required Secrets

| Secret Key | Description | Example |
|------------|-------------|---------|
| `supabase_url` | Your Supabase project URL | `https://abc123.supabase.co` |
| `supabase_key` | Your Supabase anon key | `eyJhbGciOiJIUzI1NiIs...` |
| `openai_api_key` | Your OpenAI API key | `sk-...` |
| `streamlit_server_port` | Port number (optional) | `8501` |

## 🛠️ Troubleshooting

### Common Issues
1. **"Please set SUPABASE_URL and SUPABASE_KEY"**
   - Check that secrets are properly configured in Streamlit Cloud
   - Verify secret names match exactly (case-sensitive)

2. **Database connection errors**
   - Ensure Supabase URL and key are correct
   - Check that your Supabase project is active

3. **OpenAI API errors**
   - Verify your OpenAI API key is valid
   - Check that you have credits in your OpenAI account

### Debug Steps
1. **Check Streamlit logs** in the deployment interface
2. **Verify secrets** are correctly set
3. **Test locally** with the same configuration
4. **Check Supabase logs** for database issues

## 🎯 Post-Deployment

### Database Setup
1. **Run the SQL schema** from `database/complete_schema.sql` in your Supabase SQL editor
2. **Enable Row-Level Security** policies
3. **Test user registration** and login

### App Features
- ✅ **User Authentication** (Supabase Auth)
- ✅ **Multi-Organization Support**
- ✅ **Property Management**
- ✅ **Income/Expense Tracking**
- ✅ **Real-time Dashboard**
- ✅ **P&L Calculations**

## 🔒 Security Notes

- **Never commit** `.env` files or `secrets.toml` files
- **Use Streamlit secrets** for production deployment
- **Keep API keys secure** and rotate them regularly
- **Enable RLS** in Supabase for data isolation

## 📞 Support

If you encounter issues:
1. Check the Streamlit Cloud logs
2. Verify your Supabase configuration
3. Test locally first
4. Check the GitHub repository for updates

---

**Your PropLedger app is now ready for production! 🎉**
