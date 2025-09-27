# app/api/v1/products.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.redis import get_redis, RedisManager
from app.api.deps import require_products_read, require_products_write
from app.schemas.common import PaginatedResponse, PaginationParams
from app.schemas.moysklad.products import (
    ProductResponse,
    ProductListFilter,
    ServiceResponse,
    ProductFolderResponse
)
from app.models.moysklad.products import Product, Service, ProductFolder
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
async def get_products(
    pagination: PaginationParams = Depends(),
    filters: ProductListFilter = Depends(),
    current_user: User = Depends(require_products_read),
    db: AsyncSession = Depends(get_db),
    redis: RedisManager = Depends(get_redis)
):
    """Get paginated list of products with filters."""
    
    # Build query
    stmt = select(Product).options(
        selectinload(Product.folder),
        selectinload(Product.unit),
        selectinload(Product.variants)
    ).where(Product.is_deleted == False)
    
    # Apply filters
    if filters.search:
        search_term = f"%{filters.search}%"
        stmt = stmt.where(
            or_(
                Product.name.ilike(search_term),
                Product.code.ilike(search_term),
                Product.article.ilike(search_term)
            )
        )
    
    if filters.folder_id is not None:
        stmt = stmt.where(Product.folder_id == filters.folder_id)
    
    if filters.archived is not None:
        stmt = stmt.where(Product.archived == filters.archived)
    
    if filters.min_price is not None:
        stmt = stmt.where(Product.sale_price >= filters.min_price)
    
    if filters.max_price is not None:
        stmt = stmt.where(Product.sale_price <= filters.max_price)
    
    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()
    
    # Apply pagination
    stmt = stmt.offset((pagination.page - 1) * pagination.limit).limit(pagination.limit)
    
    # Execute query
    result = await db.execute(stmt)
    products = result.scalars().all()
    
    return PaginatedResponse(
        items=[ProductResponse.from_orm(p) for p in products],
        total=total,
        page=pagination.page,
        limit=pagination.limit,
        pages=(total + pagination.limit - 1) // pagination.limit
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    current_user: User = Depends(require_products_read),
    db: AsyncSession = Depends(get_db)
):
    """Get product by ID."""
    
    stmt = select(Product).options(
        selectinload(Product.folder),
        selectinload(Product.unit),
        selectinload(Product.variants),
        selectinload(Product.stock_items)
    ).where(
        Product.id == product_id,
        Product.is_deleted == False
    )
    
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return ProductResponse.from_orm(product)


@router.get("/folders/", response_model=List[ProductFolderResponse])
async def get_product_folders(
    current_user: User = Depends(require_products_read),
    db: AsyncSession = Depends(get_db)
):
    """Get all product folders."""
    
    stmt = select(ProductFolder).where(
        ProductFolder.is_deleted == False
    ).order_by(ProductFolder.name)
    
    result = await db.execute(stmt)
    folders = result.scalars().all()
    
    return [ProductFolderResponse.from_orm(f) for f in folders]
