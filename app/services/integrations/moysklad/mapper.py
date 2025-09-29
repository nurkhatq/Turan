# app/services/integrations/moysklad/mapper.py
from typing import Dict, Any, Optional
from datetime import datetime
import json
import logging

from app.models.moysklad.products import Product, ProductVariant, Service, ProductFolder
from app.models.moysklad.counterparties import Counterparty
from app.models.moysklad.inventory import Store, Stock
from app.models.moysklad.documents import SalesDocument, PurchaseDocument

logger = logging.getLogger(__name__)


class MoySkladMapper:
    """Maps MoySklad API data to database models."""
    
    @staticmethod
    def parse_datetime(date_str: Optional[str]) -> Optional[datetime]:
        """Parse MoySklad datetime string."""
        if not date_str:
            return None
        try:
            # Remove timezone info if present and parse
            clean_date = date_str.replace('Z', '+00:00')
            return datetime.fromisoformat(clean_date)
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to parse datetime '{date_str}': {e}")
            return None
    
    @staticmethod
    def extract_id_from_meta(meta: Dict[str, Any]) -> Optional[str]:
        """Extract ID from MoySklad meta object."""
        if not meta or 'href' not in meta:
            return None
        
        # Extract ID from href URL
        href = meta['href']
        try:
            return href.split('/')[-1]
        except (IndexError, AttributeError):
            return None
    
    @staticmethod
    def map_product_folder(data: Dict[str, Any]) -> Dict[str, Any]:
        """Map MoySklad product folder to database model fields."""
        return {
            'external_id': MoySkladMapper.extract_id_from_meta(data.get('meta')),
            'name': data.get('name', ''),
            'code': data.get('code'),
            'description': data.get('description'),
            'external_meta': json.dumps(data.get('meta', {})),
            'last_sync_at': datetime.utcnow(),
            'sync_status': 'synced'
        }
    
    @staticmethod
    def map_product(data: Dict[str, Any]) -> Dict[str, Any]:
        """Map MoySklad product to database model fields."""
        # Extract pricing from salePrices
        sale_price = None
        buy_price = None
        min_price = None
        
        if 'salePrices' in data and data['salePrices']:
            # Get first sale price
            sale_price = data['salePrices'][0].get('value', 0) / 100  # Convert kopecks to rubles
        
        if 'buyPrice' in data and data['buyPrice']:
            buy_price = data['buyPrice'].get('value', 0) / 100
        
        if 'minPrice' in data and data['minPrice']:
            min_price = data['minPrice'].get('value', 0) / 100
        
        return {
            'external_id': MoySkladMapper.extract_id_from_meta(data.get('meta')),
            'name': data.get('name', ''),
            'code': data.get('code'),
            'article': data.get('article'),
            'description': data.get('description'),
            'sale_price': sale_price,
            'buy_price': buy_price,
            'min_price': min_price,
            'weight': data.get('weight', 0) / 1000 if data.get('weight') else None,  # Convert grams to kg
            'volume': data.get('volume', 0) / 1000000 if data.get('volume') else None,  # Convert mm³ to m³
            'archived': data.get('archived', False),
            'shared': data.get('shared', True),
            'external_meta': json.dumps(data.get('meta', {})),
            'last_sync_at': datetime.utcnow(),
            'sync_status': 'synced'
        }
    
    @staticmethod
    def map_service(data: Dict[str, Any]) -> Dict[str, Any]:
        """Map MoySklad service to database model fields."""
        # Extract pricing
        sale_price = None
        buy_price = None
        min_price = None
        
        if 'salePrices' in data and data['salePrices']:
            sale_price = data['salePrices'][0].get('value', 0) / 100
        
        if 'buyPrice' in data and data['buyPrice']:
            buy_price = data['buyPrice'].get('value', 0) / 100
        
        if 'minPrice' in data and data['minPrice']:
            min_price = data['minPrice'].get('value', 0) / 100
        
        return {
            'external_id': MoySkladMapper.extract_id_from_meta(data.get('meta')),
            'name': data.get('name', ''),
            'code': data.get('code'),
            'description': data.get('description'),
            'sale_price': sale_price,
            'buy_price': buy_price,
            'min_price': min_price,
            'archived': data.get('archived', False),
            'shared': data.get('shared', True),
            'external_meta': json.dumps(data.get('meta', {})),
            'last_sync_at': datetime.utcnow(),
            'sync_status': 'synced'
        }
    
    @staticmethod
    def map_counterparty(data: Dict[str, Any]) -> Dict[str, Any]:
        """Map MoySklad counterparty to database model fields."""
        # Extract contact info
        email = None
        phone = None
        
        if 'contactpersons' in data and data['contactpersons']:
            # Get first contact person
            contact = data['contactpersons'][0]
            email = contact.get('email')
            phone = contact.get('phone')
        
        # Extract legal info
        legal_address = None
        actual_address = None
        
        if 'legalAddress' in data:
            legal_address = data['legalAddress'].get('addInfo')
        
        if 'actualAddress' in data:
            actual_address = data['actualAddress'].get('addInfo')
        
        return {
            'external_id': MoySkladMapper.extract_id_from_meta(data.get('meta')),
            'name': data.get('name', ''),
            'code': data.get('code'),
            'description': data.get('description'),
            'email': email,
            'phone': phone,
            'legal_title': data.get('legalTitle'),
            'legal_address': legal_address,
            'actual_address': actual_address,
            'inn': data.get('inn'),
            'kpp': data.get('kpp'),
            'ogrn': data.get('ogrn'),
            'okpo': data.get('okpo'),
            'is_supplier': data.get('supplier', False),
            'is_customer': not data.get('supplier', False),  # Assume customer if not supplier
            'discount_percentage': data.get('discountCardNumber', 0),
            'archived': data.get('archived', False),
            'shared': data.get('shared', True),
            'external_meta': json.dumps(data.get('meta', {})),
            'last_sync_at': datetime.utcnow(),
            'sync_status': 'synced'
        }
    
    @staticmethod
    def map_store(data: Dict[str, Any]) -> Dict[str, Any]:
        """Map MoySklad store to database model fields."""
        address = None
        if 'address' in data:
            address = data['address'].get('addInfo')
        
        return {
            'external_id': MoySkladMapper.extract_id_from_meta(data.get('meta')),
            'name': data.get('name', ''),
            'code': data.get('code'),
            'description': data.get('description'),
            'address': address,
            'archived': data.get('archived', False),
            'external_meta': json.dumps(data.get('meta', {})),
            'last_sync_at': datetime.utcnow(),
            'sync_status': 'synced'
        }
    
    @staticmethod
    def map_stock(data: Dict[str, Any]) -> Dict[str, Any]:
        """Map MoySklad stock data to database model fields."""
        return {
            'external_id': MoySkladMapper.extract_id_from_meta(data.get('meta')),
            'stock': data.get('stock', 0) / 1000,  # Convert to units
            'in_transit': data.get('inTransit', 0) / 1000,
            'reserve': data.get('reserve', 0) / 1000,
            'available': data.get('quantity', 0) / 1000,
            'external_meta': json.dumps(data.get('meta', {})),
            'last_sync_at': datetime.utcnow(),
            'sync_status': 'synced'
        }

