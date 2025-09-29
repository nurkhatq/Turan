# app/models/__init__.py (COMPLETE VERSION)
"""Database models package with proper import order."""

# Import base first
from .base import Base, BaseModel, ExternalIdMixin

# Import system models
from .system import IntegrationConfig, SyncJob, ApiLog, SystemAlert, Permission

# Import user models
from .user import User, Role, UserSession

# Import MoySklad models in dependency order
from .moysklad.products import ProductFolder, UnitOfMeasure, Product, ProductVariant, Service
from .moysklad.counterparties import Counterparty
from .moysklad.inventory import Store, Stock
from .moysklad.documents import SalesDocument, SalesDocumentPosition, PurchaseDocument, PurchaseDocumentPosition
from .moysklad.organizations import (
    Organization, Employee, Project, Contract,
    Currency, PriceType, Country, EmployeeProject
)
# Import analytics models last (they depend on others)
from .analytics import ProductAnalytics, CustomerAnalytics, SalesAnalytics

# Export all models
__all__ = [
    "Base",
    "BaseModel", 
    "ExternalIdMixin",
    "IntegrationConfig",
    "SyncJob", 
    "ApiLog",
    "SystemAlert",
    "Permission",
    "User",
    "Role", 
    "UserSession",
    "ProductFolder",
    "UnitOfMeasure", 
    "Product",
    "ProductVariant",
    "Service",
    "Counterparty",
    "Store",
    "Stock", 
    "SalesDocument",
    "SalesDocumentPosition",
    "PurchaseDocument", 
    "PurchaseDocumentPosition",
    "ProductAnalytics",
    "CustomerAnalytics",
    "SalesAnalytics",
    "Organization",
    "Employee",
    "Project",
    "Contract",
    "Currency",
    "PriceType",
    "Country",
    "EmployeeProject"
]