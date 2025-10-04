from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class PropertyType(str, Enum):
    APARTMENT = "apartment"
    HOUSE = "house"
    CONDO = "condo"
    TOWNHOUSE = "townhouse"
    COMMERCIAL = "commercial"

class IncomeType(str, Enum):
    RENT = "rent"
    DEPOSIT = "deposit"
    LATE_FEE = "late_fee"
    OTHER = "other"

class ExpenseType(str, Enum):
    MORTGAGE = "mortgage"
    MAINTENANCE = "maintenance"
    REPAIRS = "repairs"
    UTILITIES = "utilities"
    INSURANCE = "insurance"
    TAXES = "taxes"
    MANAGEMENT = "management"
    ADVERTISING = "advertising"
    LEGAL = "legal"
    OTHER = "other"

class OrganizationRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"

class Organization(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UserOrganization(BaseModel):
    id: Optional[int] = None
    user_id: str
    organization_id: int
    role: OrganizationRole = OrganizationRole.MEMBER
    joined_at: Optional[datetime] = None

class Property(BaseModel):
    id: Optional[int] = None
    organization_id: Optional[int] = None
    name: str
    address: str
    property_type: PropertyType
    purchase_price: float
    purchase_date: datetime
    monthly_rent: float
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class Income(BaseModel):
    id: Optional[int] = None
    organization_id: Optional[int] = None
    property_id: int
    amount: float
    income_type: IncomeType
    description: str
    transaction_date: datetime
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class Expense(BaseModel):
    id: Optional[int] = None
    organization_id: Optional[int] = None
    property_id: int
    amount: float
    expense_type: ExpenseType
    description: str
    transaction_date: datetime
    receipt_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class Category(BaseModel):
    id: Optional[int] = None
    name: str
    type: str  # 'income' or 'expense'
    description: Optional[str] = None
    created_at: Optional[datetime] = None
