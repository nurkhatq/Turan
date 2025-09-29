#!/usr/bin/env python3
"""
Debug script to check price extraction from MoySklad API responses.
"""

import asyncio
import sys
import json
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent))

async def debug_prices():
    """Debug price extraction issues."""
    print("🔍 Debugging MoySklad price extraction...")
    
    try:
        from app.services.integrations.moysklad.client import MoySkladClient
        
        async with MoySkladClient() as client:
            # Get products with all price-related fields
            print("\n1️⃣ Fetching products with all price fields...")
            products = await client.get("entity/product", {
                "limit": 3,
                "expand": "salePrices,buyPrice,minPrice"
            })
            
            for i, product in enumerate(products.get("rows", [])):
                print(f"\n--- Product {i+1}: {product.get('name', 'No name')} ---")
                print(f"ID: {product.get('id')}")
                
                # Raw salePrices
                sale_prices = product.get("salePrices", [])
                print(f"Raw salePrices: {json.dumps(sale_prices, indent=2)}")
                
                # Raw buyPrice
                buy_price = product.get("buyPrice")
                print(f"Raw buyPrice: {json.dumps(buy_price, indent=2)}")
                
                # Raw minPrice
                min_price = product.get("minPrice")
                print(f"Raw minPrice: {json.dumps(min_price, indent=2)}")
                
                # Test our extraction methods
                if sale_prices:
                    if isinstance(sale_prices, list) and len(sale_prices) > 0:
                        first_price = sale_prices[0]
                        if isinstance(first_price, dict) and "value" in first_price:
                            extracted_price = first_price["value"] / 100
                            print(f"Extracted sale price: {extracted_price}")
                        else:
                            print(f"Unexpected salePrices format: {first_price}")
                    else:
                        print("salePrices is not a list or is empty")
                else:
                    print("No salePrices found")
                
                print("-" * 50)
            
            # Test assortment endpoint which might have different price structure
            print("\n2️⃣ Testing assortment endpoint...")
            assortment = await client.get("entity/assortment", {
                "limit": 2,
                "expand": "salePrices,buyPrice"
            })
            
            for i, item in enumerate(assortment.get("rows", [])):
                print(f"\n--- Assortment {i+1}: {item.get('name', 'No name')} ---")
                print(f"Type: {item.get('meta', {}).get('type', 'unknown')}")
                sale_prices = item.get("salePrices", [])
                print(f"Assortment salePrices: {json.dumps(sale_prices, indent=2)}")
            
            return True
            
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_prices())
    sys.exit(0 if success else 1)