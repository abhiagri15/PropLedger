import openai
from config import get_openai_api_key
import streamlit as st
from typing import List, Dict, Any
import json

class LLMInsights:
    def __init__(self):
        openai_api_key = get_openai_api_key()
        if not openai_api_key:
            st.warning("OpenAI API key not found. LLM features will be disabled.")
            self.enabled = False
        else:
            openai.api_key = openai_api_key
            self.enabled = True
    
    def generate_financial_insights(self, property_data: Dict[str, Any], financial_summary: Dict[str, Any]) -> str:
        """Generate financial insights for a property using LLM"""
        if not self.enabled:
            return "LLM features are disabled. Please configure your OpenAI API key."
        
        try:
            prompt = f"""
            Analyze the following rental property financial data and provide insights and recommendations:
            
            Property: {property_data.get('name', 'Unknown')}
            Monthly Rent: ${property_data.get('monthly_rent', 0):,.2f}
            Purchase Price: ${property_data.get('purchase_price', 0):,.2f}
            
            Financial Summary:
            - Total Income: ${financial_summary.get('total_income', 0):,.2f}
            - Total Expenses: ${financial_summary.get('total_expenses', 0):,.2f}
            - Net Income: ${financial_summary.get('net_income', 0):,.2f}
            - ROI: {financial_summary.get('roi', 0):.2f}%
            
            Please provide:
            1. Key insights about the property's performance
            2. Recommendations for improvement
            3. Potential risks or concerns
            4. Suggestions for optimizing rental income
            
            Keep the response concise and actionable.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a real estate investment advisor with expertise in rental property analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            st.error(f"Error generating insights: {str(e)}")
            return "Unable to generate insights at this time."
    
    def generate_expense_analysis(self, expenses: List[Dict[str, Any]]) -> str:
        """Analyze expense patterns and provide recommendations"""
        if not self.enabled:
            return "LLM features are disabled. Please configure your OpenAI API key."
        
        try:
            # Group expenses by type
            expense_by_type = {}
            for expense in expenses:
                expense_type = expense.get('expense_type', 'other')
                if expense_type not in expense_by_type:
                    expense_by_type[expense_type] = 0
                expense_by_type[expense_type] += expense.get('amount', 0)
            
            prompt = f"""
            Analyze the following expense breakdown for a rental property:
            
            Expense Breakdown:
            {json.dumps(expense_by_type, indent=2)}
            
            Total Expenses: ${sum(expense_by_type.values()):,.2f}
            
            Please provide:
            1. Analysis of expense patterns
            2. Identification of high-cost categories
            3. Recommendations for cost reduction
            4. Budget optimization suggestions
            
            Keep the response concise and practical.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a property management expert specializing in cost optimization."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            st.error(f"Error analyzing expenses: {str(e)}")
            return "Unable to analyze expenses at this time."
    
    def generate_rental_market_insights(self, property_data: Dict[str, Any], market_data: Dict[str, Any] = None) -> str:
        """Generate market insights for rental pricing"""
        if not self.enabled:
            return "LLM features are disabled. Please configure your OpenAI API key."
        
        try:
            prompt = f"""
            Provide rental market insights for the following property:
            
            Property Details:
            - Type: {property_data.get('property_type', 'Unknown')}
            - Location: {property_data.get('address', 'Unknown')}
            - Current Rent: ${property_data.get('monthly_rent', 0):,.2f}
            - Purchase Price: ${property_data.get('purchase_price', 0):,.2f}
            
            Please provide:
            1. Market analysis for this property type and location
            2. Rent pricing recommendations
            3. Market trends and outlook
            4. Tips for attracting quality tenants
            
            Keep the response concise and data-driven.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a real estate market analyst specializing in rental properties."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            st.error(f"Error generating market insights: {str(e)}")
            return "Unable to generate market insights at this time."
    
    def generate_investment_recommendations(self, portfolio_data: List[Dict[str, Any]]) -> str:
        """Generate investment recommendations based on portfolio data"""
        if not self.enabled:
            return "LLM features are disabled. Please configure your OpenAI API key."
        
        try:
            total_investment = sum(prop.get('purchase_price', 0) for prop in portfolio_data)
            total_monthly_income = sum(prop.get('monthly_rent', 0) for prop in portfolio_data)
            avg_roi = sum(prop.get('roi', 0) for prop in portfolio_data) / len(portfolio_data) if portfolio_data else 0
            
            prompt = f"""
            Analyze this rental property portfolio and provide investment recommendations:
            
            Portfolio Summary:
            - Number of Properties: {len(portfolio_data)}
            - Total Investment: ${total_investment:,.2f}
            - Total Monthly Income: ${total_monthly_income:,.2f}
            - Average ROI: {avg_roi:.2f}%
            
            Individual Properties:
            {json.dumps(portfolio_data, indent=2, default=str)}
            
            Please provide:
            1. Portfolio performance analysis
            2. Diversification recommendations
            3. Growth opportunities
            4. Risk assessment
            5. Next steps for portfolio expansion
            
            Keep the response comprehensive but actionable.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a real estate investment portfolio manager with expertise in rental property optimization."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            st.error(f"Error generating investment recommendations: {str(e)}")
            return "Unable to generate investment recommendations at this time."
