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
    """MoySklad API client with token-only authentication support."""
    
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
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            logger.info("Using MoySklad token authentication")
        elif self.username and self.password:
            credentials = base64.b64encode(
                f"{self.username}:{self.password}".encode()
            ).decode()
            self.headers = {
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/json",
                "Accept": "application/json"
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
            logger.debug(f"Making {method} request to {url}")
            
            response = await self.client.request(
                method=method,
                url=url,
                params=params,
                json=data
            )
            
            response.raise_for_status()
            
            if response.content:
                return response.json()
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
        """Get all items from paginated endpoint."""
        all_items = []
        offset = 0
        
        if params is None:
            params = {}
        
        params["limit"] = limit
        
        while True:
            params["offset"] = offset
            
            response = await self.get(endpoint, params)
            rows = response.get("rows", [])
            
            if not rows:
                break
            
            all_items.extend(rows)
            offset += len(rows)
            
            # Check if we got all items
            if len(rows) < limit:
                break
        
        return all_items
    
    # Entity-specific methods (same as before)
    async def get_products(self, updated_since: Optional[datetime] = None) -> List[Dict]:
        """Get products from MoySklad."""
        params = {}
        if updated_since:
            params["updatedBy"] = updated_since.isoformat()
        
        return await self.get_paginated("entity/product", params)
    
    async def get_services(self, updated_since: Optional[datetime] = None) -> List[Dict]:
        """Get services from MoySklad."""
        params = {}
        if updated_since:
            params["updatedBy"] = updated_since.isoformat()
        
        return await self.get_paginated("entity/service", params)
    
    async def get_variants(self, product_id: str) -> List[Dict]:
        """Get product variants."""
        return await self.get_paginated(f"entity/product/{product_id}/modifications")
    
    async def get_counterparties(self, updated_since: Optional[datetime] = None) -> List[Dict]:
        """Get counterparties from MoySklad."""
        params = {}
        if updated_since:
            params["updatedBy"] = updated_since.isoformat()
        
        return await self.get_paginated("entity/counterparty", params)
    
    async def get_stores(self) -> List[Dict]:
        """Get stores/warehouses from MoySklad."""
        return await self.get_paginated("entity/store")
    
    async def get_stock(self, store_id: Optional[str] = None) -> List[Dict]:
        """Get stock levels from MoySklad."""
        params = {}
        if store_id:
            params["store"] = store_id
        
        return await self.get_paginated("report/stock/all", params)
    
    async def get_sales_documents(
        self,
        document_type: str,
        updated_since: Optional[datetime] = None
    ) -> List[Dict]:
        """Get sales documents from MoySklad."""
        params = {}
        if updated_since:
            params["updatedBy"] = updated_since.isoformat()
        
        return await self.get_paginated(f"entity/{document_type}", params)
    
    async def get_document_positions(self, document_type: str, document_id: str) -> List[Dict]:
        """Get document positions."""
        return await self.get_paginated(f"entity/{document_type}/{document_id}/positions")
