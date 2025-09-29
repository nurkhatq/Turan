# app/api/v1/organizations.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.deps import require_admin_access, get_current_active_user
from app.schemas.common import PaginatedResponse, PaginationParams
from app.schemas.moysklad.organizations import (
    OrganizationResponse,
    EmployeeResponse,
    ProjectResponse,
    ContractResponse,
    CurrencyResponse,
    CountryResponse,
    OrganizationListFilter,
    EmployeeListFilter,
    ProjectListFilter,
    ContractListFilter
)
from app.models.moysklad.organizations import (
    Organization,
    Employee,
    Project,
    Contract,
    Currency,
    Country
)
from app.models.user import User

router = APIRouter()


@router.get("/organizations", response_model=PaginatedResponse)
async def get_organizations(
    pagination: PaginationParams = Depends(),
    filters: OrganizationListFilter = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get paginated list of organizations."""
    
    stmt = select(Organization).where(Organization.is_deleted == False)
    
    # Apply filters
    if filters.search:
        search_term = f"%{filters.search}%"
        stmt = stmt.where(
            or_(
                Organization.name.ilike(search_term),
                Organization.code.ilike(search_term),
                Organization.inn.ilike(search_term)
            )
        )
    
    if filters.archived is not None:
        stmt = stmt.where(Organization.archived == filters.archived)
    
    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()
    
    # Apply pagination
    stmt = stmt.offset((pagination.page - 1) * pagination.limit).limit(pagination.limit)
    
    # Execute query
    result = await db.execute(stmt)
    organizations = result.scalars().all()
    
    return PaginatedResponse(
        items=[OrganizationResponse.from_orm(org) for org in organizations],
        total=total,
        page=pagination.page,
        limit=pagination.limit,
        pages=(total + pagination.limit - 1) // pagination.limit
    )


@router.get("/organizations/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get organization by ID."""
    
    stmt = select(Organization).where(
        Organization.id == organization_id,
        Organization.is_deleted == False
    )
    
    result = await db.execute(stmt)
    organization = result.scalar_one_or_none()
    
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return OrganizationResponse.from_orm(organization)


@router.get("/employees", response_model=PaginatedResponse)
async def get_employees(
    pagination: PaginationParams = Depends(),
    filters: EmployeeListFilter = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get paginated list of employees."""
    
    stmt = select(Employee).where(Employee.is_deleted == False)
    
    # Apply filters
    if filters.search:
        search_term = f"%{filters.search}%"
        stmt = stmt.where(
            or_(
                Employee.full_name.ilike(search_term),
                Employee.email.ilike(search_term),
                Employee.code.ilike(search_term)
            )
        )
    
    if filters.organization_id is not None:
        stmt = stmt.where(Employee.organization_id == filters.organization_id)
    
    if filters.archived is not None:
        stmt = stmt.where(Employee.archived == filters.archived)
    
    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()
    
    # Apply pagination
    stmt = stmt.offset((pagination.page - 1) * pagination.limit).limit(pagination.limit)
    
    # Execute query
    result = await db.execute(stmt)
    employees = result.scalars().all()
    
    return PaginatedResponse(
        items=[EmployeeResponse.from_orm(emp) for emp in employees],
        total=total,
        page=pagination.page,
        limit=pagination.limit,
        pages=(total + pagination.limit - 1) // pagination.limit
    )


@router.get("/projects", response_model=PaginatedResponse)
async def get_projects(
    pagination: PaginationParams = Depends(),
    filters: ProjectListFilter = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get paginated list of projects."""
    
    stmt = select(Project).where(Project.is_deleted == False)
    
    # Apply filters
    if filters.search:
        search_term = f"%{filters.search}%"
        stmt = stmt.where(
            or_(
                Project.name.ilike(search_term),
                Project.code.ilike(search_term)
            )
        )
    
    if filters.archived is not None:
        stmt = stmt.where(Project.archived == filters.archived)
    
    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()
    
    # Apply pagination
    stmt = stmt.offset((pagination.page - 1) * pagination.limit).limit(pagination.limit)
    
    # Execute query
    result = await db.execute(stmt)
    projects = result.scalars().all()
    
    return PaginatedResponse(
        items=[ProjectResponse.from_orm(proj) for proj in projects],
        total=total,
        page=pagination.page,
        limit=pagination.limit,
        pages=(total + pagination.limit - 1) // pagination.limit
    )


@router.get("/contracts", response_model=PaginatedResponse)
async def get_contracts(
    pagination: PaginationParams = Depends(),
    filters: ContractListFilter = Depends(),
    expand: str = Query(None, description="Comma-separated list of relations to expand (counterparty,organization,project)"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get paginated list of contracts."""
    
    stmt = select(Contract).where(Contract.is_deleted == False)
    
    # Apply expand
    if expand:
        expand_list = [e.strip() for e in expand.split(',')]
        if 'counterparty' in expand_list:
            stmt = stmt.options(selectinload(Contract.counterparty))
        if 'organization' in expand_list:
            stmt = stmt.options(selectinload(Contract.organization))
        if 'project' in expand_list:
            stmt = stmt.options(selectinload(Contract.project))
    
    # Apply filters
    if filters.search:
        search_term = f"%{filters.search}%"
        stmt = stmt.where(
            or_(
                Contract.name.ilike(search_term),
                Contract.number.ilike(search_term),
                Contract.code.ilike(search_term)
            )
        )
    
    if filters.contract_type:
        stmt = stmt.where(Contract.contract_type == filters.contract_type)
    
    if filters.counterparty_id is not None:
        stmt = stmt.where(Contract.counterparty_id == filters.counterparty_id)
    
    if filters.archived is not None:
        stmt = stmt.where(Contract.archived == filters.archived)
    
    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()
    
    # Apply pagination
    stmt = stmt.offset((pagination.page - 1) * pagination.limit).limit(pagination.limit)
    
    # Execute query
    result = await db.execute(stmt)
    contracts = result.scalars().all()
    
    return PaginatedResponse(
        items=[ContractResponse.from_orm(contract) for contract in contracts],
        total=total,
        page=pagination.page,
        limit=pagination.limit,
        pages=(total + pagination.limit - 1) // pagination.limit
    )


@router.get("/currencies", response_model=List[CurrencyResponse])
async def get_currencies(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all currencies."""
    
    stmt = select(Currency).where(
        Currency.is_deleted == False,
        Currency.archived == False
    ).order_by(Currency.is_default.desc(), Currency.name)
    
    result = await db.execute(stmt)
    currencies = result.scalars().all()
    
    return [CurrencyResponse.from_orm(currency) for currency in currencies]


@router.get("/countries", response_model=List[CountryResponse])
async def get_countries(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all countries."""
    
    stmt = select(Country).where(
        Country.is_deleted == False
    ).order_by(Country.name)
    
    result = await db.execute(stmt)
    countries = result.scalars().all()
    
    return [CountryResponse.from_orm(country) for country in countries]