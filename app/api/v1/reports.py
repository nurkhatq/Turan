# app/api/v1/reports.py
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date, timedelta

from app.core.database import get_db
from app.api.deps import require_analytics_read, get_current_active_user
from app.models.user import User
from app.services.integrations.moysklad.sync_service import MoySkladSyncService

router = APIRouter()


@router.get("/dashboard/sales")
async def get_sales_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get sales dashboard from MoySklad API."""
    try:
        sync_service = MoySkladSyncService(db)
        
        async with await sync_service.create_moysklad_client() as client:
            # Get sales dashboard data from MoySklad
            dashboard_data = await client.get_sales_dashboard()
            
            return {
                "status": "success",
                "data": dashboard_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch sales dashboard: {str(e)}"
        )


@router.get("/dashboard/orders")
async def get_orders_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get orders dashboard from MoySklad API."""
    try:
        sync_service = MoySkladSyncService(db)
        
        async with await sync_service.create_moysklad_client() as client:
            # Get orders dashboard data from MoySklad
            dashboard_data = await client.get_orders_dashboard()
            
            return {
                "status": "success",
                "data": dashboard_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch orders dashboard: {str(e)}"
        )


@router.get("/dashboard/money")
async def get_money_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get money flow dashboard from MoySklad API."""
    try:
        sync_service = MoySkladSyncService(db)
        
        async with await sync_service.create_moysklad_client() as client:
            # Get money dashboard data from MoySklad
            dashboard_data = await client.get_money_dashboard()
            
            return {
                "status": "success",
                "data": dashboard_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch money dashboard: {str(e)}"
        )


@router.get("/profit/by-product")
async def get_profit_by_product(
    date_from: date = Query(..., description="Start date (YYYY-MM-DD)"),
    date_to: date = Query(..., description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(require_analytics_read),
    db: AsyncSession = Depends(get_db)
):
    """Get profit report by products from MoySklad API."""
    try:
        sync_service = MoySkladSyncService(db)
        
        # Convert dates to datetime
        start_datetime = datetime.combine(date_from, datetime.min.time())
        end_datetime = datetime.combine(date_to, datetime.max.time())
        
        async with await sync_service.create_moysklad_client() as client:
            # Get profit by product data from MoySklad
            profit_data = await client.get_profit_by_product(
                date_from=start_datetime,
                date_to=end_datetime
            )
            
            return {
                "status": "success",
                "period": {
                    "from": date_from.isoformat(),
                    "to": date_to.isoformat()
                },
                "data": profit_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch profit by product report: {str(e)}"
        )


@router.get("/profit/by-counterparty")
async def get_profit_by_counterparty(
    date_from: date = Query(..., description="Start date (YYYY-MM-DD)"),
    date_to: date = Query(..., description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(require_analytics_read),
    db: AsyncSession = Depends(get_db)
):
    """Get profit report by counterparties from MoySklad API."""
    try:
        sync_service = MoySkladSyncService(db)
        
        # Convert dates to datetime
        start_datetime = datetime.combine(date_from, datetime.min.time())
        end_datetime = datetime.combine(date_to, datetime.max.time())
        
        async with await sync_service.create_moysklad_client() as client:
            # Get profit by counterparty data from MoySklad
            profit_data = await client.get_profit_by_counterparty(
                date_from=start_datetime,
                date_to=end_datetime
            )
            
            return {
                "status": "success",
                "period": {
                    "from": date_from.isoformat(),
                    "to": date_to.isoformat()
                },
                "data": profit_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch profit by counterparty report: {str(e)}"
        )


@router.get("/turnover")
async def get_turnover_report(
    date_from: date = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: date = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(require_analytics_read),
    db: AsyncSession = Depends(get_db)
):
    """Get product turnover report from MoySklad API."""
    try:
        sync_service = MoySkladSyncService(db)
        
        # Convert dates to datetime if provided
        start_datetime = datetime.combine(date_from, datetime.min.time()) if date_from else None
        end_datetime = datetime.combine(date_to, datetime.max.time()) if date_to else None
        
        async with await sync_service.create_moysklad_client() as client:
            # Get turnover data from MoySklad
            turnover_data = await client.get_turnover_report(
                date_from=start_datetime,
                date_to=end_datetime
            )
            
            return {
                "status": "success",
                "period": {
                    "from": date_from.isoformat() if date_from else None,
                    "to": date_to.isoformat() if date_to else None
                },
                "data": turnover_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch turnover report: {str(e)}"
        )


@router.get("/stock/all")
async def get_stock_report(
    store_id: str = Query(None, description="Filter by store ID"),
    current_user: User = Depends(require_analytics_read),
    db: AsyncSession = Depends(get_db)
):
    """Get stock report from MoySklad API."""
    try:
        sync_service = MoySkladSyncService(db)
        
        async with await sync_service.create_moysklad_client() as client:
            # Get stock data from MoySklad
            stock_data = await client.get_stock(store_id=store_id)
            
            return {
                "status": "success",
                "store_id": store_id,
                "data": stock_data,
                "total_items": len(stock_data),
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch stock report: {str(e)}"
        )