# app/core/monitoring.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import psutil
import logging

logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Number of active connections'
)

SYSTEM_MEMORY_USAGE = Gauge(
    'system_memory_usage_bytes',
    'System memory usage in bytes'
)

SYSTEM_CPU_USAGE = Gauge(
    'system_cpu_usage_percent',
    'System CPU usage percentage'
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to collect Prometheus metrics."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Increment active connections
        ACTIVE_CONNECTIONS.inc()
        
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            logger.error(f"Request failed: {e}")
            response = Response(status_code=500)
        finally:
            # Decrement active connections
            ACTIVE_CONNECTIONS.dec()
        
        # Record metrics
        duration = time.time() - start_time
        REQUEST_DURATION.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=status_code
        ).inc()
        
        return response


def setup_prometheus_metrics(app: FastAPI):
    """Setup Prometheus metrics collection."""
    
    # Add Prometheus middleware
    app.add_middleware(PrometheusMiddleware)
    
    @app.get("/metrics")
    async def metrics():
        """Prometheus metrics endpoint."""
        # Update system metrics
        try:
            SYSTEM_MEMORY_USAGE.set(psutil.virtual_memory().used)
            SYSTEM_CPU_USAGE.set(psutil.cpu_percent())
        except Exception as e:
            logger.error(f"Failed to update system metrics: {e}")
        
        return Response(
            content=generate_latest(),
            media_type="text/plain"
        )
