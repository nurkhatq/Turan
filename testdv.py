#!/usr/bin/env python3
"""
Test script to verify MoySklad fixes are working correctly.
Run this to test the corrected API client and sync functionality.
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent.parent))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
            
            # Test 2: Get product folders
            print("\n2️⃣ Testing product folders...")
            folders = await client.get_product_folders()
            print(f"   Found {len(folders)} product folders")
            if folders:
                print(f"   Sample folder: {folders[0].get('name', 'No name')}")
            
            # Test 3: Get units of measure
            print("\n3️⃣ Testing units of measure...")
            units = await client.get_units_of_measure()
            print(f"   Found {len(units)} units")
            if units:
                print(f"   Sample unit: {units[0].get('name', 'No name')}")
            
            # Test 4: Get products with expand
            print("\n4️⃣ Testing products with expand...")
            products = await client.get("entity/product", {
                "limit": 5,
                "expand": "productFolder,uom,salePrices,buyPrice"
            })
            product_rows = products.get("rows", [])
            print(f"   Found {len(product_rows)} products")
            
            if product_rows:
                sample = product_rows[0]
                print(f"   Sample product: {sample.get('name', 'No name')}")
                print(f"   Has folder: {'productFolder' in sample}")
                print(f"   Has uom: {'uom' in sample}")
                print(f"   Has salePrices: {'salePrices' in sample}")
                
                # Test price extraction
                if 'salePrices' in sample and sample['salePrices']:
                    sale_price = sample['salePrices'][0].get('value', 0) / 100
                    print(f"   Sale price: {sale_price}")
            
            # Test 5: Get stock report
            print("\n5️⃣ Testing stock report...")
            stock = await client.get("report/stock/all", {"limit": 5})
            stock_rows = stock.get("rows", [])
            print(f"   Found {len(stock_rows)} stock records")
            
            if stock_rows:
                sample_stock = stock_rows[0]
                print(f"   Sample stock: {sample_stock.get('name', 'No name')}")
                print(f"   Stock quantity: {sample_stock.get('stock', 0)}")
            
            return True
            
    except Exception as e:
        print(f"❌ Client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_sync_service():
    """Test the fixed sync service."""
    print("\n🔄 Testing fixed sync service...")
    
    try:
        from app.core.database import get_db_context
        from app.services.integrations.moysklad.sync_service_fixed import FixedMoySkladSyncService
        
        async with get_db_context() as db:
            sync_service = FixedMoySkladSyncService(db)
            
            # Test creating client
            print("   Testing client creation...")
            try:
                async with await sync_service.create_moysklad_client() as client:
                    test_result = await client.test_connection()
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

async def test_data_extraction():
    """Test data extraction methods."""
    print("\n🔧 Testing data extraction methods...")
    
    try:
        from app.services.integrations.moysklad.sync_service_fixed import FixedMoySkladSyncService
        from app.core.database import get_db_context
        
        async with get_db_context() as db:
            sync_service = FixedMoySkladSyncService(db)
            
            # Test price extraction
            price_test_cases = [
                {"value": 12500},  # 125.00 rubles
                12500,  # Direct value
                None,  # No price
                {"value": 0}  # Zero price
            ]
            
            print("   Testing price extraction:")
            for i, test_case in enumerate(price_test_cases):
                result = sync_service.extract_price_value(test_case)
                print(f"     Test {i+1}: {test_case} -> {result}")
            
            # Test sale prices extraction
            sale_prices_test = [
                {"value": 15000}  # 150.00 rubles
            ]
            
            sale_price = sync_service.extract_sale_prices(sale_prices_test)
            print(f"   Sale prices extraction: {sale_prices_test} -> {sale_price}")
            
            # Test ID extraction
            test_objects = [
                {"meta": {"href": "https://api.moysklad.ru/api/remap/1.2/entity/product/123"}},
                "https://api.moysklad.ru/api/remap/1.2/entity/productfolder/456",
                None,
                {}
            ]
            
            print("   Testing ID extraction:")
            for i, test_obj in enumerate(test_objects):
                result = sync_service.extract_id_from_meta_or_href(test_obj)
                print(f"     Test {i+1}: -> {result}")
            
            return True
            
    except Exception as e:
        print(f"❌ Data extraction test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_database_models():
    """Test that database models can be imported and created."""
    print("\n🗄️ Testing database models...")
    
    try:
        # Test imports
        from app.models.moysklad.products import Product, ProductFolder, UnitOfMeasure, Service
        from app.models.moysklad.inventory import Store, Stock
        from app.models.moysklad.counterparties import Counterparty
        
        print("   ✅ All model imports successful")
        
        # Test creating instances (not saving)
        test_product = Product(
            external_id="test-123",
            name="Test Product",
            folder_external_id="folder-123",
            unit_external_id="unit-123"
        )
        
        test_stock = Stock(
            external_id="stock-123",
            product_external_id="test-123",
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

async def run_full_test():
    """Run all tests."""
    print("🚀 Starting MoySklad fixes verification...\n")
    
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
        print("\n🎉 All tests passed! Your MoySklad integration should now work correctly.")
        print("\n💡 Next steps:")
        print("   1. Run the migration: alembic upgrade head")
        print("   2. Test with: python -c 'from app.tasks.sync_tasks_fixed import debug_moysklad_products; debug_moysklad_products.delay()'")
        print("   3. Try a full sync: python -c 'from app.tasks.sync_tasks_fixed import moysklad_full_sync_fixed; moysklad_full_sync_fixed.delay()'")
    else:
        print("\n⚠️  Some tests failed. Check the errors above and fix them before proceeding.")
        print("\n🔧 Common fixes:")
        print("   - Make sure MoySklad credentials are set in .env")
        print("   - Run database migrations: alembic upgrade head")
        print("   - Check that Redis and PostgreSQL are running")
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(run_full_test())
    sys.exit(0 if success else 1)