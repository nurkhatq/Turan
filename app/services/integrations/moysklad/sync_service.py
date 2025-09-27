# app/services/integrations/moysklad/sync_service.py
import json
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timedelta
import logging

from app.core.database import get_db_context
from app.services.integrations.moysklad.client import MoySkladClient
from app.services.integrations.moysklad.mapper import MoySkladMapper
from app.models.moysklad.products import Product, Service, ProductFolder
from app.models.moysklad.counterparties import Counterparty
from app.models.moysklad.inventory import Store, Stock
from app.models.system import IntegrationConfig, SyncJob

logger = logging.getLogger(__name__)


class MoySkladSyncService:
    """Service for synchronizing data with MoySklad."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.mapper = MoySkladMapper()
    
    async def get_integration_config(self) -> Optional[IntegrationConfig]:
        """Get MoySklad integration configuration."""
        stmt = select(IntegrationConfig).where(
            IntegrationConfig.service_name == "moysklad"
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def sync_products(
        self, 
        client: MoySkladClient, 
        incremental: bool = True
    ) -> Dict[str, int]:
        """Sync products from MoySklad."""
        logger.info("Starting product synchronization")
        
        # Get last sync time for incremental sync
        updated_since = None
        if incremental:
            config = await self.get_integration_config()
            if config and config.last_sync_at:
                updated_since = config.last_sync_at - timedelta(minutes=5)  # 5 min buffer
        
        # Fetch products from MoySklad
        products_data = await client.get_products(updated_since)
        
        created_count = 0
        updated_count = 0
        
        for product_data in products_data:
            try:
                mapped_data = self.mapper.map_product(product_data)
                
                # Check if product exists
                stmt = select(Product).where(
                    Product.external_id == mapped_data['external_id']
                )
                result = await self.db.execute(stmt)
                existing_product = result.scalar_one_or_none()
                
                if existing_product:
                    # Update existing product
                    for key, value in mapped_data.items():
                        if key != 'id':
                            setattr(existing_product, key, value)
                    updated_count += 1
                else:
                    # Create new product
                    product = Product(**mapped_data)
                    self.db.add(product)
                    created_count += 1
                
                await self.db.flush()
                
            except Exception as e:
                logger.error(f"Failed to sync product {product_data.get('id', 'unknown')}: {e}")
                continue
        
        await self.db.commit()
        
        logger.info(f"Product sync completed: {created_count} created, {updated_count} updated")
        return {"created": created_count, "updated": updated_count}
    
    async def sync_services(
        self, 
        client: MoySkladClient, 
        incremental: bool = True
    ) -> Dict[str, int]:
        """Sync services from MoySklad."""
        logger.info("Starting service synchronization")
        
        updated_since = None
        if incremental:
            config = await self.get_integration_config()
            if config and config.last_sync_at:
                updated_since = config.last_sync_at - timedelta(minutes=5)
        
        services_data = await client.get_services(updated_since)
        
        created_count = 0
        updated_count = 0
        
        for service_data in services_data:
            try:
                mapped_data = self.mapper.map_service(service_data)
                
                stmt = select(Service).where(
                    Service.external_id == mapped_data['external_id']
                )
                result = await self.db.execute(stmt)
                existing_service = result.scalar_one_or_none()
                
                if existing_service:
                    for key, value in mapped_data.items():
                        if key != 'id':
                            setattr(existing_service, key, value)
                    updated_count += 1
                else:
                    service = Service(**mapped_data)
                    self.db.add(service)
                    created_count += 1
                
                await self.db.flush()
                
            except Exception as e:
                logger.error(f"Failed to sync service {service_data.get('id', 'unknown')}: {e}")
                continue
        
        await self.db.commit()
        
        logger.info(f"Service sync completed: {created_count} created, {updated_count} updated")
        return {"created": created_count, "updated": updated_count}
    
    async def sync_counterparties(
        self, 
        client: MoySkladClient, 
        incremental: bool = True
    ) -> Dict[str, int]:
        """Sync counterparties from MoySklad."""
        logger.info("Starting counterparty synchronization")
        
        updated_since = None
        if incremental:
            config = await self.get_integration_config()
            if config and config.last_sync_at:
                updated_since = config.last_sync_at - timedelta(minutes=5)
        
        counterparties_data = await client.get_counterparties(updated_since)
        
        created_count = 0
        updated_count = 0
        
        for cp_data in counterparties_data:
            try:
                mapped_data = self.mapper.map_counterparty(cp_data)
                
                stmt = select(Counterparty).where(
                    Counterparty.external_id == mapped_data['external_id']
                )
                result = await self.db.execute(stmt)
                existing_cp = result.scalar_one_or_none()
                
                if existing_cp:
                    for key, value in mapped_data.items():
                        if key != 'id':
                            setattr(existing_cp, key, value)
                    updated_count += 1
                else:
                    counterparty = Counterparty(**mapped_data)
                    self.db.add(counterparty)
                    created_count += 1
                
                await self.db.flush()
                
            except Exception as e:
                logger.error(f"Failed to sync counterparty {cp_data.get('id', 'unknown')}: {e}")
                continue
        
        await self.db.commit()
        
        logger.info(f"Counterparty sync completed: {created_count} created, {updated_count} updated")
        return {"created": created_count, "updated": updated_count}
    
    async def sync_stores(self, client: MoySkladClient) -> Dict[str, int]:
        """Sync stores from MoySklad."""
        logger.info("Starting store synchronization")
        
        stores_data = await client.get_stores()
        
        created_count = 0
        updated_count = 0
        
        for store_data in stores_data:
            try:
                mapped_data = self.mapper.map_store(store_data)
                
                stmt = select(Store).where(
                    Store.external_id == mapped_data['external_id']
                )
                result = await self.db.execute(stmt)
                existing_store = result.scalar_one_or_none()
                
                if existing_store:
                    for key, value in mapped_data.items():
                        if key != 'id':
                            setattr(existing_store, key, value)
                    updated_count += 1
                else:
                    store = Store(**mapped_data)
                    self.db.add(store)
                    created_count += 1
                
                await self.db.flush()
                
            except Exception as e:
                logger.error(f"Failed to sync store {store_data.get('id', 'unknown')}: {e}")
                continue
        
        await self.db.commit()
        
        logger.info(f"Store sync completed: {created_count} created, {updated_count} updated")
        return {"created": created_count, "updated": updated_count}
    
    async def full_sync(self) -> Dict[str, Any]:
        """Perform full synchronization of all MoySklad data."""
        logger.info("Starting full MoySklad synchronization")
        
        config = await self.get_integration_config()
        if not config or not config.is_enabled:
            raise ValueError("MoySklad integration is not configured or enabled")
        
        # Get credentials from config
        credentials = json.loads(config.credentials_data) if config.credentials_data else {}
        
        async with MoySkladClient(
            username=credentials.get('username'),
            password=credentials.get('password'),
            token=credentials.get('token')
        ) as client:
            results = {}
            
            # Sync reference data first
            results['stores'] = await self.sync_stores(client)
            
            # Sync main entities
            results['products'] = await self.sync_products(client, incremental=False)
            results['services'] = await self.sync_services(client, incremental=False)
            results['counterparties'] = await self.sync_counterparties(client, incremental=False)
            
            # Update last sync time
            config.last_sync_at = datetime.utcnow()
            config.sync_status = "active"
            config.error_message = None
            await self.db.commit()
            
            logger.info("Full MoySklad synchronization completed successfully")
            return results
    
    async def incremental_sync(self) -> Dict[str, Any]:
        """Perform incremental synchronization."""
        logger.info("Starting incremental MoySklad synchronization")
        
        config = await self.get_integration_config()
        if not config or not config.is_enabled:
            logger.warning("MoySklad integration is not enabled, skipping sync")
            return {}
        
        credentials = json.loads(config.credentials_data) if config.credentials_data else {}
        
        async with MoySkladClient(
            username=credentials.get('username'),
            password=credentials.get('password'),
            token=credentials.get('token')
        ) as client:
            results = {}
            
            # Sync main entities incrementally
            results['products'] = await self.sync_products(client, incremental=True)
            results['services'] = await self.sync_services(client, incremental=True)
            results['counterparties'] = await self.sync_counterparties(client, incremental=True)
            
            # Update last sync time
            config.last_sync_at = datetime.utcnow()
            config.sync_status = "active"
            config.error_message = None
            await self.db.commit()
            
            logger.info("Incremental MoySklad synchronization completed")
            return results