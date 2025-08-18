"""
Application Use Cases - Business logic orchestration
Following Clean Architecture: Application layer use cases
"""

import uuid
from typing import Optional
from datetime import datetime

from ..domain.entities import (
    ConversationSession, 
    InvoiceData, 
    InvoiceStatus,
    ConversationStatus,
    CreatedInvoice
)
from .interfaces import (
    IInvoiceAgentService, 
    ISessionRepository, 
    IInvoiceRepository,
    INotificationService
)


class ConversationUseCase:
    """
    Use case for handling conversation flow
    Single Responsibility: Orchestrate conversation logic
    """
    
    def __init__(
        self,
        agent_service: IInvoiceAgentService,
        session_repository: ISessionRepository
    ):
        self._agent_service = agent_service
        self._session_repository = session_repository
    
    async def handle_conversation(
        self, 
        user_input: str, 
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> dict:
        """
        Main conversation handling logic - API version with clean responses
        """
        # Get or create session
        if session_id:
            session = await self._session_repository.get_session(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
        else:
            session = await self._session_repository.create_session(user_id)
        
        # Process user input through agent using API method
        agent_response = await self._agent_service.process_user_input_api(
            user_input, session
        )
        
        # Update session timestamp
        session.update_timestamp()
        await self._session_repository.update_session(session)
        
        # Get session metadata
        session_metadata = await self._agent_service.get_session_metadata(session)
        
        # Structure the response based on agent response
        response = {
            "session_id": session.session_id,
            "session_metadata": session_metadata
        }
        
        # Merge agent response into the main response
        response.update(agent_response)
        
        return response


class InvoiceCreationUseCase:
    """
    Use case for creating invoices
    Single Responsibility: Handle invoice creation flow
    """
    
    def __init__(
        self,
        session_repository: ISessionRepository,
        invoice_repository: IInvoiceRepository,
        notification_service: Optional[INotificationService] = None
    ):
        self._session_repository = session_repository
        self._invoice_repository = invoice_repository
        self._notification_service = notification_service
    
    async def approve_invoice(
        self, 
        session_id: str, 
        action: str = "approve",
        field_updates: Optional[dict] = None
    ) -> dict:
        """
        Handle invoice approval and creation
        """
        # Get session
        session = await self._session_repository.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        if action == "approve":
            return await self._create_invoice(session)
        elif action == "edit" and field_updates:
            return await self._update_invoice_fields(session, field_updates)
        else:
            raise ValueError(f"Unsupported action: {action}")
    
    async def _create_invoice(self, session: ConversationSession) -> dict:
        """Create invoice from session data"""
        if not session.invoice_data.is_complete():
            missing_fields = session.invoice_data.get_missing_fields()
            raise ValueError(f"Invoice incomplete. Missing: {', '.join(missing_fields)}")
        
        # Create invoice
        created_invoice = await self._invoice_repository.create_invoice(
            session.invoice_data,
            session.user_id
        )
        
        # Update session status
        session.status = ConversationStatus.COMPLETED
        session.update_timestamp()
        await self._session_repository.update_session(session)
        
        # Send notification (if service is available)
        if self._notification_service:
            await self._notification_service.send_invoice_created_notification(
                created_invoice
            )
        
        return {
            "success": True,
            "invoice_id": created_invoice.invoice_id,
            "invoice_number": created_invoice.invoice_number,
            "preview_url": created_invoice.preview_url,
            "pdf_url": created_invoice.pdf_url,
            "message": f"Invoice {created_invoice.invoice_number} created successfully!"
        }
    
    async def _update_invoice_fields(
        self, 
        session: ConversationSession, 
        field_updates: dict
    ) -> dict:
        """Update invoice fields in session"""
        # Validate and update fields
        current_data = session.invoice_data.model_dump()
        current_data.update(field_updates)
        
        # Validate updated data
        updated_invoice_data = InvoiceData(**current_data)
        session.invoice_data = updated_invoice_data
        session.update_timestamp()
        
        await self._session_repository.update_session(session)
        
        return {
            "success": True,
            "message": "Invoice fields updated successfully",
            "updated_fields": list(field_updates.keys()),
            "invoice_status": session.get_invoice_status()
        }


class SessionManagementUseCase:
    """
    Use case for session management operations
    Single Responsibility: Handle session lifecycle
    """
    
    def __init__(self, session_repository: ISessionRepository):
        self._session_repository = session_repository
    
    async def get_session_info(self, session_id: str) -> dict:
        """Get session information"""
        session = await self._session_repository.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        return {
            "session_id": session.session_id,
            "status": session.status,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "invoice_status": session.get_invoice_status(),
            "missing_fields": session.invoice_data.get_missing_fields(),
            "metadata": session.metadata.model_dump()
        }
    
    async def reset_session(self, session_id: str) -> dict:
        """Reset session data while keeping metadata"""
        session = await self._session_repository.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Reset invoice data but keep metadata
        session.invoice_data = InvoiceData()
        session.status = ConversationStatus.ACTIVE
        session.update_timestamp()
        
        await self._session_repository.update_session(session)
        
        return {
            "success": True,
            "message": "Session reset successfully",
            "session_id": session.session_id
        }
