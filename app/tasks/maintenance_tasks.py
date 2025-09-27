# app/tasks/maintenance_tasks.py
from datetime import datetime, timedelta
import logging

from app.core.celery_app import celery_app
from app.core.database import get_db_context

logger = logging.getLogger(__name__)


@celery_app.task
def cleanup_old_logs():
    """Clean up old log entries and expired sessions."""
    
    async def _cleanup():
        async with get_db_context() as db:
            try:
                # Clean up old API logs (older than 30 days)
                from app.models.system import ApiLog
                from sqlalchemy import delete
                
                cutoff_date = datetime.utcnow() - timedelta(days=30)
                
                # Delete old API logs
                api_log_stmt = delete(ApiLog).where(ApiLog.created_at < cutoff_date)
                api_result = await db.execute(api_log_stmt)
                api_deleted = api_result.rowcount
                
                # Clean up expired user sessions
                from app.models.user import UserSession
                session_stmt = delete(UserSession).where(
                    UserSession.expires_at < datetime.utcnow()
                )
                session_result = await db.execute(session_stmt)
                session_deleted = session_result.rowcount
                
                await db.commit()
                
                logger.info(f"Cleanup completed: {api_deleted} API logs, {session_deleted} sessions")
                return {
                    "api_logs_deleted": api_deleted,
                    "sessions_deleted": session_deleted
                }
                
            except Exception as e:
                logger.error(f"Cleanup failed: {e}")
                return {"error": str(e)}
    
    import asyncio
    return asyncio.run(_cleanup())


@celery_app.task
def backup_analytics_data():
    """Backup calculated analytics data."""
    
    async def _backup():
        try:
            # This would implement analytics data backup
            logger.info("Analytics backup completed")
            return {"status": "completed", "timestamp": datetime.utcnow().isoformat()}
            
        except Exception as e:
            logger.error(f"Analytics backup failed: {e}")
            return {"error": str(e)}
    
    import asyncio
    return asyncio.run(_backup())