# app/services/integrations/moysklad/sync_service_complete.py
"""
Complete MoySklad synchronization service that actually fetches and saves real data.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from app.core.exceptions import IntegrationError
from app.services.integrations.moysklad.client import MoySkladClient
from app.models.system import IntegrationConfig
from app.models.moysklad.products import Product, ProductFolder, UnitOfMeasure, ProductVariant, Service
from app.models.moysklad.counterparties import Counterparty
from app.models.moysklad.inventory import Store, Stock
from app.models.moysklad.documents import SalesDocument, SalesDocumentPosition

logger = logging.getLogger(__name__)


class CompleteMoySkladSyncService:
    """Complete MoySklad synchronization service with real data fetching."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.results = {
            "products": {"created": 0, "updated": 0, "errors": 0},
            "services": {"created": 0, "updated": 0, "errors": 0},
            "counterparties": {"created": 0, "updated": 0, "errors": 0},
            "stores": {"created": 0, "updated": 0, "errors": 0},
            "stock": {"created": 0, "updated": 0, "errors": 0},
            "folders": {"created": 0, "updated": 0, "errors": 0},
            "units": {"created": 0, "updated": 0, "errors": 0}
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
            import json
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
    
    async def sync_product_folders(self, client: MoySkladClient) -> None:
        """Sync product folders/categories."""
        logger.info("📁 Syncing product folders...")
        
        try:
            folders_data = await client.get_paginated("entity/productfolder")
            logger.info(f"Found {len(folders_data)} product folders")
            
            for folder_data in folders_data:
                try:
                    folder_id = folder_data.get("id")
                    if not folder_id:
                        continue
                    
                    # Upsert folder
                    stmt = insert(ProductFolder).values(
                        external_id=folder_id,
                        name=folder_data.get("name", ""),
                        description=folder_data.get("description"),
                        path_name=folder_data.get("pathName", ""),
                        archived=folder_data.get("archived", False),
                        last_sync_at=datetime.utcnow()
                    ).on_conflict_do_update(
                        index_elements=["external_id"],
                        set_=dict(
                            name=folder_data.get("name", ""),
                            description=folder_data.get("description"),
                            path_name=folder_data.get("pathName", ""),
                            archived=folder_data.get("archived", False),
                            last_sync_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                    )
                    
                    result = await self.db.execute(stmt)
                    if result.rowcount > 0:
                        if hasattr(result, 'inserted_primary_key'):
                            self.results["folders"]["created"] += 1
                        else:
                            self.results["folders"]["updated"] += 1
                    
                except Exception as e:
                    logger.error(f"Error syncing folder {folder_data.get('id', 'unknown')}: {e}")
                    self.results["folders"]["errors"] += 1
            
            await self.db.commit()
            logger.info(f"✅ Product folders sync completed: {self.results['folders']}")
            
        except Exception as e:
            logger.error(f"❌ Product folders sync failed: {e}")
            await self.db.rollback()
            raise
    
    async def sync_units_of_measure(self, client: MoySkladClient) -> None:
        """Sync units of measure."""
        logger.info("📏 Syncing units of measure...")
        
        try:
            units_data = await client.get_paginated("entity/uom")
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
                        description=unit_data.get("description"),
                        last_sync_at=datetime.utcnow()
                    ).on_conflict_do_update(
                        index_elements=["external_id"],
                        set_=dict(
                            name=unit_data.get("name", ""),
                            description=unit_data.get("description"),
                            last_sync_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                    )
                    
                    result = await self.db.execute(stmt)
                    if result.rowcount > 0:
                        if hasattr(result, 'inserted_primary_key'):
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
        """Sync products from MoySklad."""
        logger.info("🛍️ Syncing products...")
        
        try:
            products_data = await client.get_products()
            logger.info(f"Found {len(products_data)} products")
            
            for product_data in products_data:
                try:
                    product_id = product_data.get("id")
                    if not product_id:
                        continue
                    
                    # Extract price from salePrices
                    sale_price = 0
                    if "salePrices" in product_data and product_data["salePrices"]:
                        sale_price = product_data["salePrices"][0].get("value", 0) / 100  # Convert kopecks to rubles
                    
                    # Extract folder reference
                    folder_id = None
                    if "productFolder" in product_data and product_data["productFolder"]:
                        folder_meta = product_data["productFolder"].get("meta", {})
                        folder_href = folder_meta.get("href", "")
                        if folder_href:
                            folder_id = folder_href.split("/")[-1]
                    
                    # Extract unit reference
                    unit_id = None
                    if "uom" in product_data and product_data["uom"]:
                        unit_meta = product_data["uom"].get("meta", {})
                        unit_href = unit_meta.get("href", "")
                        if unit_href:
                            unit_id = unit_href.split("/")[-1]
                    
                    # Upsert product
                    stmt = insert(Product).values(
                        external_id=product_id,
                        name=product_data.get("name", ""),
                        description=product_data.get("description"),
                        code=product_data.get("code"),
                        article=product_data.get("article"),
                        sale_price=sale_price,
                        archived=product_data.get("archived", False),
                        folder_external_id=folder_id,
                        unit_external_id=unit_id,
                        last_sync_at=datetime.utcnow()
                    ).on_conflict_do_update(
                        index_elements=["external_id"],
                        set_=dict(
                            name=product_data.get("name", ""),
                            description=product_data.get("description"),
                            code=product_data.get("code"),
                            article=product_data.get("article"),
                            sale_price=sale_price,
                            archived=product_data.get("archived", False),
                            folder_external_id=folder_id,
                            unit_external_id=unit_id,
                            last_sync_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                    )
                    
                    result = await self.db.execute(stmt)
                    if result.rowcount > 0:
                        if hasattr(result, 'inserted_primary_key'):
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
                    
                    # Extract contact info
                    email = ""
                    phone = ""
                    if "contactpersons" in cp_data and cp_data["contactpersons"]:
                        contact = cp_data["contactpersons"][0]
                        email = contact.get("email", "")
                        phone = contact.get("phone", "")
                    
                    # Upsert counterparty
                    stmt = insert(Counterparty).values(
                        external_id=cp_id,
                        name=cp_data.get("name", ""),
                        legal_title=cp_data.get("legalTitle"),
                        inn=cp_data.get("inn"),
                        kpp=cp_data.get("kpp"),
                        email=email,
                        phone=phone,
                        archived=cp_data.get("archived", False),
                        last_sync_at=datetime.utcnow()
                    ).on_conflict_do_update(
                        index_elements=["external_id"],
                        set_=dict(
                            name=cp_data.get("name", ""),
                            legal_title=cp_data.get("legalTitle"),
                            inn=cp_data.get("inn"),
                            kpp=cp_data.get("kpp"),
                            email=email,
                            phone=phone,
                            archived=cp_data.get("archived", False),
                            last_sync_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                    )
                    
                    result = await self.db.execute(stmt)
                    if result.rowcount > 0:
                        if hasattr(result, 'inserted_primary_key'):
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
                    
                    # Upsert store
                    stmt = insert(Store).values(
                        external_id=store_id,
                        name=store_data.get("name", ""),
                        description=store_data.get("description"),
                        archived=store_data.get("archived", False),
                        last_sync_at=datetime.utcnow()
                    ).on_conflict_do_update(
                        index_elements=["external_id"],
                        set_=dict(
                            name=store_data.get("name", ""),
                            description=store_data.get("description"),
                            archived=store_data.get("archived", False),
                            last_sync_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                    )
                    
                    result = await self.db.execute(stmt)
                    if result.rowcount > 0:
                        if hasattr(result, 'inserted_primary_key'):
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
    
    async def full_sync(self) -> Dict[str, Any]:
        """Perform complete full synchronization."""
        logger.info("🔄 Starting complete MoySklad full synchronization...")
        start_time = datetime.utcnow()
        
        try:
            async with await self.create_moysklad_client() as client:
                # Test connection first
                connection_test = await client.test_connection()
                if not connection_test.get("success"):
                    raise IntegrationError(f"Connection test failed: {connection_test.get('message')}")
                
                logger.info(f"✅ Connection test passed: {connection_test.get('message')}")
                
                # Sync in order (dependencies first)
                await self.sync_units_of_measure(client)
                await self.sync_product_folders(client)
                await self.sync_products(client)
                await self.sync_counterparties(client)
                await self.sync_stores(client)
                
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
        """Perform incremental synchronization (last 24 hours)."""
        logger.info("🔄 Starting incremental MoySklad synchronization...")
        start_time = datetime.utcnow()
        
        try:
            # Get last sync time (default to 24 hours ago)
            since = start_time - timedelta(hours=24)
            
            async with await self.create_moysklad_client() as client:
                # Only sync products and counterparties for incremental
                products_data = await client.get_products(updated_since=since)
                counterparties_data = await client.get_counterparties(updated_since=since)
                
                logger.info(f"Found {len(products_data)} updated products, {len(counterparties_data)} updated counterparties")
                
                # Process updates (simplified for incremental)
                if products_data:
                    await self.sync_products(client)
                
                if counterparties_data:
                    await self.sync_counterparties(client)
                
                duration = datetime.utcnow() - start_time
                total_updated = sum(entity["updated"] for entity in self.results.values())
                
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
