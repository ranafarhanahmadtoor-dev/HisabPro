from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_paid: bool
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Product Schemas
class ProductBase(BaseModel):
    name: str
    cost_price: float
    selling_price: float
    stock_quantity: int

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True

# Sale Schemas
class SaleCreate(BaseModel):
    product_id: int
    quantity: int # Input usually just calls it quantity, mapped to quantity_sold in DB

class SaleResponse(BaseModel):
    id: int
    product_name: str
    quantity_sold: int
    total_amount: float
    date: datetime
    
    class Config:
        from_attributes = True

# Payment/Transaction Schemas
class PaymentInitiate(BaseModel):
    amount: float = 1000.0
