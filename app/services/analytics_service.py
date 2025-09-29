# app/services/analytics_service.py
from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text
from sqlalchemy.orm import selectinload
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging

from app.models.moysklad.products import Product
from app.models.moysklad.counterparties import Counterparty
from app.models.moysklad.documents import SalesDocument, SalesDocumentPosition
from app.models.moysklad.inventory import Stock
from app.models.analytics import ProductAnalytics, CustomerAnalytics, SalesAnalytics
from app.schemas.analytics import (
    DashboardMetrics,
    SalesReport,
    InventoryReport,
    InventoryAnalytics,
    AnalyticsPeriod
)

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for calculating and providing business analytics."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_dashboard_metrics(self) -> DashboardMetrics:
        """Get overview metrics for dashboard."""
        logger.info("Calculating dashboard metrics")
        
        today = date.today()
        yesterday = today - timedelta(days=1)
        month_start = today.replace(day=1)
        prev_month_start = (month_start - timedelta(days=1)).replace(day=1)
        prev_month_end = month_start - timedelta(days=1)
        
        # Today's metrics
        today_revenue = await self._get_revenue_for_period(today, today)
        today_orders = await self._get_orders_count_for_period(today, today)
        today_customers = await self._get_unique_customers_for_period(today, today)
        
        # This month's metrics
        month_revenue = await self._get_revenue_for_period(month_start, today)
        month_orders = await self._get_orders_count_for_period(month_start, today)
        month_new_customers = await self._get_new_customers_for_period(month_start, today)
        
        # Previous month's metrics for growth calculation
        prev_month_revenue = await self._get_revenue_for_period(prev_month_start, prev_month_end)
        prev_month_orders = await self._get_orders_count_for_period(prev_month_start, prev_month_end)
        prev_month_customers = await self._get_new_customers_for_period(prev_month_start, prev_month_end)
        
        # Calculate growth percentages
        revenue_growth = self._calculate_growth(month_revenue, prev_month_revenue)
        orders_growth = self._calculate_growth(month_orders, prev_month_orders)
        customers_growth = self._calculate_growth(month_new_customers, prev_month_customers)
        
        # Inventory alerts
        low_stock_products = await self._count_low_stock_products()
        out_of_stock_products = await self._count_out_of_stock_products()
        
        # Top performers
        top_products = await self._get_top_products(limit=5)
        top_customers = await self._get_top_customers(limit=5)
        
        return DashboardMetrics(
            today_revenue=today_revenue,
            today_orders=today_orders,
            today_customers=today_customers,
            month_revenue=month_revenue,
            month_orders=month_orders,
            month_new_customers=month_new_customers,
            revenue_growth=revenue_growth,
            orders_growth=orders_growth,
            customers_growth=customers_growth,
            low_stock_products=low_stock_products,
            out_of_stock_products=out_of_stock_products,
            top_products=top_products,
            top_customers=top_customers
        )
    
    async def get_sales_report(self, period: AnalyticsPeriod) -> SalesReport:
        """Generate comprehensive sales report."""
        logger.info(f"Generating sales report for period {period.start_date} to {period.end_date}")
        
        # Get or calculate sales analytics for the period
        sales_analytics = await self._get_sales_analytics_for_period(period)
        
        # Get product breakdown
        products_breakdown = await self._get_product_analytics_for_period(period)
        
        # Get customer breakdown
        customers_breakdown = await self._get_customer_analytics_for_period(period)
        
        # Get daily trends
        daily_trends = await self._get_daily_sales_trends(period)
        
        # Get growth analysis
        growth_analysis = await self._get_growth_analysis(period)
        
        return SalesReport(
            period=period,
            summary=sales_analytics,
            products_breakdown=products_breakdown,
            customers_breakdown=customers_breakdown,
            daily_trends=daily_trends,
            growth_analysis=growth_analysis
        )
    
    async def get_inventory_report(self) -> InventoryReport:
        """Generate inventory analysis report."""
        logger.info("Generating inventory report")
        
        # Calculate inventory analytics
        inventory_analytics = await self._calculate_inventory_analytics()
        
        # Get product analysis
        products_analysis = await self._get_inventory_product_analysis()
        
        # Get stock movements (simplified - would need movement tracking)
        stock_movements = []
        
        # Get forecasting data (simplified)
        forecasting = await self._get_inventory_forecasting()
        
        return InventoryReport(
            generated_at=datetime.utcnow(),
            summary=inventory_analytics,
            products_analysis=products_analysis,
            stock_movements=stock_movements,
            forecasting=forecasting
        )
    
    # Helper methods for calculations
    async def _get_revenue_for_period(self, start_date: date, end_date: date) -> Decimal:
        """Get total revenue for date period."""
        stmt = select(func.coalesce(func.sum(SalesDocument.sum_total), 0)).where(
            and_(
                SalesDocument.moment >= start_date,
                SalesDocument.moment <= end_date,
                SalesDocument.applicable == True,
                SalesDocument.is_deleted == False
            )
        )
        result = await self.db.execute(stmt)
        return Decimal(str(result.scalar() or 0))
    
    async def _get_orders_count_for_period(self, start_date: date, end_date: date) -> int:
        """Get orders count for date period."""
        stmt = select(func.count(SalesDocument.id)).where(
            and_(
                SalesDocument.moment >= start_date,
                SalesDocument.moment <= end_date,
                SalesDocument.applicable == True,
                SalesDocument.is_deleted == False
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0
    
    async def _get_unique_customers_for_period(self, start_date: date, end_date: date) -> int:
        """Get unique customers count for period."""
        stmt = select(func.count(func.distinct(SalesDocument.counterparty_id))).where(
            and_(
                SalesDocument.moment >= start_date,
                SalesDocument.moment <= end_date,
                SalesDocument.applicable == True,
                SalesDocument.is_deleted == False,
                SalesDocument.counterparty_id.isnot(None)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0
    
    async def _get_new_customers_for_period(self, start_date: date, end_date: date) -> int:
        """Get new customers count for period."""
        # This is simplified - would need to track first order date
        return await self._get_unique_customers_for_period(start_date, end_date)
    
    def _calculate_growth(self, current: float, previous: float) -> Decimal:
        """Calculate growth percentage."""
        if previous == 0:
            return Decimal('0') if current == 0 else Decimal('100')
        return Decimal(str(((current - previous) / previous) * 100))
    
    async def _count_low_stock_products(self, threshold: int = 10) -> int:
        """Count products with low stock."""
        stmt = select(func.count(func.distinct(Stock.product_id))).where(
            and_(
                Stock.available <= threshold,
                Stock.available > 0,
                Stock.is_deleted == False
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0
    
    async def _count_out_of_stock_products(self) -> int:
        """Count products out of stock."""
        stmt = select(func.count(func.distinct(Stock.product_id))).where(
            and_(
                Stock.available <= 0,
                Stock.is_deleted == False
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0
    
    async def _get_top_products(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top selling products."""
        # This would need more complex query joining with sales data
        stmt = select(Product.name, Product.id).where(
            Product.is_deleted == False
        ).limit(limit)
        result = await self.db.execute(stmt)
        
        return [
            {"id": row.id, "name": row.name, "revenue": 0}
            for row in result
        ]
    
    async def _get_top_customers(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top customers by revenue."""
        # This would need more complex query
        stmt = select(Counterparty.name, Counterparty.id).where(
            and_(
                Counterparty.is_customer == True,
                Counterparty.is_deleted == False
            )
        ).limit(limit)
        result = await self.db.execute(stmt)
        
        return [
            {"id": row.id, "name": row.name, "revenue": 0}
            for row in result
        ]
    
    async def _calculate_inventory_analytics(self) -> InventoryAnalytics:
        """Calculate inventory analytics summary."""
        # Count products
        products_stmt = select(func.count(Product.id)).where(
            and_(Product.is_deleted == False, Product.archived == False)
        )
        products_result = await self.db.execute(products_stmt)
        total_products = products_result.scalar() or 0
        
        # Count variants (simplified)
        total_variants = 0
        
        # Calculate stock value (simplified)
        total_stock_value = Decimal('0')
        
        # Stock status counts
        in_stock_stmt = select(func.count(func.distinct(Stock.product_id))).where(
            and_(Stock.available > 0, Stock.is_deleted == False)
        )
        in_stock_result = await self.db.execute(in_stock_stmt)
        in_stock_count = in_stock_result.scalar() or 0
        
        low_stock_count = await self._count_low_stock_products()
        out_of_stock_count = await self._count_out_of_stock_products()
        
        return InventoryAnalytics(
            total_products=total_products,
            total_variants=total_variants,
            total_stock_value=total_stock_value,
            avg_stock_turnover=Decimal('0'),
            in_stock_count=in_stock_count,
            low_stock_count=low_stock_count,
            out_of_stock_count=out_of_stock_count,
            overstock_count=0,
            categories_breakdown=[],
            reorder_recommendations=[],
            slow_moving_products=[]
        )
    
    async def _get_inventory_product_analysis(self) -> List[Dict[str, Any]]:
        """Get product analysis for inventory report."""
        from app.schemas.analytics import InventoryProductResponse
        
        # Get products with their stock information
        stmt = select(
            Product.id,
            Product.name,
            Product.code,
            Product.sale_price,
            func.coalesce(func.sum(Stock.available), 0).label('total_stock'),
            func.coalesce(func.sum(Stock.stock), 0).label('total_stock_qty')
        ).outerjoin(Stock, Product.id == Stock.product_id).where(
            and_(
                Product.is_deleted == False,
                Product.archived == False
            )
        ).group_by(Product.id, Product.name, Product.code, Product.sale_price)
        
        result = await self.db.execute(stmt)
        
        products_analysis = []
        for row in result:
            sale_price = Decimal(str(row.sale_price)) if row.sale_price else Decimal('0')
            total_stock = Decimal(str(row.total_stock))
            total_stock_qty = Decimal(str(row.total_stock_qty))
            stock_value = sale_price * total_stock_qty
            
            products_analysis.append(InventoryProductResponse(
                id=row.id,
                name=row.name,
                code=row.code,
                sale_price=sale_price,
                total_stock=total_stock,
                total_stock_qty=total_stock_qty,
                stock_value=stock_value,
                status="in_stock" if row.total_stock > 0 else "out_of_stock"
            ))
        
        return products_analysis
    
    async def _get_inventory_forecasting(self) -> Dict[str, Any]:
        """Get inventory forecasting data."""
        # Simplified forecasting - would need historical data for proper forecasting
        return {
            "method": "simplified",
            "forecast_period": "30_days",
            "recommendations": [
                "Implement proper demand forecasting based on historical sales",
                "Set up automated reorder points",
                "Monitor seasonal trends"
            ],
            "next_review_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
    
    async def _get_sales_analytics_for_period(self, period: AnalyticsPeriod) -> SalesAnalytics:
        """Get sales analytics for a specific period."""
        # This would typically query the SalesAnalytics table or calculate on the fly
        return SalesAnalytics(
            id=0,
            period_start=datetime.combine(period.start_date, datetime.min.time()),
            period_end=datetime.combine(period.end_date, datetime.max.time()),
            period_type=period.period_type.value,
            total_revenue=await self._get_revenue_for_period(period.start_date, period.end_date),
            total_profit=Decimal('0'),  # Would need cost data
            total_orders=await self._get_orders_count_for_period(period.start_date, period.end_date),
            avg_order_value=Decimal('0'),  # Would calculate from orders
            revenue_growth_percent=Decimal('0'),
            order_growth_percent=Decimal('0'),
            metrics_data={}
        )
    
    async def _get_product_analytics_for_period(self, period: AnalyticsPeriod) -> List[Dict[str, Any]]:
        """Get product analytics for a specific period."""
        # Simplified - would need proper sales data analysis
        return []
    
    async def _get_customer_analytics_for_period(self, period: AnalyticsPeriod) -> List[Dict[str, Any]]:
        """Get customer analytics for a specific period."""
        # Simplified - would need proper customer analysis
        return []
    
    async def _get_daily_sales_trends(self, period: AnalyticsPeriod) -> List[Dict[str, Any]]:
        """Get daily sales trends for the period."""
        # Simplified - would need proper trend analysis
        return []
    
    async def _get_growth_analysis(self, period: AnalyticsPeriod) -> Dict[str, Any]:
        """Get growth analysis for the period."""
        # Simplified - would need comparison with previous period
        return {
            "revenue_growth": 0,
            "orders_growth": 0,
            "customers_growth": 0,
            "analysis": "Growth analysis requires historical data comparison"
        }