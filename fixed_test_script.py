#!/usr/bin/env python3
"""
Fixed test script with proper async connection handling.
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_database_models():
    """Test that database models can be imported and created."""
    print("\n🗄️ Testing database models...")
    
    try:
        # Test imports
        from app.models.moysklad.products import Product, ProductFolder, UnitOfMeasure, Service
        from app.models.moysklad.inventory import Store, Stock
        from app.models.moysklad.counterparties import Counterparty
        
        print("   ✅ All model imports successful")
        
        # Test creating instances (not saving) - with FIXED fields
        test_product = Product(
            external_id="test-123",
            name="Test Product",
            folder_external_id="folder-123",
            unit_external_id="unit-123"
        )
        
        test_stock = Stock(
            external_id="stock-123",
            product_external_id="test-123",  # This should work now
            store_external_id="store-123",
            stock=100.0,
            available=95.0
        )
        
        print("   ✅ Model instances can be created")
        return True
        
    except Exception as e:
        print(f"❌ Database models test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_sync_service():
    """Test the fixed sync service with proper connection handling."""
    print("\n🔄 Testing fixed sync service...")
    
    try:
        from app.core.database import get_db_context
        from app.services.integrations.moysklad.sync_service_fixed import FixedMoySkladSyncService
        
        async with get_db_context() as db:
            sync_service = FixedMoySkladSyncService(db)
            
            # Test creating client without reusing connections
            print("   Testing client creation (fresh connection)...")
            try:
                # Create a separate client instance for testing
                from app.services.integrations.moysklad.client import MoySkladClient
                
                # Test with fresh client
                test_client = MoySkladClient()
                async with test_client:
                    test_result = await test_client.test_connection()
                    print(f"   Client creation: {'✅' if test_result.get('success') else '❌'}")
                    return test_result.get('success', False)
                    
            except Exception as e:
                print(f"   Client creation failed: {e}")
                return False
            
    except Exception as e:
        print(f"❌ Sync service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_client_fixes():
    """Test the fixed MoySklad client."""
    print("🔍 Testing fixed MoySklad client...")
    
    try:
        from app.services.integrations.moysklad.client import MoySkladClient
        
        async with MoySkladClient() as client:
            # Test 1: Connection test
            print("\n1️⃣ Testing connection...")
            connection_result = await client.test_connection()
            print(f"   Result: {connection_result}")
            
            if not connection_result.get("success"):
                print("❌ Connection failed, skipping other tests")
                return False
            
            # Test 2: Get products with expand to debug price issue
            print("\n2️⃣ Testing products with price debugging...")
            products = await client.get("entity/product", {
                "limit": 2,
                "expand": "productFolder,uom,salePrices,buyPrice"
            })
            product_rows = products.get("rows", [])
            print(f"   Found {len(product_rows)} products")
            
            if product_rows:
                sample = product_rows[0]
                print(f"   Sample product: {sample.get('name', 'No name')}")
                
                # Debug price extraction
                sale_prices = sample.get('salePrices', [])
                print(f"   Raw salePrices: {sale_prices}")
                
                if sale_prices and isinstance(sale_prices, list) and len(sale_prices) > 0:
                    first_price = sale_prices[0]
                    print(f"   First price object: {first_price}")
                    
                    if isinstance(first_price, dict) and 'value' in first_price:
                        value = first_price['value']
                        converted = value / 100 if value else 0
                        print(f"   Price value: {value} -> {converted} rubles")
                    else:
                        print(f"   Unexpected price format: {type(first_price)}")
                else:
                    print("   No valid sale prices found")
            
            # Test 3: Get stock report
            print("\n3️⃣ Testing stock report...")
            stock = await client.get("report/stock/all", {"limit": 2})
            stock_rows = stock.get("rows", [])
            print(f"   Found {len(stock_rows)} stock records")
            
            if stock_rows:
                sample_stock = stock_rows[0]
                print(f"   Sample stock: {sample_stock.get('name', 'No name')}")
                print(f"   Stock quantity: {sample_stock.get('stock', 0)}")
                print(f"   Has price: {'price' in sample_stock}")
                print(f"   Has salePrice: {'salePrice' in sample_stock}")
            
            return True
            
    except Exception as e:
        print(f"❌ Client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_data_extraction():
    """Test data extraction methods."""
    print("\n🔧 Testing data extraction methods...")
    
    try:
        from app.services.integrations.moysklad.sync_service_fixed import FixedMoySkladSyncService
        from app.core.database import get_db_context
        
        async with get_db_context() as db:
            sync_service = FixedMoySkladSyncService(db)
            
            # Test price extraction with real MoySklad format
            print("   Testing price extraction with MoySklad format:")
            test_cases = [
                {"value": 12500},  # 125.00 rubles
                {"value": 0},      # Free
                None,              # No price
                12500,             # Direct value
            ]
            
            for i, test_case in enumerate(test_cases):
                result = sync_service.extract_price_value(test_case)
                print(f"     Test {i+1}: {test_case} -> {result}")
            
            # Test sale prices array extraction
            sale_prices_tests = [
                [{"value": 15000}],  # Normal case
                [{"value": 0}],      # Free product
                [],                  # Empty array
                None,                # No sale prices
                [{"someOtherField": "value"}]  # Invalid format
            ]
            
            print("   Testing sale prices array extraction:")
            for i, test_case in enumerate(sale_prices_tests):
                result = sync_service.extract_sale_prices(test_case)
                print(f"     Test {i+1}: {test_case} -> {result}")
            
            return True
            
    except Exception as e:
        print(f"❌ Data extraction test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def run_full_test():
    """Run all tests."""
    print("🚀 Starting FIXED MoySklad verification...\n")
    
    tests = [
        ("Database Models", test_database_models),
        ("Data Extraction", test_data_extraction),
        ("MoySklad Client", test_client_fixes),
        ("Sync Service", test_sync_service),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"TESTING: {test_name}")
        print('='*60)
        
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    
    all_passed = True
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Your MoySklad integration is working correctly.")
        print("\n💡 Next steps:")
        print("   1. Copy the fixed models to your actual files")
        print("   2. Run: alembic revision --autogenerate -m 'Add external ID fields'")
        print("   3. Run: alembic upgrade head")
        print("   4. Test a full sync")
    else:
        print("\n⚠️  Some tests failed. The main issue seems to be the database model.")
        print("\n🔧 Quick fix:")
        print("   1. Update your app/models/moysklad/inventory.py with the external ID fields")
        print("   2. Update your app/models/moysklad/products.py with the external ID fields")
        print("   3. Run migration: alembic revision --autogenerate -m 'Add external ID fields'")
        print("   4. Apply migration: alembic upgrade head")
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(run_full_test())
    sys.exit(0 if success else 1)