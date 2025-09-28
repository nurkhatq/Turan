# app/tasks/sync_tasks_new.py
"""
Synchronous Celery tasks for MoySklad synchronization.

This version uses synchronous database operations to avoid
asyncio event loop conflicts in Celery workers.
"""

from celery import current_task
from datetime import datetime
import logging
import json

from app.core.celery_app import celery_app
from app.core.database_sync import get_sync_db
from app.models.system import SyncJob, IntegrationConfig
from app.core.exceptions import IntegrationError
from sqlalchemy import select

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def moysklad_full_sync(self):
    """Celery task for full MoySklad synchronization (synchronous version)."""
    task_id = self.request.id
    
    with get_sync_db() as db:
        # Create sync job record
        sync_job = SyncJob(
            job_id=task_id,
            service_name="moysklad",
            job_type="full_sync",
            status="running",
            started_at=datetime.utcnow()
        )
        db.add(sync_job)
        db.commit()
        
        try:
            # Check if MoySklad integration is enabled
            stmt = select(IntegrationConfig).where(
                IntegrationConfig.service_name == "moysklad"
            )
            config = db.execute(stmt).scalar_one_or_none()
            
            if not config or not config.is_enabled:
                logger.warning("MoySklad integration is not enabled, skipping sync")
                sync_job.status = "skipped"
                sync_job.completed_at = datetime.utcnow()
                sync_job.result_data = {"message": "Integration not enabled"}
                db.commit()
                return {"message": "Integration not enabled"}
            
            # TODO: Implement actual synchronization logic here
            # For now, just simulate a successful sync
            logger.info("Starting full MoySklad synchronization")
            
            # Simulate sync work
            results = {
                "products": {"created": 0, "updated": 0},
                "counterparties": {"created": 0, "updated": 0},
                "stores": {"created": 0, "updated": 0}
            }
            
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
            
            db.commit()
            
            logger.info(f"Full sync completed successfully: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Full sync failed: {e}")
            
            # Update job status
            sync_job.status = "failed"
            sync_job.completed_at = datetime.utcnow()
            sync_job.error_message = str(e)
            sync_job.failed_items = 1
            
            db.commit()
            
            raise


@celery_app.task(bind=True)
def moysklad_incremental_sync(self):
    """Celery task for incremental MoySklad synchronization (synchronous version)."""
    task_id = self.request.id
    
    with get_sync_db() as db:
        # Create sync job record
        sync_job = SyncJob(
            job_id=task_id,
            service_name="moysklad",
            job_type="incremental_sync",
            status="running",
            started_at=datetime.utcnow()
        )
        db.add(sync_job)
        db.commit()
        
        try:
            # Check if MoySklad integration is enabled
            stmt = select(IntegrationConfig).where(
                IntegrationConfig.service_name == "moysklad"
            )
            config = db.execute(stmt).scalar_one_or_none()
            
            if not config or not config.is_enabled:
                logger.warning("MoySklad integration is not enabled, skipping sync")
                sync_job.status = "skipped"
                sync_job.completed_at = datetime.utcnow()
                sync_job.result_data = {"message": "Integration not enabled"}
                db.commit()
                return {"message": "Integration not enabled"}
            
            # TODO: Implement actual incremental synchronization logic here
            logger.info("Starting incremental MoySklad synchronization")
            
            # Simulate incremental sync
            results = {
                "products": {"updated": 0},
                "counterparties": {"updated": 0},
                "stock": {"updated": 0}
            }
            
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
            
            db.commit()
            
            logger.info(f"Incremental sync completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Incremental sync failed: {e}")
            
            # Update job status
            sync_job.status = "failed"
            sync_job.completed_at = datetime.utcnow()
            sync_job.error_message = str(e)
            sync_job.failed_items = 1
            
            db.commit()
            
            # Don't raise for incremental sync to avoid breaking the schedule
            return {"error": str(e)}


@celery_app.task
def test_moysklad_connection(credentials: dict):
    """Test MoySklad API connection (synchronous version)."""
    
    try:
        # TODO: Implement actual connection test
        # For now, just simulate a successful test
        logger.info("Testing MoySklad connection")
        
        # Simulate connection test
        if credentials.get('token') or (credentials.get('username') and credentials.get('password')):
            return {
                "success": True,
                "message": "Connection test successful (simulated)",
                "details": {
                    "auth_method": "token" if credentials.get('token') else "credentials"
                }
            }
        else:
            return {
                "success": False,
                "message": "No credentials provided",
                "details": {"error": "Missing token or username/password"}
            }
            
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return {
            "success": False,
            "message": f"Connection test failed: {str(e)}",
            "details": {"error": str(e)}
        }
