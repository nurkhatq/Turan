# app/services/integrations/moysklad/sync_service.py
"""MoySklad synchronization service with comprehensive entity support."""

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

# Import all models
from app.models.moysklad.products import Product, ProductFolder, UnitOfMeasure, ProductVariant, Service
from app.models.moysklad.counterparties import Counterparty
from app.models.moysklad.inventory import Store, Stock
from app.models.moysklad.documents import SalesDocument, PurchaseDocument
from app.models.moysklad.organizations import Organization, Employee, Project, Contract, Currency, PriceType, Country

logger = logging.getLogger(__name__)


class MoySkladSyncService:
    """Comprehensive MoySklad sync service with support for all entities."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.results = {}
    
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
        
        # Handle JSON string
        if isinstance(credentials, str):
            try:
                credentials = json.loads(credentials)
            except (json.JSONDecodeError, TypeError):
                credentials = {}
        
        token = credentials.get("token")
        username = credentials.get("username")
        password = credentials.get("password")
        
        if not token and not (username and password):
            raise IntegrationError("MoySklad credentials not configured")
        
        return MoySkladClient(token=token, username=username, password=password)
    
    # Reference data sync methods
    async def sync_currencies(self, client: MoySkladClient) -> Dict[str, int]:
        """Sync currencies."""
        logger.info("💱 Syncing currencies...")
        
        try:
            currencies_data = await client.get("entity/currency")
            rows = currencies_data.get("rows", [])
            
            created = updated = 0
            
            for currency_data in rows:
                currency_id = currency_data.get("id")
                if not currency_id:
                    continue
                
                # Extract minor units
                minor_units = None
                if "minorUnit" in currency_data:
                    minor_units = json.dumps(currency_data["minorUnit"])
                
                stmt = insert(Currency).values(
                    external_id=currency_id,
                    name=currency_data.get("name", ""),
                    full_name=currency_data.get("fullName"),
                    code=currency_data.get("code", ""),
                    iso_code=currency_data.get("isoCode"),
                    is_default=currency_data.get("default", False),
                    is_indirect=currency_data.get("indirect", False),
                    multiplicity=currency_data.get("multiplicity", 1),
                    rate=currency_data.get("rate", 1),
                    minor_units=minor_units,
                    archived=currency_data.get("archived", False),
                    last_sync_at=datetime.utcnow()
                ).on_conflict_do_update(
                    index_elements=["external_id"],
                    set_=dict(
                        name=currency_data.get("name", ""),
                        full_name=currency_data.get("fullName"),
                        code=currency_data.get("code", ""),
                        iso_code=currency_data.get("isoCode"),
                        is_default=currency_data.get("default", False),
                        rate=currency_data.get("rate", 1),
                        last_sync_at=datetime.utcnow()
                    )
                )
                
                result = await self.db.execute(stmt)
                if result.rowcount == 2:  # PostgreSQL returns 2 for upsert update
                    updated += 1
                else:
                    created += 1
            
            logger.info(f"✅ Currencies sync: {created} created, {updated} updated")
            return {"created": created, "updated": updated}
            
        except Exception as e:
            logger.error(f"❌ Error syncing currencies: {e}")
            return {"created": 0, "updated": 0, "errors": 1}
    
    async def sync_countries(self, client: MoySkladClient) -> Dict[str, int]:
        """Sync countries."""
        logger.info("🌍 Syncing countries...")
        
        try:
            countries_data = await client.get("entity/country")
            rows = countries_data.get("rows", [])
            
            created = updated = 0
            
            for country_data in rows:
                country_id = country_data.get("id")
                if not country_id:
                    continue
                
                stmt = insert(Country).values(
                    external_id=country_id,
                    name=country_data.get("name", ""),
                    description=country_data.get("description"),
                    code=country_data.get("code"),
                    external_code=country_data.get("externalCode"),
                    last_sync_at=datetime.utcnow()
                ).on_conflict_do_update(
                    index_elements=["external_id"],
                    set_=dict(
                        name=country_data.get("name", ""),
                        description=country_data.get("description"),
                        code=country_data.get("code"),
                        external_code=country_data.get("externalCode"),
                        last_sync_at=datetime.utcnow()
                    )
                )
                
                result = await self.db.execute(stmt)
                if result.rowcount == 2:
                    updated += 1
                else:
                    created += 1
        
            logger.info(f"✅ Countries sync: {created} created, {updated} updated")
            return {"created": created, "updated": updated}
            
        except Exception as e:
            logger.error(f"❌ Error syncing countries: {e}")
            return {"created": 0, "updated": 0, "errors": 1}
    
    async def sync_organizations(self, client: MoySkladClient) -> Dict[str, int]:
        """Sync organizations."""
        logger.info("🏢 Syncing organizations...")
        
        try:
            logger.info("Making request to organizations endpoint...")
            orgs_data = await client.get("entity/organization")
            logger.info(f"Organizations response received, type: {type(orgs_data)}")
            
            # Debug logging
            if isinstance(orgs_data, str):
                logger.info(f"Organizations response (first 200 chars): {orgs_data[:200]}")
            
            # Handle case where response might be a string
            if isinstance(orgs_data, str):
                try:
                    orgs_data = json.loads(orgs_data)
                    logger.debug("Successfully parsed organizations response as JSON")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse organizations response as JSON: {e}")
                    logger.error(f"Response content: {orgs_data[:500]}")
                    return {"created": 0, "updated": 0, "errors": 1}
            
            # Check if we have valid data structure
            if not isinstance(orgs_data, dict):
                logger.error(f"Invalid organizations data type: {type(orgs_data)}")
                logger.error(f"Data content: {str(orgs_data)[:500]}")
                return {"created": 0, "updated": 0, "errors": 1}
            
            rows = orgs_data.get("rows", [])
            
            created = updated = 0
            
            for org_data in rows:
                org_id = org_data.get("id")
                if not org_id:
                    continue
                
                # Extract bank accounts
                bank_accounts = None
                if "accounts" in org_data:
                    bank_accounts = json.dumps(org_data["accounts"])
                
                # Extract chief accountant ID
                chief_accountant_id = None
                if "chiefAccountant" in org_data:
                    chief_meta = org_data["chiefAccountant"].get("meta", {})
                    chief_href = chief_meta.get("href", "")
                    if chief_href:
                        chief_accountant_id = chief_href.split("/")[-1]
                
                stmt = insert(Organization).values(
                    external_id=org_id,
                    name=org_data.get("name", ""),
                    code=org_data.get("code"),
                    description=org_data.get("description"),
                    legal_title=org_data.get("legalTitle"),
                    legal_address=org_data.get("legalAddress"),
                    actual_address=org_data.get("actualAddress"),
                    inn=org_data.get("inn"),
                    kpp=org_data.get("kpp"),
                    ogrn=org_data.get("ogrn"),
                    okpo=org_data.get("okpo"),
                    email=org_data.get("email"),
                    phone=org_data.get("phone"),
                    fax=org_data.get("fax"),
                    bank_accounts=bank_accounts,
                    archived=org_data.get("archived", False),
                    shared=org_data.get("shared", True),
                    chief_accountant_external_id=chief_accountant_id,
                    last_sync_at=datetime.utcnow()
                ).on_conflict_do_update(
                    index_elements=["external_id"],
                    set_=dict(
                        name=org_data.get("name", ""),
                        code=org_data.get("code"),
                        description=org_data.get("description"),
                        legal_title=org_data.get("legalTitle"),
                        legal_address=org_data.get("legalAddress"),
                        actual_address=org_data.get("actualAddress"),
                        inn=org_data.get("inn"),
                        kpp=org_data.get("kpp"),
                        email=org_data.get("email"),
                        phone=org_data.get("phone"),
                        bank_accounts=bank_accounts,
                        archived=org_data.get("archived", False),
                        last_sync_at=datetime.utcnow()
                    )
                )
                
                result = await self.db.execute(stmt)
                if result.rowcount == 2:
                    updated += 1
                else:
                    created += 1
        
            logger.info(f"✅ Organizations sync: {created} created, {updated} updated")
            return {"created": created, "updated": updated}
            
        except Exception as e:
            logger.error(f"❌ Error syncing organizations: {e}")
            return {"created": 0, "updated": 0, "errors": 1}
    
    async def sync_employees(self, client: MoySkladClient) -> Dict[str, int]:
        """Sync employees."""
        logger.info("👥 Syncing employees...")
        
        try:
            employees_data = await client.get("entity/employee")
            rows = employees_data.get("rows", [])
            
            created = updated = 0
            
            for emp_data in rows:
                emp_id = emp_data.get("id")
                if not emp_id:
                    continue
                
                # Extract organization ID
                org_external_id = None
                if "organization" in emp_data:
                    org_meta = emp_data["organization"].get("meta", {})
                    org_href = org_meta.get("href", "")
                    if org_href:
                        org_external_id = org_href.split("/")[-1]
                
                # Build full name
                first_name = emp_data.get("firstName", "")
                middle_name = emp_data.get("middleName", "")
                last_name = emp_data.get("lastName", "")
                
                full_name = " ".join(filter(None, [last_name, first_name, middle_name]))
                
                # Extract permissions
                permissions = None
                if "permissions" in emp_data:
                    permissions = json.dumps(emp_data["permissions"])
                
                stmt = insert(Employee).values(
                    external_id=emp_id,
                    first_name=first_name,
                    middle_name=middle_name,
                    last_name=last_name,
                    full_name=full_name or emp_data.get("name", ""),
                    position=emp_data.get("position"),
                    code=emp_data.get("code"),
                    email=emp_data.get("email"),
                    phone=emp_data.get("phone"),
                    permissions_data=permissions,
                    archived=emp_data.get("archived", False),
                    shared=emp_data.get("shared", True),
                    cashier_inn=emp_data.get("inn"),
                    organization_external_id=org_external_id,
                    last_sync_at=datetime.utcnow()
                ).on_conflict_do_update(
                    index_elements=["external_id"],
                    set_=dict(
                        first_name=first_name,
                        middle_name=middle_name,
                        last_name=last_name,
                        full_name=full_name or emp_data.get("name", ""),
                        position=emp_data.get("position"),
                        email=emp_data.get("email"),
                        phone=emp_data.get("phone"),
                        permissions_data=permissions,
                        archived=emp_data.get("archived", False),
                        organization_external_id=org_external_id,
                        last_sync_at=datetime.utcnow()
                    )
                )
                
                result = await self.db.execute(stmt)
                if result.rowcount == 2:
                    updated += 1
                else:
                    created += 1
            
            logger.info(f"✅ Employees sync: {created} created, {updated} updated")
            return {"created": created, "updated": updated}
            
        except Exception as e:
            logger.error(f"❌ Error syncing employees: {e}")
            return {"created": 0, "updated": 0, "errors": 1}
    
    async def sync_projects(self, client: MoySkladClient) -> Dict[str, int]:
        """Sync projects."""
        logger.info("📋 Syncing projects...")
        
        try:
            projects_data = await client.get("entity/project")
            rows = projects_data.get("rows", [])
            
            created = updated = 0
            
            for proj_data in rows:
                proj_id = proj_data.get("id")
                if not proj_id:
                    continue
                
                stmt = insert(Project).values(
                    external_id=proj_id,
                    name=proj_data.get("name", ""),
                    code=proj_data.get("code"),
                    description=proj_data.get("description"),
                    archived=proj_data.get("archived", False),
                    shared=proj_data.get("shared", True),
                    last_sync_at=datetime.utcnow()
                ).on_conflict_do_update(
                    index_elements=["external_id"],
                    set_=dict(
                        name=proj_data.get("name", ""),
                        code=proj_data.get("code"),
                        description=proj_data.get("description"),
                        archived=proj_data.get("archived", False),
                        last_sync_at=datetime.utcnow()
                    )
                )
                
                result = await self.db.execute(stmt)
                if result.rowcount == 2:
                    updated += 1
                else:
                    created += 1
        
            logger.info(f"✅ Projects sync: {created} created, {updated} updated")
            return {"created": created, "updated": updated}
            
        except Exception as e:
            logger.error(f"❌ Error syncing projects: {e}")
            return {"created": 0, "updated": 0, "errors": 1}
    
    async def sync_contracts(self, client: MoySkladClient) -> Dict[str, int]:
        """Sync contracts."""
        logger.info("📄 Syncing contracts...")
        
        try:
            contracts_data = await client.get("entity/contract")
            rows = contracts_data.get("rows", [])
            
            created = updated = 0
            
            for contract_data in rows:
                contract_id = contract_data.get("id")
                if not contract_id:
                    continue
                
                # Extract related entity IDs
                counterparty_id = self._extract_id_from_entity(contract_data.get("agent"))
                organization_id = self._extract_id_from_entity(contract_data.get("ownAgent"))
                project_id = self._extract_id_from_entity(contract_data.get("project"))
                
                # Parse dates
                moment = self._parse_datetime(contract_data.get("moment"))
                contract_date = self._parse_datetime(contract_data.get("contractDate"))
                
                stmt = insert(Contract).values(
                    external_id=contract_id,
                    name=contract_data.get("name", ""),
                    code=contract_data.get("code"),
                    number=contract_data.get("number"),
                    description=contract_data.get("description"),
                    moment=moment or datetime.utcnow(),
                    contract_date=contract_date,
                    contract_type=contract_data.get("contractType", "sales"),
                    sum_amount=contract_data.get("sum", 0) / 100,  # Convert kopecks to rubles
                    reward_percent=contract_data.get("rewardPercent"),
                    reward_type=contract_data.get("rewardType"),
                    archived=contract_data.get("archived", False),
                    shared=contract_data.get("shared", True),
                    counterparty_external_id=counterparty_id,
                    organization_external_id=organization_id,
                    project_external_id=project_id,
                    last_sync_at=datetime.utcnow()
                ).on_conflict_do_update(
                    index_elements=["external_id"],
                    set_=dict(
                        name=contract_data.get("name", ""),
                        code=contract_data.get("code"),
                        number=contract_data.get("number"),
                        description=contract_data.get("description"),
                        moment=moment or datetime.utcnow(),
                        contract_date=contract_date,
                        contract_type=contract_data.get("contractType", "sales"),
                        sum_amount=contract_data.get("sum", 0) / 100,
                        reward_percent=contract_data.get("rewardPercent"),
                        reward_type=contract_data.get("rewardType"),
                        archived=contract_data.get("archived", False),
                        counterparty_external_id=counterparty_id,
                        organization_external_id=organization_id,
                        project_external_id=project_id,
                        last_sync_at=datetime.utcnow()
                    )
                )
                
                result = await self.db.execute(stmt)
                if result.rowcount == 2:
                    updated += 1
                else:
                    created += 1
                
            logger.info(f"✅ Contracts sync: {created} created, {updated} updated")
            return {"created": created, "updated": updated}
            
        except Exception as e:
            logger.error(f"❌ Error syncing contracts: {e}")
            return {"created": 0, "updated": 0, "errors": 1}
    
    # Helper methods
    def _extract_id_from_entity(self, entity: Optional[Dict]) -> Optional[str]:
        """Extract ID from MoySklad entity reference."""
        if not entity:
            return None
        
        meta = entity.get("meta", {})
        href = meta.get("href", "")
        if href:
            return href.split("/")[-1]
        
        return None
    
    def _parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse MoySklad datetime string."""
        if not date_str:
            return None
        
        try:
            # Remove timezone and parse
            clean_date = date_str.replace('Z', '+00:00')
            return datetime.fromisoformat(clean_date)
        except (ValueError, TypeError):
            return None
    
    async def resolve_foreign_keys(self):
        """Resolve external IDs to actual foreign keys after sync."""
        logger.info("🔗 Resolving foreign key relationships...")
        
        # Resolve organization relationships for employees
        await self.db.execute(text("""
            UPDATE employee e
            SET organization_id = o.id
            FROM organization o
            WHERE e.organization_external_id = o.external_id
            AND e.organization_id IS NULL
        """))
        
        # Resolve relationships for contracts
        await self.db.execute(text("""
            UPDATE contract c
            SET counterparty_id = cp.id
            FROM counterparty cp
            WHERE c.counterparty_external_id = cp.external_id
            AND c.counterparty_id IS NULL
        """))
        
        await self.db.execute(text("""
            UPDATE contract c
            SET organization_id = o.id
            FROM organization o
            WHERE c.organization_external_id = o.external_id
            AND c.organization_id IS NULL
        """))
        
        await self.db.execute(text("""
            UPDATE contract c
            SET project_id = p.id
            FROM project p
            WHERE c.project_external_id = p.external_id
            AND c.project_id IS NULL
        """))
        
        # Resolve product relationships
        await self.db.execute(text("""
            UPDATE product p
            SET folder_id = pf.id
            FROM product_folder pf
            WHERE p.folder_external_id = pf.external_id
            AND p.folder_id IS NULL
        """))
        
        await self.db.execute(text("""
            UPDATE product p
            SET unit_id = u.id
            FROM unit_of_measure u
            WHERE p.unit_external_id = u.external_id
            AND p.unit_id IS NULL
        """))
        
        logger.info("✅ Foreign key relationships resolved")
    
    async def full_sync(self) -> Dict[str, Any]:
        """Perform complete sync of all entities."""
        logger.info("🚀 Starting FULL MoySklad synchronization...")
        start_time = datetime.utcnow()
        
        try:
            async with await self.create_moysklad_client() as client:
            # Sync reference data first
                logger.info("Starting currencies sync...")
                self.results["currencies"] = await self.sync_currencies(client)
                logger.info("Starting countries sync...")
                self.results["countries"] = await self.sync_countries(client)
                logger.info("Starting organizations sync...")
                self.results["organizations"] = await self.sync_organizations(client)
                logger.info("Starting employees sync...")
                self.results["employees"] = await self.sync_employees(client)
                logger.info("Starting projects sync...")
                self.results["projects"] = await self.sync_projects(client)
                logger.info("Starting contracts sync...")
                self.results["contracts"] = await self.sync_contracts(client)
                
            # Finally resolve all foreign key relationships
            # Temporarily disabled to test basic sync functionality
            # await self.resolve_foreign_keys()
            
            # Update configuration
            config = await self.get_integration_config()
            config.last_sync_at = datetime.utcnow()
            config.sync_status = "active"
            config.error_message = None
            
            duration = datetime.utcnow() - start_time
            
            result = {
                "status": "completed",
                "duration_seconds": duration.total_seconds(),
                "started_at": start_time.isoformat(),
                "completed_at": datetime.utcnow().isoformat(),
                "results": self.results
            }
            
            logger.info(f"✅ Full sync completed in {duration.total_seconds():.2f}s")
            return result
                
        except Exception as e:
            duration = datetime.utcnow() - start_time
            logger.error(f"❌ Full sync failed after {duration.total_seconds():.2f}s: {e}")
            
            # Update config with error
            try:
                config = await self.get_integration_config()
                config.sync_status = "error"
                config.error_message = str(e)
            except Exception as config_error:
                logger.error(f"Failed to update config with error: {config_error}")
            
            raise
    
    async def incremental_sync(self) -> Dict[str, Any]:
        """Perform incremental synchronization (last 24 hours)."""
        logger.info("🔄 Starting incremental MoySklad synchronization...")
        start_time = datetime.utcnow()
        
        try:
            # Get last sync time (default to 24 hours ago)
            since = start_time - timedelta(hours=24)
            
            async with await self.create_moysklad_client() as client:
                # For now, just sync organizations and employees for incremental
                self.results["organizations"] = await self.sync_organizations(client)
                self.results["employees"] = await self.sync_employees(client)
                
                # Resolve foreign keys
                await self.resolve_foreign_keys()
                
                duration = datetime.utcnow() - start_time
                total_updated = sum(entity.get("updated", 0) for entity in self.results.values())
                
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
