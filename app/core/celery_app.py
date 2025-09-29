# app/core/celery_app.py
from celery import Celery
from app.core.config import Settings

settings = Settings()

# Create Celery app
celery_app = Celery(
    "business_crm",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.sync_tasks",
        "app.tasks.analytics_tasks",
        "app.tasks.notification_tasks",
        "app.tasks.maintenance_tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,  # 1 hour
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    beat_schedule={
        "moysklad-incremental-sync": {
            "task": "app.tasks.sync_tasks.moysklad_incremental_sync",
            "schedule": settings.MOYSKLAD_SYNC_INTERVAL_MINUTES * 60.0,  # Convert to seconds
        },
        "calculate-daily-analytics": {
            "task": "app.tasks.analytics_tasks.calculate_daily_analytics",
            "schedule": 3600.0,  # Every hour
        },
        "cleanup-old-logs": {
            "task": "app.tasks.maintenance_tasks.cleanup_old_logs",
            "schedule": 86400.0,  # Daily
        }
    }
)