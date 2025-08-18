"""
API Routes - HTTP endpoints
Following Clean Architecture: Interface adapters layer
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from .models import (
    ConversationRequest,
    ConversationResponse, 
    InvoiceApprovalRequest,
    InvoiceApprovalResponse,
    SessionInfoResponse,
    SessionResetResponse,
    HealthCheckResponse,
    ErrorResponse
)
from ..application.use_cases import (
    ConversationUseCase,
    InvoiceCreationUseCase,
    SessionManagementUseCase
)


class APIRoutes:
    """
    API Routes class - Dependency Injection for use cases
    Single Responsibility: Handle HTTP routing and response formatting
    """
    
    def __init__(
        self,
        conversation_use_case: ConversationUseCase,
        invoice_creation_use_case: InvoiceCreationUseCase,
        session_management_use_case: SessionManagementUseCase
    ):
        self.conversation_use_case = conversation_use_case
        self.invoice_creation_use_case = invoice_creation_use_case
        self.session_management_use_case = session_management_use_case
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self) -> None:
        """Setup all API routes"""
        
        @self.router.post(
            "/conversation",
            response_model=ConversationResponse,
            summary="Process user conversation",
            description="Handle conversational invoice creation"
        )
        async def handle_conversation(request: ConversationRequest) -> ConversationResponse:
            """Handle conversation with the invoice agent"""
            try:
                result = await self.conversation_use_case.handle_conversation(
                    user_input=request.user_input,
                    session_id=request.session_id,
                    user_id=request.user_id
                )
                
                return ConversationResponse(**result)
                
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
        
        @self.router.post(
            "/invoice/approve",
            response_model=InvoiceApprovalResponse,
            summary="Approve invoice creation",
            description="Approve and create invoice from session data"
        )
        async def approve_invoice(request: InvoiceApprovalRequest) -> InvoiceApprovalResponse:
            """Approve and create invoice"""
            try:
                result = await self.invoice_creation_use_case.approve_invoice(
                    session_id=request.session_id,
                    action=request.action,
                    field_updates=request.field_updates
                )
                
                return InvoiceApprovalResponse(**result)
                
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
        
        @self.router.get(
            "/session/{session_id}",
            response_model=SessionInfoResponse,
            summary="Get session information",
            description="Retrieve session details and status"
        )
        async def get_session_info(session_id: str) -> SessionInfoResponse:
            """Get session information"""
            try:
                result = await self.session_management_use_case.get_session_info(session_id)
                return SessionInfoResponse(**result)
                
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
        
        @self.router.post(
            "/session/{session_id}/reset",
            response_model=SessionResetResponse,
            summary="Reset session",
            description="Reset session data while preserving metadata"
        )
        async def reset_session(session_id: str) -> SessionResetResponse:
            """Reset session data"""
            try:
                result = await self.session_management_use_case.reset_session(session_id)
                return SessionResetResponse(**result)
                
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
        
        @self.router.get(
            "/health",
            response_model=HealthCheckResponse,
            summary="Health check",
            description="Check API and agent service health"
        )
        async def health_check() -> HealthCheckResponse:
            """Health check endpoint"""
            try:
                # Test agent availability by creating a test session
                test_result = await self.conversation_use_case.handle_conversation(
                    user_input="test",
                    session_id=None,
                    user_id="health_check"
                )
                agent_available = bool(test_result.get("success"))
                
                return HealthCheckResponse(
                    status="healthy",
                    timestamp=datetime.now(),
                    version="1.0.0",
                    agent_available=agent_available
                )
                
            except Exception as e:
                return HealthCheckResponse(
                    status="degraded",
                    timestamp=datetime.now(),
                    version="1.0.0",
                    agent_available=False
                )


def create_api_router(
    conversation_use_case: ConversationUseCase,
    invoice_creation_use_case: InvoiceCreationUseCase,
    session_management_use_case: SessionManagementUseCase
) -> APIRouter:
    """
    Factory function to create API router with dependencies
    Dependency Injection: Inject use cases into routes
    """
    api_routes = APIRoutes(
        conversation_use_case,
        invoice_creation_use_case,
        session_management_use_case
    )
    return api_routes.router
