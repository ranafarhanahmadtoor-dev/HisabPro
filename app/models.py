from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime
import enum

class PaymentStatus(str, enum.Enum):
    pending = "pending"
    success = "success"
    failed = "failed"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    phone = Column(String)
    is_paid = Column(Boolean, default=False)
    
    # Relationships
    products = relationship("Product", back_populates="owner")
    sales = relationship("Sale", back_populates="user")
    payments = relationship("Payment", back_populates="user")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, index=True)
    cost_price = Column(Float)
    selling_price = Column(Float)
    stock_quantity = Column(Integer, default=0)

    owner = relationship("User", back_populates="products")
    sales = relationship("Sale", back_populates="product")

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity_sold = Column(Integer)
    date = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float) # Snapshot
    
    # Relationships
    user = relationship("User", back_populates="sales")
    product = relationship("Product", back_populates="sales")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    transaction_id = Column(String, unique=True, index=True)
    status = Column(String, default="pending") # PaymentStatus
    date = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="payments")
