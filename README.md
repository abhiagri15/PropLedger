# Budget & Analysis Module

A comprehensive real estate property management system with advanced budgeting, expense tracking, and financial analysis capabilities.

## 🚀 Features

### Core Functionality
- **Multi-Property Management**: Track income and expenses across multiple properties
- **Advanced Budgeting**: Create and manage budgets at company, property, and unit levels
- **CapEx Tracking**: Monitor capital expenditures with detailed categorization
- **Vendor Management**: Maintain vendor directory with spend analysis
- **Auto-Categorization**: Rule-based and ML-powered transaction categorization
- **Financial Reporting**: Comprehensive P&L, budget vs actual, and trend analysis

### Key Metrics & KPIs
- **NOI (Net Operating Income)**: Automated calculation with operating expense separation
- **OER (Operating Expense Ratio)**: Real-time expense ratio monitoring
- **DSCR (Debt Service Coverage Ratio)**: Mortgage and debt service analysis
- **CapEx Percentage**: Capital expenditure tracking as percentage of income
- **Budget Variance**: Automated variance analysis with color-coded alerts

### Advanced Features
- **Role-Based Access**: Owner, Admin, Staff, and ReadOnly permission levels
- **Audit Logging**: Complete transaction and change tracking
- **Data Import/Export**: CSV/Excel import with duplicate detection
- **Smart Filters**: Advanced transaction filtering and search
- **Tax-Ready Exports**: Formatted reports for tax preparation
- **Real-Time Analytics**: Interactive charts and trend analysis

## 🏗️ Architecture

### Tech Stack
- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python with Supabase integration
- **Database**: Supabase Postgres with Row-Level Security (RLS)
- **Authentication**: Supabase Auth with multi-company support
- **ML/AI**: Scikit-learn for auto-categorization
- **Visualization**: Plotly for interactive charts

### Database Schema
- **Companies**: Multi-tenant company management
- **Properties & Units**: Hierarchical property structure
- **Transactions**: Income/expense tracking with full audit trail
- **Budgets**: Flexible budget management at multiple levels
- **CapEx Items**: Capital expenditure tracking
- **Vendors**: Vendor management with spend analysis
- **Categories & Subcategories**: Flexible expense categorization
- **Audit Logs**: Complete change tracking

## 📦 Installation

### Prerequisites
- Python 3.11+
- Supabase account
- Git

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd budget-analysis-module
   ```

2. **Install dependencies**
   ```bash
   pip install -r app/requirements.txt
   ```

3. **Environment Configuration**
   ```bash
   # Copy environment template
   cp env.example .env
   
   # Edit .env with your Supabase credentials
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   OPENAI_API_KEY=your_openai_key  # Optional for LLM features
   ```

4. **Database Setup**
   ```bash
   # Run SQL schema and seed data
   psql -f sql/01_schema.sql
   psql -f sql/02_seed.sql
   ```

5. **Run the application**
   ```bash
   streamlit run app/app.py
   ```

## 🗄️ Database Setup

### Schema Creation
Execute the SQL files in order:
1. `sql/01_schema.sql` - Creates all tables, indexes, and RLS policies
2. `sql/02_seed.sql` - Inserts default categories and sample data

### Key Tables
- **companies**: Company information
- **properties**: Property details with occupancy rates
- **units**: Unit-level tracking
- **transactions**: All financial transactions
- **budget_lines**: Budget planning and tracking
- **capex_items**: Capital expenditure items
- **vendors**: Vendor directory
- **categories/subcategories**: Expense categorization
- **audit_logs**: Complete audit trail

### Row-Level Security (RLS)
All tables implement RLS policies ensuring:
- Users can only access their company's data
- Role-based permissions (Owner > Admin > Staff > ReadOnly)
- Secure multi-tenant architecture

## 🚀 Usage

### Getting Started
1. **Sign Up**: Create your account
2. **Create Company**: Set up your company profile
3. **Add Properties**: Register your properties
4. **Set Budgets**: Create monthly budgets
5. **Import Data**: Upload existing transactions
6. **Analyze**: View dashboards and reports

### Key Workflows

#### Property Management
1. Add properties with addresses and occupancy rates
2. Create units for each property
3. Track income and expenses by property
4. Monitor property-specific KPIs

#### Budget Management
1. Create budgets at company, property, or unit level
2. Set monthly budget amounts by category
3. Monitor budget vs actual performance
4. Use variance analysis for optimization

#### Transaction Processing
1. Add transactions manually or import via CSV/Excel
2. Auto-categorization applies rules and ML models
3. Review and correct categorizations
4. Export for tax preparation

#### CapEx Tracking
1. Log capital expenditure items
2. Track by property and unit
3. Monitor CapEx trends and budgets
4. Generate CapEx reports

### Advanced Features

#### Auto-Categorization
- **Rule-Based**: Keyword and vendor pattern matching
- **ML-Powered**: Scikit-learn models with confidence scoring
- **Hybrid Approach**: Rules first, ML fallback
- **Continuous Learning**: Model retraining with user feedback

#### Financial Analysis
- **NOI Calculation**: Automated operating income analysis
- **OER Monitoring**: Real-time expense ratio tracking
- **DSCR Analysis**: Debt service coverage monitoring
- **CapEx Analysis**: Capital expenditure trend analysis

#### Reporting & Export
- **P&L Reports**: Property and company-level profit & loss
- **Budget Reports**: Variance analysis and trend reporting
- **Tax Exports**: Formatted reports for tax preparation
- **Custom Exports**: CSV/Excel export with filtering

## 🔧 Configuration

### Environment Variables
```bash
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
OPENAI_API_KEY=your_openai_key  # Optional
```

### Streamlit Configuration
Create `.streamlit/config.toml`:
```toml
[server]
port = 8501
headless = true

[browser]
gatherUsageStats = false
```

### Supabase Setup
1. Create Supabase project
2. Enable Row-Level Security
3. Configure authentication
4. Set up storage for receipts
5. Configure email templates

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/

# Run specific test files
pytest tests/test_rules.py
pytest tests/test_ml.py
pytest tests/test_etl_import.py
```

### Test Coverage
- **Rules Engine**: Categorization rule testing
- **ML Models**: Model training and prediction testing
- **ETL Import**: Data import and validation testing
- **Database Operations**: CRUD operation testing
- **Authentication**: User and permission testing

## 📊 Performance

### Scalability
- **Users**: Supports 10-50 concurrent users
- **Transactions**: Handles 5k-50k transactions/year
- **Properties**: Scales to hundreds of properties
- **Data**: Optimized for large datasets with pagination

### Optimization
- **Database Indexes**: Optimized queries with proper indexing
- **Caching**: Streamlit caching for dashboard queries
- **Pagination**: Large table pagination for performance
- **Lazy Loading**: On-demand data loading

## 🔒 Security

### Authentication
- **Supabase Auth**: Secure user authentication
- **Multi-Factor**: Optional 2FA support
- **Session Management**: Secure session handling

### Data Protection
- **Row-Level Security**: Database-level access control
- **Encryption**: Data encryption at rest and in transit
- **Audit Logging**: Complete change tracking
- **Backup**: Automated database backups

### Compliance
- **GDPR**: Data protection compliance
- **SOC 2**: Security and availability standards
- **HIPAA**: Healthcare data protection (if applicable)

## 🚀 Deployment

### Streamlit Cloud
1. Connect GitHub repository
2. Configure environment variables
3. Deploy with one click
4. Monitor usage and performance

### Self-Hosted
1. Deploy on your infrastructure
2. Configure reverse proxy
3. Set up SSL certificates
4. Monitor and maintain

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app/app.py"]
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

### Code Standards
- **Python**: PEP 8 style guide
- **Type Hints**: Use type annotations
- **Documentation**: Docstrings for all functions
- **Testing**: Comprehensive test coverage

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Documentation
- **User Guide**: Comprehensive usage documentation
- **API Reference**: Complete API documentation
- **Tutorials**: Step-by-step tutorials
- **FAQ**: Frequently asked questions

### Community
- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: Community support and ideas
- **Discord**: Real-time community chat
- **Email**: Direct support contact

## 🔮 Roadmap

### Upcoming Features
- **Mobile App**: Native mobile application
- **Advanced Analytics**: Machine learning insights
- **Integration**: QuickBooks, Xero, and other accounting software
- **Automation**: Automated data collection and processing
- **AI Insights**: LLM-powered financial recommendations

### Long-term Vision
- **Multi-Currency**: International property management
- **Advanced Reporting**: Custom report builder
- **Workflow Automation**: Automated business processes
- **API Platform**: Third-party integrations
- **Enterprise Features**: Advanced enterprise capabilities

---

**Built with ❤️ for real estate professionals**