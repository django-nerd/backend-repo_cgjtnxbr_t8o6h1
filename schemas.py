"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# Core user schema (kept from template, extended slightly)
class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: Optional[str] = Field(None, description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")
    preferred_language: str = Field("en", description="User language preference: en or ar")

# Optional example schema left for reference
class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Trading app schemas for Saudi market
class Instrument(BaseModel):
    symbol: str = Field(..., description="Ticker symbol (e.g., 2222)")
    name: str = Field(..., description="Company or fund name")
    sector: Optional[str] = Field(None, description="Sector/industry")
    market: str = Field("Tadawul", description="Market name")

class Holding(BaseModel):
    symbol: str
    quantity: float = Field(..., ge=0)
    avg_price: float = Field(..., ge=0)

class Portfolio(BaseModel):
    user_id: str
    holdings: List[Holding] = Field(default_factory=list)
    cash_sar: float = Field(0.0, ge=0, description="Cash balance in SAR")

class Order(BaseModel):
    user_id: str
    symbol: str
    side: str = Field(..., description="buy or sell")
    quantity: float = Field(..., gt=0)
    price: float = Field(..., gt=0)
    status: str = Field("submitted", description="submitted, filled, cancelled")

class Strategy(BaseModel):
    user_id: str
    name: str
    params: Dict[str, Any] = Field(default_factory=dict)
    active: bool = True

class AnalysisRequest(BaseModel):
    symbols: List[str]
    language: str = Field("en", description="en or ar")

class AnalysisInsight(BaseModel):
    symbol: str
    rsi: float
    sma_14: float
    signal: str
    summary: str
