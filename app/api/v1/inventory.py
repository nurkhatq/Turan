# app/api/v1/inventory.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.deps import require_products_read
from app.schemas.common import PaginatedResponse, PaginationParams
from app.schemas.moysklad.inventory import StockResponse, StockListFilter, StoreResponse
from app.models.moysklad.inventory import Stock, Store
from app.models.user import User

router = APIRouter()


@router.get("/stock", response_model=PaginatedResponse)
async def get_stock_levels(
    pagination: PaginationParams = Depends(),
    filters: StockListFilter = Depends(),
    current_user: User = Depends(require_products_read),
    db: AsyncSession = Depends(get_db)
):
    """Get stock levels with filters."""
    
    # Build query
    stmt = select(Stock).options(
        selectinload(Stock.product),
        selectinload(Stock.variant),
        selectinload(Stock.store)
    ).where(Stock.is_deleted == False)
    
    # Apply filters
    if filters.store_id is not None:
        stmt = stmt.where(Stock.store_id == filters.store_id)
    
    if filters.product_id is not None:
        stmt = stmt.where(Stock.product_id == filters.product_id)
    
    if filters.low_stock_threshold is not None:
        stmt = stmt.where(Stock.available <= filters.low_stock_threshold)
    
    if filters.zero_stock is True:
        stmt = stmt.where(Stock.available == 0)
    
    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()
    
    # Apply pagination
    stmt = stmt.offset((pagination.page - 1) * pagination.limit).limit(pagination.limit)
    
    # Execute query
    result = await db.execute(stmt)
    stock_items = result.scalars().all()
    
    return PaginatedResponse(
        items=[StockResponse.from_orm(s) for s in stock_items],
        total=total,
        page=pagination.page,
        limit=pagination.limit,
        pages=(total + pagination.limit - 1) // pagination.limit
    )


@router.get("/stores", response_model=List[StoreResponse])
async def get_stores(
    current_user: User = Depends(require_products_read),
    db: AsyncSession = Depends(get_db)
):
    """Get all stores/warehouses."""
    
    stmt = select(Store).where(
        Store.is_deleted == False,
        Store.archived == False
    ).order_by(Store.name)
    
    result = await db.execute(stmt)
    stores = result.scalars().all()
    
    return [StoreResponse.from_orm(s) for s in stores]
