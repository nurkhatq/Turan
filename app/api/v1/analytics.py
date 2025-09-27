# app/api/v1/analytics.py
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date

from app.core.database import get_db
from app.api.deps import require_analytics_read
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import (
    DashboardMetrics,
    SalesReport,
    InventoryReport,
    AnalyticsPeriod,
    PeriodType
)
from app.models.user import User

router = APIRouter()


@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    current_user: User = Depends(require_analytics_read),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard overview metrics."""
    
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_dashboard_metrics()


@router.get("/sales/report", response_model=SalesReport)
async def get_sales_report(
    period_type: PeriodType = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user: User = Depends(require_analytics_read),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive sales report."""
    
    period = AnalyticsPeriod(
        period_type=period_type,
        start_date=start_date,
        end_date=end_date
    )
    
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_sales_report(period)


@router.get("/inventory/report", response_model=InventoryReport)
async def get_inventory_report(
    current_user: User = Depends(require_analytics_read),
    db: AsyncSession = Depends(get_db)
):
    """Get inventory analysis report."""
    
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_inventory_report()

