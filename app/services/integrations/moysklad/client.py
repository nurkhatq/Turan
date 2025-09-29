# app/services/integrations/moysklad/client.py
"""Comprehensive MoySklad API client with all entity methods."""

import httpx
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import base64
from urllib.parse import urlencode

from app.core.config import Settings
from app.core.exceptions import IntegrationError

settings = Settings()
logger = logging.getLogger(__name__)


class MoySkladClient:
    """Comprehensive MoySklad API client with all entity methods."""
    
    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None
    ):
        self.base_url = settings.MOYSKLAD_BASE_URL
        self.username = username or settings.MOYSKLAD_USERNAME
        self.password = password or settings.MOYSKLAD_PASSWORD
        self.token = token or settings.MOYSKLAD_TOKEN
        
        # Setup authentication - prefer token over username/password
        if self.token:
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json;charset=utf-8",
                "Accept": "application/json;charset=utf-8"
            }
            logger.info("Using MoySklad token authentication")
        elif self.username and self.password:
            credentials = base64.b64encode(
                f"{self.username}:{self.password}".encode()
            ).decode()
            self.headers = {
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/json;charset=utf-8",
                "Accept": "application/json;charset=utf-8"
            }
            logger.info("Using MoySklad basic authentication")
        else:
            raise IntegrationError(
                "No MoySklad authentication credentials provided. "
                "Please provide either a token or username/password."
            )
        
        self.client = httpx.AsyncClient(
            headers=self.headers,
            timeout=30.0,
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test API connection and return basic info."""
        try:
            logger.info("Testing MoySklad API connection...")
            
            # Test with a simple request to get organization info
            response = await self.get("entity/organization")
            
            if response and "rows" in response:
                org_count = len(response["rows"])
                logger.info(f"✅ MoySklad connection successful. Found {org_count} organizations.")
                
                return {
                    "success": True,
                    "message": f"Connection successful. Access to {org_count} organizations.",
                    "organizations_count": org_count,
                    "auth_method": "token" if self.token else "basic"
                }
            else:
                logger.warning("⚠️ Connection successful but unexpected response format")
                return {
                    "success": True,
                    "message": "Connection successful but unexpected response format",
                    "auth_method": "token" if self.token else "basic"
                }
                
        except IntegrationError as e:
            logger.error(f"❌ MoySklad connection failed: {e.message}")
            return {
                "success": False,
                "message": f"Connection failed: {e.message}",
                "details": e.details
            }
        except Exception as e:
            logger.error(f"❌ Unexpected error testing MoySklad connection: {e}")
            return {
                "success": False,
                "message": f"Unexpected error: {str(e)}"
            }
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to MoySklad API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            logger.debug(f"Making {method} request to {url} with params: {params}")
            
            response = await self.client.request(
                method=method,
                url=url,
                params=params,
                json=data
            )
            
            response.raise_for_status()
            
            if response.content:
                try:
                    result = response.json()
                    logger.info(f"Response received: {len(result.get('rows', []))} items")
                    logger.info(f"Response type: {type(result)}")
                    return result
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response: {e}")
                    logger.error(f"Response content: {response.text[:500]}")
                    raise IntegrationError(f"Invalid JSON response from MoySklad API: {e}")
            return {}
            
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_response = e.response.json()
                if "errors" in error_response:
                    error_detail = "; ".join([
                        err.get("error", str(err)) for err in error_response["errors"]
                    ])
            except:
                error_detail = e.response.text
            
            logger.error(f"HTTP error {e.response.status_code}: {error_detail}")
            
            if e.response.status_code == 401:
                raise IntegrationError(
                    "MoySklad authentication failed. Please check your token.",
                    details={"status_code": e.response.status_code, "response": error_detail}
                )
            elif e.response.status_code == 403:
                raise IntegrationError(
                    "MoySklad access denied. Please check your permissions.",
                    details={"status_code": e.response.status_code, "response": error_detail}
                )
            else:
                raise IntegrationError(
                    f"MoySklad API error: {e.response.status_code} - {error_detail}",
                    details={"status_code": e.response.status_code, "response": error_detail}
                )
                
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise IntegrationError(f"Request failed: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise IntegrationError("Invalid JSON response from MoySklad")
    
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request."""
        return await self._make_request("GET", endpoint, params=params)
    
    async def post(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        """Make POST request."""
        return await self._make_request("POST", endpoint, data=data)
    
    async def put(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        """Make PUT request."""
        return await self._make_request("PUT", endpoint, data=data)
    
    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request."""
        return await self._make_request("DELETE", endpoint)
    
    async def get_paginated(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Get all items from paginated endpoint with proper limit handling."""
        all_items = []
        offset = 0
        
        if params is None:
            params = {}
        
        # Use smaller limit for expand queries
        if 'expand' in params:
            limit = min(limit, 100)  # MoySklad limit for expand queries
        
        params["limit"] = limit
        
        while True:
            params["offset"] = offset
            
            try:
                response = await self.get(endpoint, params)
                rows = response.get("rows", [])
                
                if not rows:
                    break
                
                all_items.extend(rows)
                offset += len(rows)
                
                logger.debug(f"Loaded {len(all_items)} items from {endpoint}")
                
                # Check if we got all items
                if len(rows) < limit:
                    break
                    
                # Small delay to respect rate limits
                import asyncio
                await asyncio.sleep(0.05)
                
            except Exception as e:
                logger.error(f"Error in pagination at offset {offset}: {e}")
                break
        
        logger.info(f"Total loaded from {endpoint}: {len(all_items)} items")
        return all_items
    
    # Organization entities
    async def get_organizations(self) -> List[Dict]:
        """Get organizations."""
        logger.info("🏢 Fetching organizations from MoySklad...")
        return await self.get_paginated("entity/organization")
    
    async def get_employees(self, expand: Optional[str] = None) -> List[Dict]:
        """Get employees."""
        logger.info("👥 Fetching employees from MoySklad...")
        params = {}
        if expand:
            params["expand"] = expand
        return await self.get_paginated("entity/employee", params)
    
    async def get_projects(self) -> List[Dict]:
        """Get projects."""
        logger.info("📋 Fetching projects from MoySklad...")
        return await self.get_paginated("entity/project")
    
    async def get_contracts(self, updated_since: Optional[datetime] = None) -> List[Dict]:
        """Get contracts."""
        logger.info("📄 Fetching contracts from MoySklad...")
        params = {"expand": "agent,ownAgent,project"}
        
        if updated_since:
            filter_date = updated_since.strftime("%Y-%m-%d %H:%M:%S")
            params["filter"] = f"updated>={filter_date}"
        
        return await self.get_paginated("entity/contract", params)
    
    # Reference entities
    async def get_currencies(self) -> List[Dict]:
        """Get currencies."""
        logger.info("💱 Fetching currencies from MoySklad...")
        return await self.get_paginated("entity/currency")
    
    async def get_price_types(self) -> List[Dict]:
        """Get price types."""
        logger.info("💰 Fetching price types from MoySklad...")
        return await self.get_paginated("entity/pricetype")
    
    async def get_countries(self) -> List[Dict]:
        """Get countries."""
        logger.info("🌍 Fetching countries from MoySklad...")
        return await self.get_paginated("entity/country")
    
    # Product entities
    async def get_products(self, updated_since: Optional[datetime] = None) -> List[Dict]:
        """Get products from MoySklad with proper filtering and expand."""
        logger.info("🛍️ Fetching products from MoySklad...")
        
        params = {
            "expand": "productFolder,uom,supplier,salePrices,buyPrice"  # Get related data
        }
        
        if updated_since:
            filter_date = updated_since.strftime("%Y-%m-%d %H:%M:%S")
            params["filter"] = f"updated>={filter_date}"
        
        return await self.get_paginated("entity/product", params)
    
    async def get_services(self, updated_since: Optional[datetime] = None) -> List[Dict]:
        """Get services from MoySklad."""
        logger.info("🔧 Fetching services from MoySklad...")
        
        params = {
            "expand": "productFolder,uom,salePrices,buyPrice"
        }
        
        if updated_since:
            filter_date = updated_since.strftime("%Y-%m-%d %H:%M:%S")
            params["filter"] = f"updated>={filter_date}"
        
        return await self.get_paginated("entity/service", params)
    
    async def get_product_folders(self) -> List[Dict]:
        """Get product folders/categories."""
        logger.info("📁 Fetching product folders from MoySklad...")
        return await self.get_paginated("entity/productfolder")
    
    async def get_units_of_measure(self) -> List[Dict]:
        """Get units of measure."""
        logger.info("📏 Fetching units of measure from MoySklad...")
        return await self.get_paginated("entity/uom")
    
    async def get_variants(self, product_id: str) -> List[Dict]:
        """Get product variants."""
        return await self.get_paginated(f"entity/product/{product_id}/modifications")
    
    async def get_counterparties(self, updated_since: Optional[datetime] = None) -> List[Dict]:
        """Get counterparties from MoySklad."""
        logger.info("🤝 Fetching counterparties from MoySklad...")
        
        params = {
            "expand": "contactpersons"  # Get contact persons
        }
        
        if updated_since:
            filter_date = updated_since.strftime("%Y-%m-%d %H:%M:%S")
            params["filter"] = f"updated>={filter_date}"
        
        return await self.get_paginated("entity/counterparty", params)
    
    async def get_stores(self) -> List[Dict]:
        """Get stores/warehouses from MoySklad."""
        logger.info("🏪 Fetching stores from MoySklad...")
        return await self.get_paginated("entity/store")
    
    async def get_stock(self, store_id: Optional[str] = None) -> List[Dict]:
        """Get stock levels from MoySklad using the correct report endpoint."""
        logger.info("📦 Fetching stock levels from MoySklad...")
        
        params = {}
        if store_id:
            params["store.id"] = store_id
        
        return await self.get_paginated("report/stock/all", params)
    
    # Document entities
    async def get_customer_orders(self, updated_since: Optional[datetime] = None) -> List[Dict]:
        """Get customer orders."""
        logger.info("📦 Fetching customer orders from MoySklad...")
        params = {"expand": "agent,organization,store,state,project,contract"}
        
        if updated_since:
            filter_date = updated_since.strftime("%Y-%m-%d %H:%M:%S")
            params["filter"] = f"updated>={filter_date}"
        
        return await self.get_paginated("entity/customerorder", params)
    
    async def get_demands(self, updated_since: Optional[datetime] = None) -> List[Dict]:
        """Get shipments (demands)."""
        logger.info("🚚 Fetching shipments from MoySklad...")
        params = {"expand": "agent,organization,store,state,project,contract"}
        
        if updated_since:
            filter_date = updated_since.strftime("%Y-%m-%d %H:%M:%S")
            params["filter"] = f"updated>={filter_date}"
        
        return await self.get_paginated("entity/demand", params)
    
    async def get_invoices_out(self, updated_since: Optional[datetime] = None) -> List[Dict]:
        """Get sales invoices."""
        logger.info("📄 Fetching sales invoices from MoySklad...")
        params = {"expand": "agent,organization,state,project,contract"}
        
        if updated_since:
            filter_date = updated_since.strftime("%Y-%m-%d %H:%M:%S")
            params["filter"] = f"updated>={filter_date}"
        
        return await self.get_paginated("entity/invoiceout", params)
    
    async def get_sales_returns(self, updated_since: Optional[datetime] = None) -> List[Dict]:
        """Get sales returns."""
        logger.info("↩️ Fetching sales returns from MoySklad...")
        params = {"expand": "agent,organization,store,state"}
        
        if updated_since:
            filter_date = updated_since.strftime("%Y-%m-%d %H:%M:%S")
            params["filter"] = f"updated>={filter_date}"
        
        return await self.get_paginated("entity/salesreturn", params)
    
    async def get_purchase_orders(self, updated_since: Optional[datetime] = None) -> List[Dict]:
        """Get purchase orders."""
        logger.info("📋 Fetching purchase orders from MoySklad...")
        params = {"expand": "agent,organization,store,state,project,contract"}
        
        if updated_since:
            filter_date = updated_since.strftime("%Y-%m-%d %H:%M:%S")
            params["filter"] = f"updated>={filter_date}"
        
        return await self.get_paginated("entity/purchaseorder", params)
    
    async def get_supplies(self, updated_since: Optional[datetime] = None) -> List[Dict]:
        """Get supplies (receipts)."""
        logger.info("📥 Fetching supplies from MoySklad...")
        params = {"expand": "agent,organization,store,state,project,contract"}
        
        if updated_since:
            filter_date = updated_since.strftime("%Y-%m-%d %H:%M:%S")
            params["filter"] = f"updated>={filter_date}"
        
        return await self.get_paginated("entity/supply", params)
    
    async def get_invoices_in(self, updated_since: Optional[datetime] = None) -> List[Dict]:
        """Get purchase invoices."""
        logger.info("📄 Fetching purchase invoices from MoySklad...")
        params = {"expand": "agent,organization,state,project,contract"}
        
        if updated_since:
            filter_date = updated_since.strftime("%Y-%m-%d %H:%M:%S")
            params["filter"] = f"updated>={filter_date}"
        
        return await self.get_paginated("entity/invoicein", params)
    
    async def get_purchase_returns(self, updated_since: Optional[datetime] = None) -> List[Dict]:
        """Get purchase returns."""
        logger.info("↩️ Fetching purchase returns from MoySklad...")
        params = {"expand": "agent,organization,store,state"}
        
        if updated_since:
            filter_date = updated_since.strftime("%Y-%m-%d %H:%M:%S")
            params["filter"] = f"updated>={filter_date}"
        
        return await self.get_paginated("entity/purchasereturn", params)
    
    # Stock movement documents
    async def get_enters(self, updated_since: Optional[datetime] = None) -> List[Dict]:
        """Get stock receipts (enter documents)."""
        logger.info("📊 Fetching stock receipts from MoySklad...")
        params = {"expand": "store"}
        
        if updated_since:
            filter_date = updated_since.strftime("%Y-%m-%d %H:%M:%S")
            params["filter"] = f"updated>={filter_date}"
        
        return await self.get_paginated("entity/enter", params)
    
    async def get_losses(self, updated_since: Optional[datetime] = None) -> List[Dict]:
        """Get stock write-offs (loss documents)."""
        logger.info("📊 Fetching stock write-offs from MoySklad...")
        params = {"expand": "store"}
        
        if updated_since:
            filter_date = updated_since.strftime("%Y-%m-%d %H:%M:%S")
            params["filter"] = f"updated>={filter_date}"
        
        return await self.get_paginated("entity/loss", params)
    
    async def get_moves(self, updated_since: Optional[datetime] = None) -> List[Dict]:
        """Get stock movements between stores."""
        logger.info("📊 Fetching stock movements from MoySklad...")
        params = {"expand": "sourceStore,targetStore"}
        
        if updated_since:
            filter_date = updated_since.strftime("%Y-%m-%d %H:%M:%S")
            params["filter"] = f"updated>={filter_date}"
        
        return await self.get_paginated("entity/move", params)
    
    async def get_inventories(self, updated_since: Optional[datetime] = None) -> List[Dict]:
        """Get inventory adjustments."""
        logger.info("📊 Fetching inventory adjustments from MoySklad...")
        params = {"expand": "store"}
        
        if updated_since:
            filter_date = updated_since.strftime("%Y-%m-%d %H:%M:%S")
            params["filter"] = f"updated>={filter_date}"
        
        return await self.get_paginated("entity/inventory", params)
    
    # Report methods
    async def get_profit_by_product(self, 
                                   date_from: datetime, 
                                   date_to: datetime) -> List[Dict]:
        """Get profit report by products."""
        logger.info("📈 Fetching profit by product report...")
        
        params = {
            "momentFrom": date_from.strftime("%Y-%m-%d %H:%M:%S"),
            "momentTo": date_to.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return await self.get_paginated("report/profit/byproduct", params)
    
    async def get_profit_by_counterparty(self,
                                        date_from: datetime,
                                        date_to: datetime) -> List[Dict]:
        """Get profit report by counterparties."""
        logger.info("📈 Fetching profit by counterparty report...")
        
        params = {
            "momentFrom": date_from.strftime("%Y-%m-%d %H:%M:%S"),
            "momentTo": date_to.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return await self.get_paginated("report/profit/bycounterparty", params)
    
    async def get_sales_dashboard(self) -> Dict[str, Any]:
        """Get sales dashboard metrics."""
        logger.info("📊 Fetching sales dashboard...")
        return await self.get("report/dashboard/sales")
    
    async def get_orders_dashboard(self) -> Dict[str, Any]:
        """Get orders dashboard metrics."""
        logger.info("📊 Fetching orders dashboard...")
        return await self.get("report/dashboard/orders")
    
    async def get_money_dashboard(self) -> Dict[str, Any]:
        """Get money flow dashboard."""
        logger.info("💰 Fetching money dashboard...")
        return await self.get("report/dashboard/money")
    
    async def get_turnover_report(self,
                                 date_from: Optional[datetime] = None,
                                 date_to: Optional[datetime] = None) -> List[Dict]:
        """Get product turnover report."""
        logger.info("🔄 Fetching turnover report...")
        
        params = {}
        if date_from:
            params["momentFrom"] = date_from.strftime("%Y-%m-%d %H:%M:%S")
        if date_to:
            params["momentTo"] = date_to.strftime("%Y-%m-%d %H:%M:%S")
        
        return await self.get_paginated("report/turnover/all", params)
    
    # Utility methods for batch operations
    async def create_entity(self, entity_type: str, data: Dict) -> Dict:
        """Create new entity in MoySklad."""
        logger.info(f"➕ Creating {entity_type}...")
        return await self.post(f"entity/{entity_type}", data)
    
    async def update_entity(self, entity_type: str, entity_id: str, data: Dict) -> Dict:
        """Update existing entity in MoySklad."""
        logger.info(f"✏️ Updating {entity_type}/{entity_id}...")
        return await self.put(f"entity/{entity_type}/{entity_id}", data)
    
    async def delete_entity(self, entity_type: str, entity_id: str) -> Dict:
        """Delete entity from MoySklad."""
        logger.info(f"🗑️ Deleting {entity_type}/{entity_id}...")
        return await self.delete(f"entity/{entity_type}/{entity_id}")
    
    async def batch_create(self, entity_type: str, data_list: List[Dict]) -> List[Dict]:
        """Batch create multiple entities."""
        logger.info(f"➕➕ Batch creating {len(data_list)} {entity_type} entities...")
        return await self.post(f"entity/{entity_type}", data_list)
    
    async def batch_update(self, entity_type: str, data_list: List[Dict]) -> List[Dict]:
        """Batch update multiple entities."""
        logger.info(f"✏️✏️ Batch updating {len(data_list)} {entity_type} entities...")
        
        # MoySklad requires POST with special header for batch update
        self.headers["X-Lognex-Format-Millisecond"] = "true"
        result = await self.post(f"entity/{entity_type}", data_list)
        del self.headers["X-Lognex-Format-Millisecond"]
        
        return result
    
    async def batch_delete(self, entity_type: str, entity_ids: List[str]) -> Dict:
        """Batch delete multiple entities."""
        logger.info(f"🗑️🗑️ Batch deleting {len(entity_ids)} {entity_type} entities...")
        
        # Build delete request body
        delete_data = [
            {"meta": {"href": f"{self.base_url}/entity/{entity_type}/{entity_id}"}}
            for entity_id in entity_ids
        ]
        
        return await self.post(f"entity/{entity_type}/delete", delete_data)
    
    # Legacy methods for backward compatibility
    async def get_sales_documents(
        self,
        document_type: str,
        updated_since: Optional[datetime] = None
    ) -> List[Dict]:
        """Get sales documents from MoySklad."""
        logger.info(f"📄 Fetching {document_type} documents from MoySklad...")
        
        params = {
            "expand": "agent,organization,store,state"
        }
        
        if updated_since:
            filter_date = updated_since.strftime("%Y-%m-%d %H:%M:%S")
            params["filter"] = f"updated>={filter_date}"
        
        return await self.get_paginated(f"entity/{document_type}", params)
    
    async def get_document_positions(self, document_type: str, document_id: str) -> List[Dict]:
        """Get document positions."""
        logger.info(f"📋 Fetching positions for {document_type}/{document_id}")
        return await self.get_paginated(f"entity/{document_type}/{document_id}/positions")
    
    async def get_assortment(self, updated_since: Optional[datetime] = None) -> List[Dict]:
        """Get complete assortment (products + services + variants)."""
        logger.info("📚 Fetching complete assortment from MoySklad...")
        
        params = {
            "expand": "productFolder,uom,supplier,salePrices,buyPrice"
        }
        
        if updated_since:
            filter_date = updated_since.strftime("%Y-%m-%d %H:%M:%S")
            params["filter"] = f"updated>={filter_date}"
        
        return await self.get_paginated("entity/assortment", params)