# app/services/integrations/moysklad/sync_service_fixed.py
"""
Complete fixed MoySklad synchronization service with proper data extraction and mapping.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, text
from sqlalchemy.dialects.postgresql import insert

from app.core.exceptions import IntegrationError
from app.services.integrations.moysklad.client import MoySkladClient
from app.models.system import IntegrationConfig
from app.models.moysklad.products import Product, ProductFolder, UnitOfMeasure, ProductVariant, Service
from app.models.moysklad.counterparties import Counterparty
from app.models.moysklad.inventory import Store, Stock

logger = logging.getLogger(__name__)


class FixedMoySkladSyncService:
    """Fixed MoySklad synchronization service with proper data handling."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.results = {
            "product_folders": {"created": 0, "updated": 0, "errors": 0},
            "units": {"created": 0, "updated": 0, "errors": 0},
            "products": {"created": 0, "updated": 0, "errors": 0},
            "services": {"created": 0, "updated": 0, "errors": 0},
            "counterparties": {"created": 0, "updated": 0, "errors": 0},
            "stores": {"created": 0, "updated": 0, "errors": 0},
            "stock": {"created": 0, "updated": 0, "errors": 0}
        }
    
    async def get_integration_config(self) -> IntegrationConfig:
        """Get MoySklad integration configuration."""
        stmt = select(IntegrationConfig).where(
            IntegrationConfig.service_name == "moysklad"
        )
        result = await self.db.execute(stmt)
        config = result.scalar_one_or_none()
        
        if not config:
            raise IntegrationError("MoySklad integration not configured")
        
        if not config.is_enabled:
            raise IntegrationError("MoySklad integration is not enabled")
        
        return config
    
    async def create_moysklad_client(self) -> MoySkladClient:
        """Create MoySklad client from configuration."""
        config = await self.get_integration_config()
        
        credentials = config.credentials_data or {}
        
        # Handle case where credentials_data is stored as JSON string
        if isinstance(credentials, str):
            try:
                credentials = json.loads(credentials)
            except (json.JSONDecodeError, TypeError):
                credentials = {}
        
        token = credentials.get("token")
        username = credentials.get("username")
        password = credentials.get("password")
        
        if not token and not (username and password):
            raise IntegrationError(
                "MoySklad credentials not configured. Please provide token or username/password."
            )
        
        return MoySkladClient(
            token=token,
            username=username,
            password=password
        )
    
    def extract_id_from_meta_or_href(self, obj: Any) -> Optional[str]:
        """Extract ID from MoySklad meta object or direct href."""
        if not obj:
            return None
        
        # If it's a string (href), extract ID from it
        if isinstance(obj, str):
            return obj.split("/")[-1] if obj else None
        
        # If it's an object with meta
        if isinstance(obj, dict):
            meta = obj.get("meta", {})
            href = meta.get("href", "")
            if href:
                return href.split("/")[-1]
        
        return None
    
    def extract_price_value(self, price_obj: Any, default: float = 0) -> float:
        """Extract price value from MoySklad price object."""
        if not price_obj:
            return default
        
        if isinstance(price_obj, (int, float)):
            return float(price_obj) / 100  # Convert kopecks to rubles
        
        if isinstance(price_obj, dict):
            value = price_obj.get("value", default)
            return float(value) / 100 if value else default
        
        return default
    
    def extract_sale_prices(self, sale_prices: List[Dict]) -> float:
        """Extract first sale price from salePrices array."""
        if not sale_prices or not isinstance(sale_prices, list):
            return 0
        
        if len(sale_prices) > 0:
            return self.extract_price_value(sale_prices[0])
        
        return 0
    
    async def sync_product_folders(self, client: MoySkladClient) -> None:
        """Sync product folders/categories."""
        logger.info("📁 Syncing product folders...")
        
        try:
            folders_data = await client.get_product_folders()
            logger.info(f"Found {len(folders_data)} product folders")
            
            for folder_data in folders_data:
                try:
                    folder_id = folder_data.get("id")
                    if not folder_id:
                        continue
                    
                    # Extract parent folder ID if exists
                    parent_external_id = None
                    if "productFolder" in folder_data:
                        parent_external_id = self.extract_id_from_meta_or_href(
                            folder_data["productFolder"]
                        )
                    
                    # Upsert folder
                    stmt = insert(ProductFolder).values(
                        external_id=folder_id,
                        name=folder_data.get("name", ""),
                        code=folder_data.get("code"),
                        description=folder_data.get("description"),
                        path_name=folder_data.get("pathName", ""),
                        parent_external_id=parent_external_id,
                        archived=folder_data.get("archived", False),
                        last_sync_at=datetime.utcnow()
                    ).on_conflict_do_update(
                        index_elements=["external_id"],
                        set_=dict(
                            name=folder_data.get("name", ""),
                            code=folder_data.get("code"),
                            description=folder_data.get("description"),
                            path_name=folder_data.get("pathName", ""),
                            parent_external_id=parent_external_id,
                            archived=folder_data.get("archived", False),
                            last_sync_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                    )
                    
                    result = await self.db.execute(stmt)
                    if result.rowcount > 0:
                        self.results["product_folders"]["created"] += 1
                    else:
                        self.results["product_folders"]["updated"] += 1
                    
                except Exception as e:
                    logger.error(f"Error syncing folder {folder_data.get('id', 'unknown')}: {e}")
                    self.results["product_folders"]["errors"] += 1
            
            await self.db.commit()
            logger.info(f"✅ Product folders sync completed: {self.results['product_folders']}")
            
        except Exception as e:
            logger.error(f"❌ Product folders sync failed: {e}")
            await self.db.rollback()
            raise
    
    async def sync_units_of_measure(self, client: MoySkladClient) -> None:
        """Sync units of measure."""
        logger.info("📏 Syncing units of measure...")
        
        try:
            units_data = await client.get_units_of_measure()
            logger.info(f"Found {len(units_data)} units of measure")
            
            for unit_data in units_data:
                try:
                    unit_id = unit_data.get("id")
                    if not unit_id:
                        continue
                    
                    # Upsert unit
                    stmt = insert(UnitOfMeasure).values(
                        external_id=unit_id,
                        name=unit_data.get("name", ""),
                        code=unit_data.get("code"),
                        description=unit_data.get("description"),
                        last_sync_at=datetime.utcnow()
                    ).on_conflict_do_update(
                        index_elements=["external_id"],
                        set_=dict(
                            name=unit_data.get("name", ""),
                            code=unit_data.get("code"),
                            description=unit_data.get("description"),
                            last_sync_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                    )
                    
                    result = await self.db.execute(stmt)
                    if result.rowcount > 0:
                        self.results["units"]["created"] += 1
                    else:
                        self.results["units"]["updated"] += 1
                    
                except Exception as e:
                    logger.error(f"Error syncing unit {unit_data.get('id', 'unknown')}: {e}")
                    self.results["units"]["errors"] += 1
            
            await self.db.commit()
            logger.info(f"✅ Units sync completed: {self.results['units']}")
            
        except Exception as e:
            logger.error(f"❌ Units sync failed: {e}")
            await self.db.rollback()
            raise
    
    async def sync_products(self, client: MoySkladClient) -> None:
        """Sync products from MoySklad with fixed data extraction."""
        logger.info("🛍️ Syncing products...")
        
        try:
            products_data = await client.get_products()
            logger.info(f"Found {len(products_data)} products")
            
            for product_data in products_data:
                try:
                    product_id = product_data.get("id")
                    if not product_id:
                        continue
                    
                    # FIXED: Extract prices properly
                    sale_price = 0
                    buy_price = 0
                    min_price = 0
                    
                    # Extract sale price from salePrices array
                    if "salePrices" in product_data and product_data["salePrices"]:
                        sale_price = self.extract_sale_prices(product_data["salePrices"])
                    
                    # Extract buy price
                    if "buyPrice" in product_data:
                        buy_price = self.extract_price_value(product_data["buyPrice"])
                    
                    # Extract min price
                    if "minPrice" in product_data:
                        min_price = self.extract_price_value(product_data["minPrice"])
                    
                    # FIXED: Extract external IDs for relationships
                    folder_external_id = None
                    if "productFolder" in product_data:
                        folder_external_id = self.extract_id_from_meta_or_href(
                            product_data["productFolder"]
                        )
                    
                    unit_external_id = None
                    if "uom" in product_data:
                        unit_external_id = self.extract_id_from_meta_or_href(
                            product_data["uom"]
                        )
                    
                    supplier_external_id = None
                    if "supplier" in product_data:
                        supplier_external_id = self.extract_id_from_meta_or_href(
                            product_data["supplier"]
                        )
                    
                    # Upsert product
                    stmt = insert(Product).values(
                        external_id=product_id,
                        name=product_data.get("name", ""),
                        code=product_data.get("code"),
                        article=product_data.get("article"),
                        description=product_data.get("description"),
                        sale_price=sale_price,
                        buy_price=buy_price,
                        min_price=min_price,
                        weight=product_data.get("weight", 0) / 1000 if product_data.get("weight") else None,
                        volume=product_data.get("volume", 0) / 1000000 if product_data.get("volume") else None,
                        archived=product_data.get("archived", False),
                        shared=product_data.get("shared", True),
                        folder_external_id=folder_external_id,
                        unit_external_id=unit_external_id,
                        supplier_external_id=supplier_external_id,
                        last_sync_at=datetime.utcnow()
                    ).on_conflict_do_update(
                        index_elements=["external_id"],
                        set_=dict(
                            name=product_data.get("name", ""),
                            code=product_data.get("code"),
                            article=product_data.get("article"),
                            description=product_data.get("description"),
                            sale_price=sale_price,
                            buy_price=buy_price,
                            min_price=min_price,
                            weight=product_data.get("weight", 0) / 1000 if product_data.get("weight") else None,
                            volume=product_data.get("volume", 0) / 1000000 if product_data.get("volume") else None,
                            archived=product_data.get("archived", False),
                            shared=product_data.get("shared", True),
                            folder_external_id=folder_external_id,
                            unit_external_id=unit_external_id,
                            supplier_external_id=supplier_external_id,
                            last_sync_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                    )
                    
                    result = await self.db.execute(stmt)
                    if result.rowcount > 0:
                        self.results["products"]["created"] += 1
                    else:
                        self.results["products"]["updated"] += 1
                    
                except Exception as e:
                    logger.error(f"Error syncing product {product_data.get('id', 'unknown')}: {e}")
                    self.results["products"]["errors"] += 1
            
            await self.db.commit()
            logger.info(f"✅ Products sync completed: {self.results['products']}")
            
        except Exception as e:
            logger.error(f"❌ Products sync failed: {e}")
            await self.db.rollback()
            raise
    
    async def sync_services(self, client: MoySkladClient) -> None:
        """Sync services from MoySklad."""
        logger.info("🔧 Syncing services...")
        
        try:
            services_data = await client.get_services()
            logger.info(f"Found {len(services_data)} services")
            
            for service_data in services_data:
                try:
                    service_id = service_data.get("id")
                    if not service_id:
                        continue
                    
                    # Extract prices
                    sale_price = 0
                    buy_price = 0
                    min_price = 0
                    
                    if "salePrices" in service_data and service_data["salePrices"]:
                        sale_price = self.extract_sale_prices(service_data["salePrices"])
                    
                    if "buyPrice" in service_data:
                        buy_price = self.extract_price_value(service_data["buyPrice"])
                    
                    if "minPrice" in service_data:
                        min_price = self.extract_price_value(service_data["minPrice"])
                    
                    # Extract external IDs
                    folder_external_id = None
                    if "productFolder" in service_data:
                        folder_external_id = self.extract_id_from_meta_or_href(
                            service_data["productFolder"]
                        )
                    
                    unit_external_id = None
                    if "uom" in service_data:
                        unit_external_id = self.extract_id_from_meta_or_href(
                            service_data["uom"]
                        )
                    
                    # Upsert service
                    stmt = insert(Service).values(
                        external_id=service_id,
                        name=service_data.get("name", ""),
                        code=service_data.get("code"),
                        description=service_data.get("description"),
                        sale_price=sale_price,
                        buy_price=buy_price,
                        min_price=min_price,
                        archived=service_data.get("archived", False),
                        shared=service_data.get("shared", True),
                        folder_external_id=folder_external_id,
                        unit_external_id=unit_external_id,
                        last_sync_at=datetime.utcnow()
                    ).on_conflict_do_update(
                        index_elements=["external_id"],
                        set_=dict(
                            name=service_data.get("name", ""),
                            code=service_data.get("code"),
                            description=service_data.get("description"),
                            sale_price=sale_price,
                            buy_price=buy_price,
                            min_price=min_price,
                            archived=service_data.get("archived", False),
                            shared=service_data.get("shared", True),
                            folder_external_id=folder_external_id,
                            unit_external_id=unit_external_id,
                            last_sync_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                    )
                    
                    result = await self.db.execute(stmt)
                    if result.rowcount > 0:
                        self.results["services"]["created"] += 1
                    else:
                        self.results["services"]["updated"] += 1
                    
                except Exception as e:
                    logger.error(f"Error syncing service {service_data.get('id', 'unknown')}: {e}")
                    self.results["services"]["errors"] += 1
            
            await self.db.commit()
            logger.info(f"✅ Services sync completed: {self.results['services']}")
            
        except Exception as e:
            logger.error(f"❌ Services sync failed: {e}")
            await self.db.rollback()
            raise
    
    async def sync_counterparties(self, client: MoySkladClient) -> None:
        """Sync counterparties from MoySklad."""
        logger.info("🤝 Syncing counterparties...")
        
        try:
            counterparties_data = await client.get_counterparties()
            logger.info(f"Found {len(counterparties_data)} counterparties")
            
            for cp_data in counterparties_data:
                try:
                    cp_id = cp_data.get("id")
                    if not cp_id:
                        continue
                    
                    # Extract contact info from contactpersons
                    email = ""
                    phone = ""
                    if "contactpersons" in cp_data and isinstance(cp_data["contactpersons"], list):
                        if len(cp_data["contactpersons"]) > 0:
                            contact = cp_data["contactpersons"][0]
                            email = contact.get("email", "")
                            phone = contact.get("phone", "")
                    
                    # Extract addresses
                    legal_address = ""
                    actual_address = ""
                    
                    if "legalAddress" in cp_data and cp_data["legalAddress"]:
                        legal_address = cp_data["legalAddress"].get("addInfo", "")
                    
                    if "actualAddress" in cp_data and cp_data["actualAddress"]:
                        actual_address = cp_data["actualAddress"].get("addInfo", "")
                    
                    # Upsert counterparty
                    stmt = insert(Counterparty).values(
                        external_id=cp_id,
                        name=cp_data.get("name", ""),
                        code=cp_data.get("code"),
                        description=cp_data.get("description"),
                        email=email or cp_data.get("email"),
                        phone=phone or cp_data.get("phone"),
                        legal_title=cp_data.get("legalTitle"),
                        legal_address=legal_address,
                        actual_address=actual_address,
                        inn=cp_data.get("inn"),
                        kpp=cp_data.get("kpp"),
                        ogrn=cp_data.get("ogrn"),
                        okpo=cp_data.get("okpo"),
                        is_supplier=cp_data.get("supplier", False),
                        is_customer=not cp_data.get("supplier", False),  # Assume customer if not supplier
                        discount_percentage=cp_data.get("discountCardNumber", 0),
                        archived=cp_data.get("archived", False),
                        shared=cp_data.get("shared", True),
                        last_sync_at=datetime.utcnow()
                    ).on_conflict_do_update(
                        index_elements=["external_id"],
                        set_=dict(
                            name=cp_data.get("name", ""),
                            code=cp_data.get("code"),
                            description=cp_data.get("description"),
                            email=email or cp_data.get("email"),
                            phone=phone or cp_data.get("phone"),
                            legal_title=cp_data.get("legalTitle"),
                            legal_address=legal_address,
                            actual_address=actual_address,
                            inn=cp_data.get("inn"),
                            kpp=cp_data.get("kpp"),
                            ogrn=cp_data.get("ogrn"),
                            okpo=cp_data.get("okpo"),
                            is_supplier=cp_data.get("supplier", False),
                            is_customer=not cp_data.get("supplier", False),
                            discount_percentage=cp_data.get("discountCardNumber", 0),
                            archived=cp_data.get("archived", False),
                            shared=cp_data.get("shared", True),
                            last_sync_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                    )
                    
                    result = await self.db.execute(stmt)
                    if result.rowcount > 0:
                        self.results["counterparties"]["created"] += 1
                    else:
                        self.results["counterparties"]["updated"] += 1
                    
                except Exception as e:
                    logger.error(f"Error syncing counterparty {cp_data.get('id', 'unknown')}: {e}")
                    self.results["counterparties"]["errors"] += 1
            
            await self.db.commit()
            logger.info(f"✅ Counterparties sync completed: {self.results['counterparties']}")
            
        except Exception as e:
            logger.error(f"❌ Counterparties sync failed: {e}")
            await self.db.rollback()
            raise
    
    async def sync_stores(self, client: MoySkladClient) -> None:
        """Sync stores/warehouses from MoySklad."""
        logger.info("🏪 Syncing stores...")
        
        try:
            stores_data = await client.get_stores()
            logger.info(f"Found {len(stores_data)} stores")
            
            for store_data in stores_data:
                try:
                    store_id = store_data.get("id")
                    if not store_id:
                        continue
                    
                    # Extract address
                    address = ""
                    if "address" in store_data and store_data["address"]:
                        address = store_data["address"].get("addInfo", "")
                    
                    # Upsert store
                    stmt = insert(Store).values(
                        external_id=store_id,
                        name=store_data.get("name", ""),
                        code=store_data.get("code"),
                        description=store_data.get("description"),
                        address=address,
                        archived=store_data.get("archived", False),
                        last_sync_at=datetime.utcnow()
                    ).on_conflict_do_update(
                        index_elements=["external_id"],
                        set_=dict(
                            name=store_data.get("name", ""),
                            code=store_data.get("code"),
                            description=store_data.get("description"),
                            address=address,
                            archived=store_data.get("archived", False),
                            last_sync_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                    )
                    
                    result = await self.db.execute(stmt)
                    if result.rowcount > 0:
                        self.results["stores"]["created"] += 1
                    else:
                        self.results["stores"]["updated"] += 1
                    
                except Exception as e:
                    logger.error(f"Error syncing store {store_data.get('id', 'unknown')}: {e}")
                    self.results["stores"]["errors"] += 1
            
            await self.db.commit()
            logger.info(f"✅ Stores sync completed: {self.results['stores']}")
            
        except Exception as e:
            logger.error(f"❌ Stores sync failed: {e}")
            await self.db.rollback()
            raise
    
    async def sync_stock(self, client: MoySkladClient) -> None:
        """Sync stock levels from MoySklad."""
        logger.info("📦 Syncing stock levels...")
        
        try:
            stock_data = await client.get_stock()
            logger.info(f"Found {len(stock_data)} stock records")
            
            for stock_item in stock_data:
                try:
                    # Extract IDs from stock report
                    product_external_id = self.extract_id_from_meta_or_href(stock_item)
                    store_external_id = None
                    
                    # For stock report, the store info might be in stockByStore
                    if "stockByStore" in stock_item and stock_item["stockByStore"]:
                        store_info = stock_item["stockByStore"][0] if isinstance(stock_item["stockByStore"], list) else stock_item["stockByStore"]
                        if "store" in store_info:
                            store_external_id = self.extract_id_from_meta_or_href(store_info["store"])
                    
                    if not product_external_id:
                        continue
                    
                    # Extract quantities - convert from units to decimal
                    stock_qty = float(stock_item.get("stock", 0))
                    reserve_qty = float(stock_item.get("reserve", 0))
                    in_transit_qty = float(stock_item.get("inTransit", 0))
                    available_qty = float(stock_item.get("quantity", 0))
                    
                    # Extract prices
                    price = self.extract_price_value(stock_item.get("price"))
                    sale_price = self.extract_price_value(stock_item.get("salePrice"))
                    
                    # Create unique external_id for stock record
                    stock_external_id = f"{product_external_id}_{store_external_id or 'default'}"
                    
                    # Upsert stock
                    stmt = insert(Stock).values(
                        external_id=stock_external_id,
                        product_external_id=product_external_id,
                        store_external_id=store_external_id,
                        stock=stock_qty,
                        reserve=reserve_qty,
                        in_transit=in_transit_qty,
                        available=available_qty,
                        price=price,
                        sale_price=sale_price,
                        last_sync_at=datetime.utcnow()
                    ).on_conflict_do_update(
                        index_elements=["external_id"],
                        set_=dict(
                            product_external_id=product_external_id,
                            store_external_id=store_external_id,
                            stock=stock_qty,
                            reserve=reserve_qty,
                            in_transit=in_transit_qty,
                            available=available_qty,
                            price=price,
                            sale_price=sale_price,
                            last_sync_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                    )
                    
                    result = await self.db.execute(stmt)
                    if result.rowcount > 0:
                        self.results["stock"]["created"] += 1
                    else:
                        self.results["stock"]["updated"] += 1
                    
                except Exception as e:
                    logger.error(f"Error syncing stock item: {e}")
                    self.results["stock"]["errors"] += 1
            
            await self.db.commit()
            logger.info(f"✅ Stock sync completed: {self.results['stock']}")
            
        except Exception as e:
            logger.error(f"❌ Stock sync failed: {e}")
            await self.db.rollback()
            raise
    
    async def update_foreign_key_relationships(self) -> None:
        """Update foreign key relationships after all entities are synced."""
        logger.info("🔗 Updating foreign key relationships...")
        
        try:
            # Update product folder relationships
            await self.db.execute(text("""
                UPDATE product SET folder_id = pf.id
                FROM product_folder pf
                WHERE product.folder_external_id = pf.external_id
                AND product.folder_id IS NULL
            """))
            
            # Update product unit relationships
            await self.db.execute(text("""
                UPDATE product SET unit_id = uom.id
                FROM unit_of_measure uom
                WHERE product.unit_external_id = uom.external_id
                AND product.unit_id IS NULL
            """))
            
            # Update service folder relationships
            await self.db.execute(text("""
                UPDATE service SET folder_id = pf.id
                FROM product_folder pf
                WHERE service.folder_external_id = pf.external_id
                AND service.folder_id IS NULL
            """))
            
            # Update service unit relationships
            await self.db.execute(text("""
                UPDATE service SET unit_id = uom.id
                FROM unit_of_measure uom
                WHERE service.unit_external_id = uom.external_id
                AND service.unit_id IS NULL
            """))
            
            # Update stock product relationships
            await self.db.execute(text("""
                UPDATE stock SET product_id = p.id
                FROM product p
                WHERE stock.product_external_id = p.external_id
                AND stock.product_id IS NULL
            """))
            
            # Update stock store relationships
            await self.db.execute(text("""
                UPDATE stock SET store_id = s.id
                FROM store s
                WHERE stock.store_external_id = s.external_id
                AND stock.store_id IS NULL
            """))
            
            await self.db.commit()
            logger.info("✅ Foreign key relationships updated")
            
        except Exception as e:
            logger.error(f"❌ Failed to update foreign key relationships: {e}")
            await self.db.rollback()
            raise
    
    async def full_sync(self) -> Dict[str, Any]:
        """Perform complete full synchronization with proper error handling."""
        logger.info("🚀 Starting complete MoySklad full synchronization...")
        start_time = datetime.utcnow()
        
        try:
            async with await self.create_moysklad_client() as client:
                # Test connection first
                connection_test = await client.test_connection()
                if not connection_test.get("success"):
                    raise IntegrationError(f"Connection test failed: {connection_test.get('message')}")
                
                logger.info(f"✅ Connection test passed: {connection_test.get('message')}")
                
                # Sync in dependency order
                await self.sync_units_of_measure(client)
                await self.sync_product_folders(client)
                await self.sync_stores(client)
                await self.sync_products(client)
                await self.sync_services(client)
                await self.sync_counterparties(client)
                await self.sync_stock(client)
                
                # Update foreign key relationships
                await self.update_foreign_key_relationships()
                
                # Calculate totals
                total_created = sum(entity["created"] for entity in self.results.values())
                total_updated = sum(entity["updated"] for entity in self.results.values())
                total_errors = sum(entity["errors"] for entity in self.results.values())
                
                duration = datetime.utcnow() - start_time
                
                result = {
                    "status": "completed",
                    "duration_seconds": duration.total_seconds(),
                    "summary": {
                        "total_created": total_created,
                        "total_updated": total_updated,
                        "total_errors": total_errors
                    },
                    "details": self.results,
                    "connection_test": connection_test
                }
                
                logger.info(f"🎉 Full sync completed successfully in {duration.total_seconds():.2f}s")
                logger.info(f"📊 Summary: {total_created} created, {total_updated} updated, {total_errors} errors")
                
                return result
                
        except Exception as e:
            duration = datetime.utcnow() - start_time
            logger.error(f"❌ Full sync failed after {duration.total_seconds():.2f}s: {e}")
            raise
    
    async def incremental_sync(self) -> Dict[str, Any]:
        """Perform incremental synchronization."""
        logger.info("🔄 Starting incremental MoySklad synchronization...")
        start_time = datetime.utcnow()
        
        try:
            # Get last sync time (default to 24 hours ago)
            since = start_time - timedelta(hours=24)
            
            async with await self.create_moysklad_client() as client:
                # Only sync main entities for incremental
                await self.sync_products(client)
                await self.sync_services(client)
                await self.sync_counterparties(client)
                await self.sync_stock(client)
                
                # Update relationships
                await self.update_foreign_key_relationships()
                
                duration = datetime.utcnow() - start_time
                total_updated = sum(entity["updated"] + entity["created"] for entity in self.results.values())
                
                result = {
                    "status": "completed",
                    "duration_seconds": duration.total_seconds(),
                    "updated_since": since.isoformat(),
                    "total_updated": total_updated,
                    "details": self.results
                }
                
                logger.info(f"✅ Incremental sync completed in {duration.total_seconds():.2f}s")
                return result
                
        except Exception as e:
            duration = datetime.utcnow() - start_time
            logger.error(f"❌ Incremental sync failed after {duration.total_seconds():.2f}s: {e}")
            raise