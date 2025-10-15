-- PropLedger Complete Database Schema for Supabase
-- This script creates all required tables with user authentication support

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Organizations table
CREATE TABLE IF NOT EXISTS organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User-Organization junction table
CREATE TABLE IF NOT EXISTS user_organizations (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member')),
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, organization_id)
);

-- Properties table with user authentication and organization support
CREATE TABLE IF NOT EXISTS properties (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    property_type VARCHAR(50) NOT NULL CHECK (property_type IN ('apartment', 'house', 'condo', 'townhouse', 'commercial')),
    purchase_price DECIMAL(15,2) NOT NULL,
    purchase_date DATE NOT NULL,
    monthly_rent DECIMAL(10,2) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Income table with user authentication and organization support
CREATE TABLE IF NOT EXISTS income (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    income_type VARCHAR(50) NOT NULL CHECK (income_type IN ('rent', 'deposit', 'late_fee', 'other')),
    description TEXT NOT NULL,
    transaction_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Expenses table with user authentication and organization support
CREATE TABLE IF NOT EXISTS expenses (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    expense_type VARCHAR(50) NOT NULL CHECK (expense_type IN ('mortgage', 'maintenance', 'repairs', 'utilities', 'insurance', 'taxes', 'management', 'advertising', 'legal', 'hoa', 'home_warranty', 'other')),
    description TEXT NOT NULL,
    transaction_date DATE NOT NULL,
    receipt_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Categories table for custom income/expense categories
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('income', 'expense')),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Recurring transactions table for recurring income/expense setups
CREATE TABLE IF NOT EXISTS recurring_transactions (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('income', 'expense')),
    income_type VARCHAR(50) CHECK (income_type IN ('rent', 'deposit', 'late_fee', 'other')),
    expense_type VARCHAR(50) CHECK (expense_type IN ('mortgage', 'maintenance', 'repairs', 'utilities', 'insurance', 'taxes', 'management', 'advertising', 'legal', 'hoa', 'home_warranty', 'other')),
    amount DECIMAL(10,2) NOT NULL,
    description TEXT NOT NULL,
    interval VARCHAR(20) NOT NULL CHECK (interval IN ('weekly', 'monthly', 'quarterly', 'yearly')),
    start_date DATE NOT NULL,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Pending transactions table for transactions awaiting confirmation
CREATE TABLE IF NOT EXISTS pending_transactions (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('income', 'expense')),
    income_type VARCHAR(50) CHECK (income_type IN ('rent', 'deposit', 'late_fee', 'other')),
    expense_type VARCHAR(50) CHECK (expense_type IN ('mortgage', 'maintenance', 'repairs', 'utilities', 'insurance', 'taxes', 'management', 'advertising', 'legal', 'hoa', 'home_warranty', 'other')),
    amount DECIMAL(10,2) NOT NULL,
    description TEXT NOT NULL,
    transaction_date TIMESTAMP WITH TIME ZONE NOT NULL,
    recurring_transaction_id INTEGER REFERENCES recurring_transactions(id) ON DELETE SET NULL,
    is_confirmed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_properties_user_id ON properties(user_id);
CREATE INDEX IF NOT EXISTS idx_properties_property_type ON properties(property_type);
CREATE INDEX IF NOT EXISTS idx_income_user_id ON income(user_id);
CREATE INDEX IF NOT EXISTS idx_income_property_id ON income(property_id);
CREATE INDEX IF NOT EXISTS idx_income_transaction_date ON income(transaction_date);
CREATE INDEX IF NOT EXISTS idx_expenses_user_id ON expenses(user_id);
CREATE INDEX IF NOT EXISTS idx_expenses_property_id ON expenses(property_id);
CREATE INDEX IF NOT EXISTS idx_expenses_transaction_date ON expenses(transaction_date);
CREATE INDEX IF NOT EXISTS idx_categories_user_id ON categories(user_id);
CREATE INDEX IF NOT EXISTS idx_recurring_transactions_organization_id ON recurring_transactions(organization_id);
CREATE INDEX IF NOT EXISTS idx_recurring_transactions_property_id ON recurring_transactions(property_id);
CREATE INDEX IF NOT EXISTS idx_recurring_transactions_transaction_type ON recurring_transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_pending_transactions_organization_id ON pending_transactions(organization_id);
CREATE INDEX IF NOT EXISTS idx_pending_transactions_property_id ON pending_transactions(property_id);
CREATE INDEX IF NOT EXISTS idx_pending_transactions_transaction_type ON pending_transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_pending_transactions_is_confirmed ON pending_transactions(is_confirmed);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_properties_updated_at BEFORE UPDATE ON properties
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_income_updated_at BEFORE UPDATE ON income
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_expenses_updated_at BEFORE UPDATE ON expenses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_recurring_transactions_updated_at BEFORE UPDATE ON recurring_transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pending_transactions_updated_at BEFORE UPDATE ON pending_transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE income ENABLE ROW LEVEL SECURITY;
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE recurring_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE pending_transactions ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for organizations
CREATE POLICY "Users can view organizations they belong to" ON organizations
    FOR SELECT USING (
        id IN (
            SELECT organization_id 
            FROM user_organizations 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create organizations" ON organizations
    FOR INSERT WITH CHECK (true);

-- Create RLS policies for user_organizations
CREATE POLICY "Users can view own organization memberships" ON user_organizations
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can join organizations" ON user_organizations
    FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update own organization memberships" ON user_organizations
    FOR UPDATE USING (user_id = auth.uid());

-- Create RLS policies for properties
CREATE POLICY "Users can view properties in their organizations" ON properties
    FOR SELECT USING (
        auth.uid() = user_id OR 
        organization_id IN (
            SELECT organization_id 
            FROM user_organizations 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert properties in their organizations" ON properties
    FOR INSERT WITH CHECK (
        auth.uid() = user_id AND 
        organization_id IN (
            SELECT organization_id 
            FROM user_organizations 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update properties in their organizations" ON properties
    FOR UPDATE USING (
        auth.uid() = user_id OR 
        organization_id IN (
            SELECT organization_id 
            FROM user_organizations 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete properties in their organizations" ON properties
    FOR DELETE USING (
        auth.uid() = user_id OR 
        organization_id IN (
            SELECT organization_id 
            FROM user_organizations 
            WHERE user_id = auth.uid()
        )
    );

-- Create RLS policies for income
CREATE POLICY "Users can view income in their organizations" ON income
    FOR SELECT USING (
        auth.uid() = user_id OR 
        organization_id IN (
            SELECT organization_id 
            FROM user_organizations 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert income in their organizations" ON income
    FOR INSERT WITH CHECK (
        auth.uid() = user_id AND 
        organization_id IN (
            SELECT organization_id 
            FROM user_organizations 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update income in their organizations" ON income
    FOR UPDATE USING (
        auth.uid() = user_id OR 
        organization_id IN (
            SELECT organization_id 
            FROM user_organizations 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete income in their organizations" ON income
    FOR DELETE USING (
        auth.uid() = user_id OR 
        organization_id IN (
            SELECT organization_id 
            FROM user_organizations 
            WHERE user_id = auth.uid()
        )
    );

-- Create RLS policies for expenses
CREATE POLICY "Users can view expenses in their organizations" ON expenses
    FOR SELECT USING (
        auth.uid() = user_id OR 
        organization_id IN (
            SELECT organization_id 
            FROM user_organizations 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert expenses in their organizations" ON expenses
    FOR INSERT WITH CHECK (
        auth.uid() = user_id AND 
        organization_id IN (
            SELECT organization_id 
            FROM user_organizations 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update expenses in their organizations" ON expenses
    FOR UPDATE USING (
        auth.uid() = user_id OR 
        organization_id IN (
            SELECT organization_id 
            FROM user_organizations 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete expenses in their organizations" ON expenses
    FOR DELETE USING (
        auth.uid() = user_id OR 
        organization_id IN (
            SELECT organization_id 
            FROM user_organizations 
            WHERE user_id = auth.uid()
        )
    );

-- Create RLS policies for categories
CREATE POLICY "Users can view own categories" ON categories
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own categories" ON categories
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own categories" ON categories
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own categories" ON categories
    FOR DELETE USING (auth.uid() = user_id);

-- Create RLS policies for recurring_transactions
CREATE POLICY "Users can view recurring transactions in their organizations" ON recurring_transactions
    FOR SELECT USING (
        organization_id IN (
            SELECT organization_id 
            FROM user_organizations 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert recurring transactions in their organizations" ON recurring_transactions
    FOR INSERT WITH CHECK (
        organization_id IN (
            SELECT organization_id 
            FROM user_organizations 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update recurring transactions in their organizations" ON recurring_transactions
    FOR UPDATE USING (
        organization_id IN (
            SELECT organization_id 
            FROM user_organizations 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete recurring transactions in their organizations" ON recurring_transactions
    FOR DELETE USING (
        organization_id IN (
            SELECT organization_id 
            FROM user_organizations 
            WHERE user_id = auth.uid()
        )
    );

-- Create RLS policies for pending_transactions
CREATE POLICY "Users can view pending transactions in their organizations" ON pending_transactions
    FOR SELECT USING (
        organization_id IN (
            SELECT organization_id 
            FROM user_organizations 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert pending transactions in their organizations" ON pending_transactions
    FOR INSERT WITH CHECK (
        organization_id IN (
            SELECT organization_id 
            FROM user_organizations 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update pending transactions in their organizations" ON pending_transactions
    FOR UPDATE USING (
        organization_id IN (
            SELECT organization_id 
            FROM user_organizations 
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete pending transactions in their organizations" ON pending_transactions
    FOR DELETE USING (
        organization_id IN (
            SELECT organization_id 
            FROM user_organizations 
            WHERE user_id = auth.uid()
        )
    );

-- Create views for financial reporting
CREATE OR REPLACE VIEW property_financial_summary AS
SELECT 
    p.id,
    p.user_id,
    p.name,
    p.address,
    p.monthly_rent,
    COALESCE(SUM(i.amount), 0) as total_income,
    COALESCE(SUM(e.amount), 0) as total_expenses,
    COALESCE(SUM(i.amount), 0) - COALESCE(SUM(e.amount), 0) as net_income,
    CASE 
        WHEN COALESCE(SUM(i.amount), 0) > 0 
        THEN ((COALESCE(SUM(i.amount), 0) - COALESCE(SUM(e.amount), 0)) / COALESCE(SUM(i.amount), 0)) * 100
        ELSE 0 
    END as roi_percentage
FROM properties p
LEFT JOIN income i ON p.id = i.property_id AND p.user_id = i.user_id
LEFT JOIN expenses e ON p.id = e.property_id AND p.user_id = e.user_id
GROUP BY p.id, p.user_id, p.name, p.address, p.monthly_rent;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO anon, authenticated;

-- Insert sample data for testing (optional)
-- Note: This will only work if you have a user with a specific UUID
-- You can remove this section if you don't want sample data

-- Create a function to insert sample data for the current user
CREATE OR REPLACE FUNCTION insert_sample_data()
RETURNS void AS $$
DECLARE
    current_user_id UUID;
    sample_property_id INTEGER;
BEGIN
    -- Get current user ID
    current_user_id := auth.uid();
    
    -- Only insert if user is authenticated
    IF current_user_id IS NOT NULL THEN
        -- Insert sample property
        INSERT INTO properties (user_id, name, address, property_type, purchase_price, purchase_date, monthly_rent, description)
        VALUES (
            current_user_id,
            'Sample Downtown Apartment',
            '123 Main St, Downtown, City',
            'apartment',
            250000.00,
            '2023-01-15',
            2000.00,
            '2-bedroom apartment in downtown area'
        ) RETURNING id INTO sample_property_id;
        
        -- Insert sample income
        INSERT INTO income (user_id, property_id, amount, income_type, description, transaction_date)
        VALUES 
            (current_user_id, sample_property_id, 2000.00, 'rent', 'Monthly rent payment', '2023-12-01'),
            (current_user_id, sample_property_id, 2000.00, 'rent', 'Monthly rent payment', '2023-11-01');
        
        -- Insert sample expenses
        INSERT INTO expenses (user_id, property_id, amount, expense_type, description, transaction_date)
        VALUES 
            (current_user_id, sample_property_id, 150.00, 'maintenance', 'HVAC maintenance', '2023-12-15'),
            (current_user_id, sample_property_id, 200.00, 'utilities', 'Water bill', '2023-12-10');
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permission on the function
GRANT EXECUTE ON FUNCTION insert_sample_data() TO authenticated;
