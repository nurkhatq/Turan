# app/tasks/sync_tasks_real.py
"""
Real Celery tasks for MoySklad synchronization with actual API calls and database operations.
"""

from celery import current_task
from datetime import datetime
import logging
import asyncio

from app.core.celery_app import celery_app
from app.core.database import get_db_context
from app.services.integrations.moysklad.sync_service import MoySkladSyncService
from app.models.system import SyncJob
from app.core.exceptions import IntegrationError
from sqlalchemy import select

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
def moysklad_full_sync(self):
    """Real Celery task for full MoySklad synchronization with actual API calls."""
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
                job_type="full_sync",
                status="running",
                started_at=datetime.utcnow()
            )
            db.add(sync_job)
            await db.commit()
            
            try:
                logger.info(f"🚀 Starting real full MoySklad synchronization (task: {task_id})")
                
                # Create sync service and perform real synchronization
                sync_service = MoySkladSyncService(db)
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
                
                logger.info(f"✅ Real full sync completed successfully: {results}")
                return results
                
            except IntegrationError as e:
                logger.error(f"❌ Integration error in full sync: {e.message}")
                
                # Update job status with integration error
                sync_job.status = "failed"
                sync_job.completed_at = datetime.utcnow()
                sync_job.error_message = f"Integration error: {e.message}"
                sync_job.failed_items = 1
                
                await db.commit()
                raise
                
            except Exception as e:
                logger.error(f"❌ Unexpected error in full sync: {e}")
                
                # Update job status with unexpected error
                sync_job.status = "failed"
                sync_job.completed_at = datetime.utcnow()
                sync_job.error_message = f"Unexpected error: {str(e)}"
                sync_job.failed_items = 1
                
                await db.commit()
                raise
    
    return run_async_in_celery(_sync())


@celery_app.task(bind=True)
def moysklad_incremental_sync(self):
    """Real Celery task for incremental MoySklad synchronization with actual API calls."""
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
                job_type="incremental_sync",
                status="running",
                started_at=datetime.utcnow()
            )
            db.add(sync_job)
            await db.commit()
            
            try:
                logger.info(f"🔄 Starting real incremental MoySklad synchronization (task: {task_id})")
                
                # Check if integration is enabled
                from app.models.system import IntegrationConfig
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
                
                # Create sync service and perform real incremental synchronization
                sync_service = MoySkladSyncService(db)
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
                
                logger.info(f"✅ Real incremental sync completed: {results}")
                return results
                
            except IntegrationError as e:
                logger.error(f"❌ Integration error in incremental sync: {e.message}")
                
                # Update job status with integration error
                sync_job.status = "failed"
                sync_job.completed_at = datetime.utcnow()
                sync_job.error_message = f"Integration error: {e.message}"
                sync_job.failed_items = 1
                
                await db.commit()
                
                # Don't raise for incremental sync to avoid breaking the schedule
                return {"error": f"Integration error: {e.message}", "task_id": task_id}
                
            except Exception as e:
                logger.error(f"❌ Unexpected error in incremental sync: {e}")
                
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
def test_moysklad_connection(credentials: dict):
    """Real MoySklad API connection test with actual API calls."""
    
    async def _test():
        try:
            logger.info("🔍 Testing real MoySklad connection...")
            
            from app.services.integrations.moysklad.client import MoySkladClient
            
            # Create client with provided credentials
            async with MoySkladClient(
                username=credentials.get('username'),
                password=credentials.get('password'),
                token=credentials.get('token')
            ) as client:
                # Perform real connection test
                result = await client.test_connection()
                
                logger.info(f"✅ Real connection test completed: {result}")
                return result
                
        except Exception as e:
            logger.error(f"❌ Real connection test failed: {e}")
            return {
                "success": False,
                "message": f"Connection test failed: {str(e)}",
                "details": {"error": str(e)}
            }
    
    return run_async_in_celery(_test())
