-- PropLedger Database Schema for Supabase

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Properties table
CREATE TABLE IF NOT EXISTS properties (
    id SERIAL PRIMARY KEY,
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

-- Income table
CREATE TABLE IF NOT EXISTS income (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    income_type VARCHAR(50) NOT NULL CHECK (income_type IN ('rent', 'deposit', 'late_fee', 'other')),
    description TEXT NOT NULL,
    transaction_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Expenses table
CREATE TABLE IF NOT EXISTS expenses (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    expense_type VARCHAR(50) NOT NULL CHECK (expense_type IN ('maintenance', 'repairs', 'utilities', 'insurance', 'taxes', 'management', 'advertising', 'legal', 'other')),
    description TEXT NOT NULL,
    transaction_date DATE NOT NULL,
    receipt_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Categories table for custom income/expense categories
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('income', 'expense')),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_income_property_id ON income(property_id);
CREATE INDEX IF NOT EXISTS idx_income_transaction_date ON income(transaction_date);
CREATE INDEX IF NOT EXISTS idx_expenses_property_id ON expenses(property_id);
CREATE INDEX IF NOT EXISTS idx_expenses_transaction_date ON expenses(transaction_date);
CREATE INDEX IF NOT EXISTS idx_properties_property_type ON properties(property_type);

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

-- Insert sample data
INSERT INTO properties (name, address, property_type, purchase_price, purchase_date, monthly_rent, description) VALUES
('Downtown Apartment', '123 Main St, Downtown, City', 'apartment', 250000.00, '2023-01-15', 2000.00, '2-bedroom apartment in downtown area'),
('Suburban House', '456 Oak Ave, Suburb, City', 'house', 350000.00, '2023-03-20', 2500.00, '3-bedroom house in quiet neighborhood')
ON CONFLICT DO NOTHING;

INSERT INTO income (property_id, amount, income_type, description, transaction_date) VALUES
(1, 2000.00, 'rent', 'Monthly rent payment', '2023-12-01'),
(1, 2000.00, 'rent', 'Monthly rent payment', '2023-11-01'),
(2, 2500.00, 'rent', 'Monthly rent payment', '2023-12-01'),
(2, 2500.00, 'rent', 'Monthly rent payment', '2023-11-01')
ON CONFLICT DO NOTHING;

INSERT INTO expenses (property_id, amount, expense_type, description, transaction_date) VALUES
(1, 150.00, 'maintenance', 'HVAC maintenance', '2023-12-15'),
(1, 200.00, 'utilities', 'Water bill', '2023-12-10'),
(2, 300.00, 'repairs', 'Roof repair', '2023-12-05'),
(2, 180.00, 'insurance', 'Property insurance', '2023-12-01')
ON CONFLICT DO NOTHING;

-- Create views for financial reporting
CREATE OR REPLACE VIEW property_financial_summary AS
SELECT 
    p.id,
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
LEFT JOIN income i ON p.id = i.property_id
LEFT JOIN expenses e ON p.id = e.property_id
GROUP BY p.id, p.name, p.address, p.monthly_rent;

-- Grant necessary permissions (adjust based on your Supabase setup)
-- ALTER TABLE properties ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE income ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
