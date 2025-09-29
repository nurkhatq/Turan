# app/tasks/sync_tasks_fixed.py
"""
Fixed Celery tasks for MoySklad synchronization using the corrected sync service.
"""

from celery import current_task
from datetime import datetime
import logging
import asyncio

from app.core.celery_app import celery_app
from app.core.database import get_db_context
from app.services.integrations.moysklad.sync_service_fixed import FixedMoySkladSyncService
from app.models.system import SyncJob
from app.core.exceptions import IntegrationError

logger = logging.getLogger(__name__)


def run_async_in_celery(coro):
    """
    Run async coroutine in Celery with proper event loop handling.
    """
    try:
        # Try to get existing event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(coro)
    except RuntimeError:
        # No event loop exists, create new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()


@celery_app.task(bind=True)
def moysklad_full_sync_fixed(self):
    """Fixed Celery task for full MoySklad synchronization with proper data handling."""
    task_id = self.request.id
    
    async def _sync():
        # Import needed modules at function start
        from app.models.system import IntegrationConfig
        from sqlalchemy import select
        from datetime import timedelta
        
        async with get_db_context() as db:
            # Create sync job record
            sync_job = SyncJob(
                job_id=task_id,
                service_name="moysklad",
                job_type="full_sync_fixed",
                status="running",
                started_at=datetime.utcnow()
            )
            db.add(sync_job)
            await db.commit()
            
            try:
                logger.info(f"🚀 Starting FIXED full MoySklad synchronization (task: {task_id})")
                
                # Create fixed sync service and perform real synchronization
                sync_service = FixedMoySkladSyncService(db)
                results = await sync_service.full_sync()
                
                # Update job status with real results
                sync_job.status = "completed"
                sync_job.completed_at = datetime.utcnow()
                sync_job.result_data = results
                
                # Calculate totals from real results
                summary = results.get("summary", {})
                sync_job.total_items = summary.get("total_created", 0) + summary.get("total_updated", 0)
                sync_job.processed_items = sync_job.total_items
                sync_job.failed_items = summary.get("total_errors", 0)
                
                # Update integration config status
                stmt = select(IntegrationConfig).where(IntegrationConfig.service_name == "moysklad")
                config_result = await db.execute(stmt)
                config = config_result.scalar_one_or_none()
                
                if config:
                    config.last_sync_at = datetime.utcnow()
                    config.sync_status = "active"
                    config.next_sync_at = datetime.utcnow() + timedelta(minutes=config.sync_interval_minutes)
                    config.error_message = None
                
                await db.commit()
                
                logger.info(f"✅ FIXED full sync completed successfully: {results}")
                return results
                
            except IntegrationError as e:
                logger.error(f"❌ Integration error in FIXED full sync: {e.message}")
                
                # Update job status with integration error
                sync_job.status = "failed"
                sync_job.completed_at = datetime.utcnow()
                sync_job.error_message = f"Integration error: {e.message}"
                sync_job.failed_items = 1
                
                await db.commit()
                raise
                
            except Exception as e:
                logger.error(f"❌ Unexpected error in FIXED full sync: {e}")
                
                # Update job status with unexpected error
                sync_job.status = "failed"
                sync_job.completed_at = datetime.utcnow()
                sync_job.error_message = f"Unexpected error: {str(e)}"
                sync_job.failed_items = 1
                
                await db.commit()
                raise
    
    return run_async_in_celery(_sync())


@celery_app.task(bind=True)
def moysklad_incremental_sync_fixed(self):
    """Fixed Celery task for incremental MoySklad synchronization."""
    task_id = self.request.id
    
    async def _sync():
        # Import needed modules at function start
        from app.models.system import IntegrationConfig
        from sqlalchemy import select
        from datetime import timedelta
        
        async with get_db_context() as db:
            # Create sync job record
            sync_job = SyncJob(
                job_id=task_id,
                service_name="moysklad",
                job_type="incremental_sync_fixed",
                status="running",
                started_at=datetime.utcnow()
            )
            db.add(sync_job)
            await db.commit()
            
            try:
                logger.info(f"🔄 Starting FIXED incremental MoySklad synchronization (task: {task_id})")
                
                # Check if integration is enabled
                stmt = select(IntegrationConfig).where(
                    IntegrationConfig.service_name == "moysklad"
                )
                config = await db.execute(stmt)
                integration_config = config.scalar_one_or_none()
                
                if not integration_config or not integration_config.is_enabled:
                    logger.warning("MoySklad integration is not enabled, skipping incremental sync")
                    sync_job.status = "skipped"
                    sync_job.completed_at = datetime.utcnow()
                    sync_job.result_data = {"message": "Integration not enabled"}
                    await db.commit()
                    return {"message": "Integration not enabled", "status": "skipped"}
                
                # Create fixed sync service and perform real incremental synchronization
                sync_service = FixedMoySkladSyncService(db)
                results = await sync_service.incremental_sync()
                
                # Update job status with real results
                sync_job.status = "completed"
                sync_job.completed_at = datetime.utcnow()
                sync_job.result_data = results
                
                # Calculate totals from real results
                total_updated = results.get("total_updated", 0)
                sync_job.total_items = total_updated
                sync_job.processed_items = total_updated
                
                # Update integration config status
                stmt = select(IntegrationConfig).where(IntegrationConfig.service_name == "moysklad")
                config_result = await db.execute(stmt)
                config = config_result.scalar_one_or_none()
                
                if config:
                    config.last_sync_at = datetime.utcnow()
                    config.sync_status = "active"
                    config.next_sync_at = datetime.utcnow() + timedelta(minutes=config.sync_interval_minutes)
                    config.error_message = None
                
                await db.commit()
                
                logger.info(f"✅ FIXED incremental sync completed: {results}")
                return results
                
            except IntegrationError as e:
                logger.error(f"❌ Integration error in FIXED incremental sync: {e.message}")
                
                # Update job status with integration error
                sync_job.status = "failed"
                sync_job.completed_at = datetime.utcnow()
                sync_job.error_message = f"Integration error: {e.message}"
                sync_job.failed_items = 1
                
                await db.commit()
                
                # Don't raise for incremental sync to avoid breaking the schedule
                return {"error": f"Integration error: {e.message}", "task_id": task_id}
                
            except Exception as e:
                logger.error(f"❌ Unexpected error in FIXED incremental sync: {e}")
                
                # Update job status with unexpected error
                sync_job.status = "failed"
                sync_job.completed_at = datetime.utcnow()
                sync_job.error_message = f"Unexpected error: {str(e)}"
                sync_job.failed_items = 1
                
                await db.commit()
                
                # Don't raise for incremental sync to avoid breaking the schedule
                return {"error": f"Unexpected error: {str(e)}", "task_id": task_id}
    
    return run_async_in_celery(_sync())


@celery_app.task
def test_moysklad_connection_fixed(credentials: dict):
    """Fixed MoySklad API connection test with improved error handling."""
    
    async def _test():
        try:
            logger.info("🔍 Testing MoySklad connection with FIXED client...")
            
            from app.services.integrations.moysklad.client import MoySkladClient
            
            # Create client with provided credentials
            async with MoySkladClient(
                username=credentials.get('username'),
                password=credentials.get('password'),
                token=credentials.get('token')
            ) as client:
                # Perform real connection test
                result = await client.test_connection()
                
                logger.info(f"✅ FIXED connection test completed: {result}")
                return result
                
        except Exception as e:
            logger.error(f"❌ FIXED connection test failed: {e}")
            return {
                "success": False,
                "message": f"Connection test failed: {str(e)}",
                "details": {"error": str(e)}
            }
    
    return run_async_in_celery(_test())


# Additional debug tasks for testing specific parts
@celery_app.task
def debug_moysklad_products():
    """Debug task to test product fetching specifically."""
    
    async def _debug():
        try:
            from app.services.integrations.moysklad.client import MoySkladClient
            
            async with MoySkladClient() as client:
                logger.info("🛍️ Debug: Testing product fetching...")
                
                # Test connection first
                connection_test = await client.test_connection()
                logger.info(f"Connection test: {connection_test}")
                
                # Try to fetch a small number of products
                products = await client.get("entity/product", {"limit": 5})
                logger.info(f"Products response: {products}")
                
                # Try with expand
                products_expanded = await client.get("entity/product", {
                    "limit": 3,
                    "expand": "productFolder,uom,salePrices"
                })
                logger.info(f"Products expanded: {products_expanded}")
                
                return {
                    "success": True,
                    "connection": connection_test,
                    "products_count": len(products.get("rows", [])),
                    "expanded_count": len(products_expanded.get("rows", [])),
                    "sample_product": products_expanded.get("rows", [{}])[0] if products_expanded.get("rows") else None
                }
                
        except Exception as e:
            logger.error(f"❌ Debug products failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    return run_async_in_celery(_debug())