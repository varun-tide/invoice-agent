"""
Invoice Agent API Server
Following Clean Architecture with SOLID principles
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

from .config import settings
from .api import create_api_router
from .dependencies import (
    get_conversation_use_case,
    get_invoice_creation_use_case,
    get_session_management_use_case,
    get_container
)


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan management
    """
    # Startup
    logger.info("🚀 Starting Invoice Agent API...")
    logger.info(f"🤖 Anthropic API configured: {settings.is_anthropic_configured}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Invoice Agent API...")


# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Exception",
            "message": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )


# API endpoints
@app.get("/")
async def read_root():
    """Root endpoint with API information"""
    return {
        "message": "🤖 Invoice Agent API",
        "version": settings.api_version,
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "anthropic_configured": settings.is_anthropic_configured,
        "endpoints": {
            "health": "/api/v1/health",
            "conversation": "/api/v1/conversation",
            "approve": "/api/v1/invoice/approve",
            "session": "/api/v1/session/{session_id}",
            "docs": "/docs"
        }
    }



api_router = create_api_router(
    conversation_use_case=get_conversation_use_case(),
    invoice_creation_use_case=get_invoice_creation_use_case(),
    session_management_use_case=get_session_management_use_case()
)

app.include_router(api_router, prefix="/api/v1", tags=["Invoice Agent"])


# Debug endpoints (only in development)
if settings.debug:
    @app.get("/debug/sessions")
    async def debug_get_all_sessions():
        """Debug: Get all sessions"""
        container = get_container()
        sessions = container.session_repository.get_all_sessions()
        return {
            "total_sessions": len(sessions),
            "sessions": {
                session_id: {
                    "status": session.status,
                    "created_at": session.created_at.isoformat(),
                    "invoice_complete": session.invoice_data.is_complete(),
                    "missing_fields": session.invoice_data.get_missing_fields()
                }
                for session_id, session in sessions.items()
            }
        }
    
    @app.get("/debug/invoices")
    async def debug_get_all_invoices():
        """Debug: Get all created invoices"""
        container = get_container()
        invoices = container.invoice_repository.get_all_invoices()
        return {
            "total_invoices": len(invoices),
            "invoices": list(invoices.values())
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server.server:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )