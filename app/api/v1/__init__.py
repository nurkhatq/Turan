# app/api/v1/__init__.py
from fastapi import APIRouter

# Import routers only when they exist
api_router = APIRouter()

try:
    from app.api.v1.auth import router as auth_router
    api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
except ImportError:
    pass

try:
    from app.api.v1.users import router as users_router
    api_router.include_router(users_router, prefix="/users", tags=["Users"])
except ImportError:
    pass

try:
    from app.api.v1.products import router as products_router
    api_router.include_router(products_router, prefix="/products", tags=["Products"])
except ImportError:
    pass

try:
    from app.api.v1.inventory import router as inventory_router
    api_router.include_router(inventory_router, prefix="/inventory", tags=["Inventory"])
except ImportError:
    pass

try:
    from app.api.v1.sales import router as sales_router
    api_router.include_router(sales_router, prefix="/sales", tags=["Sales"])
except ImportError:
    pass

try:
    from app.api.v1.analytics import router as analytics_router
    api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
except ImportError:
    pass

try:
    from app.api.v1.admin import router as admin_router
    api_router.include_router(admin_router, prefix="/admin", tags=["Administration"])
except ImportError:
    pass

try:
    from app.api.v1.integrations import router as integrations_router
    api_router.include_router(integrations_router, prefix="/integrations", tags=["Integrations"])
except ImportError:
    pass

try:
    from app.api.v1.organizations import router as organizations_router
    api_router.include_router(organizations_router, tags=["Organizations & Employees"])
except ImportError:
    pass

try:
    from app.api.v1.reports import router as reports_router
    api_router.include_router(reports_router, prefix="/reports", tags=["Reports"])
except ImportError:
    pass