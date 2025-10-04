# PropLedger Database Setup Guide

This guide will help you set up your Supabase database with all the required tables for PropLedger to work properly.

## 🗄️ **Step 1: Access Your Supabase Dashboard**

1. Go to [supabase.com](https://supabase.com)
2. Sign in to your account
3. Open your PropLedger project

## 🔧 **Step 2: Run the Database Schema**

1. **Navigate to SQL Editor**:
   - In your Supabase dashboard, click on "SQL Editor" in the left sidebar

2. **Create the Tables**:
   - Click "New Query"
   - Copy the entire contents of `database/complete_schema.sql`
   - Paste it into the SQL editor
   - Click "Run" to execute the script

3. **Verify Tables Created**:
   - Go to "Table Editor" in the left sidebar
   - You should see these tables:
     - `properties`
     - `income`
     - `expenses`
     - `categories`

## 🔐 **Step 3: Enable Authentication (if not already done)**

1. **Go to Authentication**:
   - Click "Authentication" in the left sidebar
   - Click "Settings"

2. **Configure Authentication**:
   - Enable "Enable email confirmations" (recommended)
   - Set "Site URL" to `http://localhost:8504`
   - Add `http://localhost:8504` to "Redirect URLs"

3. **Test Authentication**:
   - Go to "Authentication" → "Users"
   - You should be able to see registered users here

## 🧪 **Step 4: Test the Setup**

1. **Open PropLedger**: Go to http://localhost:8504

2. **Sign Up**: Create a new account with your email

3. **Add a Property**: Try adding a property to test the database connection

4. **Check Data**: Go to Supabase Table Editor to see your data

## 🔍 **Step 5: Verify Everything Works**

### **Check Tables in Supabase**:
- Go to Table Editor
- Click on each table to see the structure
- Verify RLS policies are enabled (green shield icon)

### **Test Features**:
- ✅ Sign up and login
- ✅ Add properties
- ✅ Add income records
- ✅ Add expense records
- ✅ View analytics
- ✅ Use AI insights

## 🐛 **Troubleshooting**

### **Common Issues**:

1. **"Table not found" error**:
   - Make sure you ran the complete schema SQL
   - Check that tables exist in Table Editor

2. **"Permission denied" error**:
   - Verify RLS policies are created
   - Check that user is authenticated

3. **"User not authenticated" error**:
   - Make sure you're signed in
   - Check Supabase authentication settings

### **Debug Steps**:

1. **Check Table Editor**:
   - Verify all tables exist
   - Check table structure matches the schema

2. **Check Authentication**:
   - Go to Authentication → Users
   - Verify your user account exists

3. **Check RLS Policies**:
   - Go to Authentication → Policies
   - Verify policies are created for all tables

## 📊 **Database Schema Overview**

### **Tables Created**:
- **properties**: Rental property information
- **income**: Income transactions
- **expenses**: Expense transactions
- **categories**: Custom categories

### **Security Features**:
- **Row Level Security (RLS)**: Users can only see their own data
- **User Authentication**: Secure user management
- **Data Isolation**: Each user's data is completely separate

### **Performance Features**:
- **Indexes**: Optimized for fast queries
- **Triggers**: Automatic timestamp updates
- **Views**: Pre-calculated financial summaries

## 🚀 **Next Steps**

Once the database is set up:

1. **Start Using PropLedger**: All features will work with real data
2. **Add Your Properties**: Begin tracking your rental properties
3. **Record Transactions**: Add income and expenses
4. **View Analytics**: See your financial performance
5. **Get AI Insights**: Use AI-powered recommendations

## 📚 **Additional Resources**

- [Supabase Documentation](https://supabase.com/docs)
- [Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

Your PropLedger database is now ready for full functionality! 🎉
