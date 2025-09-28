# app/models/analytics.py (FIXED VERSION)
from sqlalchemy import Column, String, Integer, Numeric, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import BaseModel


class ProductAnalytics(BaseModel):
    """Calculated analytics for products."""
    __tablename__ = "product_analytics"
    
    # Time period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    period_type = Column(String(20), nullable=False)  # daily, weekly, monthly, yearly
    
    # Sales metrics
    sales_quantity = Column(Numeric(15, 3), default=0, nullable=False)
    sales_revenue = Column(Numeric(15, 2), default=0, nullable=False)
    sales_profit = Column(Numeric(15, 2), default=0, nullable=False)
    sales_margin_percent = Column(Numeric(5, 2), default=0, nullable=False)
    
    # Inventory metrics
    avg_stock_level = Column(Numeric(15, 3), default=0, nullable=False)
    stock_turnover_ratio = Column(Numeric(10, 2), default=0, nullable=False)
    days_in_stock = Column(Integer, default=0, nullable=False)
    
    # Demand metrics
    demand_frequency = Column(Integer, default=0, nullable=False)  # Number of orders
    avg_order_quantity = Column(Numeric(15, 3), default=0, nullable=False)
    
    # Foreign keys
    product_id = Column(Integer, ForeignKey("product.id"), nullable=True)
    variant_id = Column(Integer, ForeignKey("product_variant.id"), nullable=True)


class CustomerAnalytics(BaseModel):
    """Calculated analytics for customers."""
    __tablename__ = "customer_analytics"
    
    # Time period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    period_type = Column(String(20), nullable=False)
    
    # Customer metrics
    total_orders = Column(Integer, default=0, nullable=False)
    total_revenue = Column(Numeric(15, 2), default=0, nullable=False)
    avg_order_value = Column(Numeric(15, 2), default=0, nullable=False)
    days_since_last_order = Column(Integer, default=0, nullable=False)
    
    # Segmentation
    customer_segment = Column(String(50), nullable=True)  # VIP, Regular, New, etc.
    lifetime_value = Column(Numeric(15, 2), default=0, nullable=False)
    
    # Foreign keys
    counterparty_id = Column(Integer, ForeignKey("counterparty.id"), nullable=False)


class SalesAnalytics(BaseModel):
    """Overall sales analytics."""
    __tablename__ = "sales_analytics"
    
    # Time period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    period_type = Column(String(20), nullable=False)
    
    # Sales metrics
    total_revenue = Column(Numeric(15, 2), default=0, nullable=False)
    total_profit = Column(Numeric(15, 2), default=0, nullable=False)
    total_orders = Column(Integer, default=0, nullable=False)
    avg_order_value = Column(Numeric(15, 2), default=0, nullable=False)
    
    # Growth metrics
    revenue_growth_percent = Column(Numeric(10, 2), default=0, nullable=False)
    order_growth_percent = Column(Numeric(10, 2), default=0, nullable=False)
    
    # Additional metrics (stored as JSON)
    metrics_data = Column(JSON, nullable=True)