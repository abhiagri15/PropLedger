# PropLedger - Rental Property Management System

PropLedger is a comprehensive rental property management system built with Streamlit, Supabase, and AI-powered insights. Track income, expenses, and get intelligent recommendations for your rental property portfolio with multi-organization support.

## ✨ Features

- 🏢 **Multi-Organization Support**: Manage multiple property portfolios
- 🏠 **Property Management**: Add and manage multiple rental properties
- 💰 **Income Tracking**: Record and categorize rental income with monthly/yearly tracking
- 💸 **Expense Tracking**: Track maintenance, repairs, mortgage payments, and other expenses
- 📊 **Real-time Dashboard**: Comprehensive financial overview with P&L calculations
- 📈 **Analytics & Reports**: Visualize financial performance with interactive charts
- 🤖 **AI Insights**: Get intelligent recommendations using OpenAI GPT
- 📱 **Modern UI**: Clean, responsive interface built with Streamlit
- 🔐 **Secure Authentication**: Supabase-powered user authentication
- 📅 **Monthly/Yearly Tracking**: Track finances by month and year

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: Supabase (PostgreSQL)
- **AI**: OpenAI GPT-3.5-turbo
- **Visualization**: Plotly

## Quick Start

### 1. Prerequisites

- Python 3.8+
- Supabase account
- OpenAI API key

### 2. Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd PropLedger
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the project root:
```env
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here
OPENAI_API_KEY=your_openai_api_key_here
STREAMLIT_SERVER_PORT=8501
```

### 3. Database Setup

1. Create a new Supabase project
2. Run the SQL schema from `database/schema.sql` in your Supabase SQL editor
3. Update your `.env` file with the Supabase URL and API key

### 4. Run the Application

**Local Development:**
```bash
streamlit run app_auth.py
```

**Streamlit Cloud Deployment:**
1. Push your code to GitHub
2. Deploy to [Streamlit Cloud](https://share.streamlit.io)
3. Configure secrets in the Streamlit Cloud interface
4. See [STREAMLIT_DEPLOYMENT.md](STREAMLIT_DEPLOYMENT.md) for detailed instructions

The application will be available at `http://localhost:8501` (local) or your Streamlit Cloud URL

## Project Structure

```
PropLedger/
├── app_auth.py           # Main Streamlit application with authentication
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── env.example           # Environment variables template
├── run_auth.bat          # Windows batch file to run the app
├── database/
│   ├── __init__.py
│   ├── models.py         # Pydantic models
│   ├── supabase_client.py # Database connection
│   ├── database_operations.py # CRUD operations
│   └── complete_schema.sql # Complete database schema
├── llm/
│   ├── __init__.py
│   └── llm_insights.py   # AI insights generation
└── README.md
```

## Usage

### Getting Started
1. **Sign Up/Login**: Create an account or login with existing credentials
2. **Create Organization**: Set up your first organization for property management
3. **Select Organization**: Choose which organization to work with from the sidebar

### Managing Properties
1. Navigate to the "Properties" tab
2. Click "Add/Edit Property"
3. Fill in property details (name, address, type, purchase price, monthly rent, etc.)
4. Save the property

### Recording Income
1. Go to the "Income" tab
2. Select a property from your organization
3. Enter income details (amount, type, description)
4. Choose month and year for tracking
5. Save the record

### Tracking Expenses
1. Navigate to the "Expenses" tab
2. Select a property from your organization
3. Enter expense details (amount, type, description)
4. Choose month and year for tracking
5. Save the record

### Viewing Dashboard
1. Go to the "Dashboard" tab
2. View comprehensive financial overview:
   - Key metrics (Properties, Income, Expenses, ROI)
   - Income & Expense breakdown by type
   - Property performance cards
   - Recent transactions

### Organizations Dashboard
1. Navigate to "Organizations Dashboard"
2. View all your organizations
3. See P&L calculations for each organization
4. Create new organizations as needed

### AI Insights
1. Navigate to the "AI Insights" tab
2. Select a property
3. Generate various types of insights:
   - Financial performance analysis
   - Expense pattern analysis
   - Market insights
   - Portfolio recommendations

## Database Schema

The application uses the following main tables:

- **organizations**: Organization information for multi-tenant support
- **user_organizations**: User-organization relationships and roles
- **properties**: Rental property information (linked to organizations)
- **income**: Income transactions (linked to organizations and properties)
- **expenses**: Expense transactions (linked to organizations and properties)
- **categories**: Custom income/expense categories

### Key Features:
- **Row-Level Security (RLS)**: Data isolation between organizations
- **Multi-tenancy**: Each organization has isolated data
- **User Management**: Secure user authentication and authorization
- **Audit Trail**: Created/updated timestamps on all records

## Configuration

### Supabase Setup
1. Create a new project at [supabase.com](https://supabase.com)
2. Go to Settings > API to get your URL and anon key
3. Run the complete SQL schema from `database/complete_schema.sql` in the SQL editor
4. Enable Row-Level Security (RLS) policies for data isolation
5. Update your `.env` file with the credentials

### OpenAI Setup
1. Get an API key from [OpenAI](https://platform.openai.com/api-keys)
2. Add it to your `.env` file as `OPENAI_API_KEY`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support, please open an issue on GitHub or contact the development team.

---

Built with ❤️ using Streamlit, Supabase, and OpenAI
