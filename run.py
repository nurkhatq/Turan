#!/usr/bin/env python3
"""
Simple script to run the Business CRM application.
"""
import uvicorn
from app.core.config import Settings

if __name__ == "__main__":
    settings = Settings()
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

