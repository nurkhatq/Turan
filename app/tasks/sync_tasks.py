# app/tasks/sync_tasks.py
from celery import current_task
from datetime import datetime
import logging
import json

from app.core.celery_app import celery_app
from app.core.database import get_db_context
from app.services.integrations.moysklad.sync_service import MoySkladSyncService
from app.models.system import SyncJob
from app.core.exceptions import IntegrationError

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def moysklad_full_sync(self):
    """Celery task for full MoySklad synchronization."""
    task_id = self.request.id
    
    async def _sync():
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
                # Perform synchronization
                sync_service = MoySkladSyncService(db)
                results = await sync_service.full_sync()
                
                # Update job status
                sync_job.status = "completed"
                sync_job.completed_at = datetime.utcnow()
                sync_job.result_data = results
                
                # Calculate totals
                total_processed = sum(
                    result.get('created', 0) + result.get('updated', 0)
                    for result in results.values()
                    if isinstance(result, dict)
                )
                sync_job.total_items = total_processed
                sync_job.processed_items = total_processed
                
                await db.commit()
                
                logger.info(f"Full sync completed successfully: {results}")
                return results
                
            except Exception as e:
                logger.error(f"Full sync failed: {e}")
                
                # Update job status
                sync_job.status = "failed"
                sync_job.completed_at = datetime.utcnow()
                sync_job.error_message = str(e)
                sync_job.failed_items = 1
                
                await db.commit()
                
                raise
    
    import asyncio
    return asyncio.run(_sync())


@celery_app.task(bind=True)
def moysklad_incremental_sync(self):
    """Celery task for incremental MoySklad synchronization."""
    task_id = self.request.id
    
    async def _sync():
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
                # Perform synchronization
                sync_service = MoySkladSyncService(db)
                results = await sync_service.incremental_sync()
                
                # Update job status
                sync_job.status = "completed"
                sync_job.completed_at = datetime.utcnow()
                sync_job.result_data = results
                
                # Calculate totals
                total_processed = sum(
                    result.get('created', 0) + result.get('updated', 0)
                    for result in results.values()
                    if isinstance(result, dict)
                )
                sync_job.total_items = total_processed
                sync_job.processed_items = total_processed
                
                await db.commit()
                
                logger.info(f"Incremental sync completed: {results}")
                return results
                
            except Exception as e:
                logger.error(f"Incremental sync failed: {e}")
                
                # Update job status
                sync_job.status = "failed"
                sync_job.completed_at = datetime.utcnow()
                sync_job.error_message = str(e)
                sync_job.failed_items = 1
                
                await db.commit()
                
                # Don't raise for incremental sync to avoid breaking the schedule
                return {"error": str(e)}
    
    import asyncio
    return asyncio.run(_sync())


@celery_app.task
def test_moysklad_connection(credentials: dict):
    """Test MoySklad API connection."""
    
    async def _test():
        from app.services.integrations.moysklad.client import MoySkladClient
        
        try:
            async with MoySkladClient(
                username=credentials.get('username'),
                password=credentials.get('password'),
                token=credentials.get('token')
            ) as client:
                # Try to fetch a small amount of data
                products = await client.get("entity/product", {"limit": 1})
                
                return {
                    "success": True,
                    "message": "Connection successful",
                    "details": {
                        "products_accessible": len(products.get('rows', [])) >= 0
                    }
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}",
                "details": {"error": str(e)}
            }
    
    import asyncio
    return asyncio.run(_test())