"""
FastAPI application entry point.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import time

from .config import settings
from .core.plugins.registry import plugin_registry
from .core.plugins.rules import RulePluginFactory
from .api.routes import strategies

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Wafer Sampling Strategy System")
    
    # Initialize plugin system
    rule_factory = RulePluginFactory(plugin_registry)
    app.state.rule_factory = rule_factory
    
    # Auto-discover and register plugins if enabled
    if settings.plugins.auto_discover_plugins:
        logger.info("Auto-discovering plugins...")
        # Plugin discovery logic would go here
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    plugin_registry.shutdown()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title=settings.api.title,
        description=settings.api.description,
        version=settings.api.version,
        docs_url=settings.api.docs_url if settings.debug else None,
        redoc_url=settings.api.redoc_url if settings.debug else None,
        openapi_url=settings.api.openapi_url if settings.debug else None,
        lifespan=lifespan
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api.allow_origins,
        allow_credentials=settings.api.allow_credentials,
        allow_methods=settings.api.allow_methods,
        allow_headers=settings.api.allow_headers,
    )
    
    # Compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Request timing middleware
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Global exception handler caught: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "message": "Internal server error",
                "detail": str(exc) if settings.debug else "An error occurred"
            }
        )
    
    # Health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "environment": settings.environment,
            "version": settings.api.version,
            "timestamp": time.time()
        }
    
    # Include routers
    app.include_router(strategies.router)
    
    return app


# Create application instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.logging.level.lower()
    )