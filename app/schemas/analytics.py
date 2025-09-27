# app/schemas/analytics.py
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime, date
from enum import Enum


class PeriodType(str, Enum):
    """Analytics period type."""
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    quarterly = "quarterly"
    yearly = "yearly"


class AnalyticsPeriod(BaseModel):
    """Analytics period parameters."""
    period_type: PeriodType
    start_date: date
    end_date: date


class ProductAnalyticsResponse(BaseModel):
    """Product analytics response schema."""
    id: int
    product_id: Optional[int]
    variant_id: Optional[int]
    product_name: str
    period_start: datetime
    period_end: datetime
    period_type: str
    
    # Sales metrics
    sales_quantity: Decimal
    sales_revenue: Decimal
    sales_profit: Decimal
    sales_margin_percent: Decimal
    
    # Inventory metrics
    avg_stock_level: Decimal
    stock_turnover_ratio: Decimal
    days_in_stock: int
    
    # Demand metrics
    demand_frequency: int
    avg_order_quantity: Decimal
    
    class Config:
        from_attributes = True


class CustomerAnalyticsResponse(BaseModel):
    """Customer analytics response schema."""
    id: int
    counterparty_id: int
    customer_name: str
    period_start: datetime
    period_end: datetime
    period_type: str
    
    # Customer metrics
    total_orders: int
    total_revenue: Decimal
    avg_order_value: Decimal
    days_since_last_order: int
    
    # Segmentation
    customer_segment: Optional[str]
    lifetime_value: Decimal
    
    class Config:
        from_attributes = True


class SalesAnalyticsResponse(BaseModel):
    """Sales analytics response schema."""
    id: int
    period_start: datetime
    period_end: datetime
    period_type: str
    
    # Sales metrics
    total_revenue: Decimal
    total_profit: Decimal
    total_orders: int
    avg_order_value: Decimal
    
    # Growth metrics
    revenue_growth_percent: Decimal
    order_growth_percent: Decimal
    
    # Additional metrics
    metrics_data: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class DashboardMetrics(BaseModel):
    """Dashboard overview metrics."""
    # Today's metrics
    today_revenue: Decimal
    today_orders: int
    today_customers: int
    
    # This month's metrics
    month_revenue: Decimal
    month_orders: int
    month_new_customers: int
    
    # Growth compared to previous period
    revenue_growth: Decimal
    orders_growth: Decimal
    customers_growth: Decimal
    
    # Inventory alerts
    low_stock_products: int
    out_of_stock_products: int
    
    # Top performers
    top_products: List[Dict[str, Any]]
    top_customers: List[Dict[str, Any]]


class InventoryAnalytics(BaseModel):
    """Inventory analytics response."""
    total_products: int
    total_variants: int
    total_stock_value: Decimal
    avg_stock_turnover: Decimal
    
    # Stock status
    in_stock_count: int
    low_stock_count: int
    out_of_stock_count: int
    overstock_count: int
    
    # Categories breakdown
    categories_breakdown: List[Dict[str, Any]]
    
    # Recommendations
    reorder_recommendations: List[Dict[str, Any]]
    slow_moving_products: List[Dict[str, Any]]


class SalesReport(BaseModel):
    """Sales report schema."""
    period: AnalyticsPeriod
    summary: SalesAnalyticsResponse
    products_breakdown: List[ProductAnalyticsResponse]
    customers_breakdown: List[CustomerAnalyticsResponse]
    daily_trends: List[Dict[str, Any]]
    growth_analysis: Dict[str, Any]


class InventoryReport(BaseModel):
    """Inventory report schema."""
    generated_at: datetime
    summary: InventoryAnalytics
    products_analysis: List[ProductAnalyticsResponse]
    stock_movements: List[Dict[str, Any]]
    forecasting: Dict[str, Any]
