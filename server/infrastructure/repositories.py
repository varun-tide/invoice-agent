"""
Infrastructure - Repository Implementations
Following Clean Architecture: Infrastructure layer implementations
"""

import uuid
from datetime import datetime
from typing import Optional, Dict

from ..application.interfaces import ISessionRepository, IInvoiceRepository
from ..domain.entities import (
    ConversationSession, 
    InvoiceData, 
    CreatedInvoice,
    SessionMetadata
)


class InMemorySessionRepository(ISessionRepository):
    """
    In-memory session repository for development/testing
    Single Responsibility: Handle session storage operations
    
    Note: In production, replace with Redis/Database implementation
    """
    
    def __init__(self):
        self._sessions: Dict[str, ConversationSession] = {}
    
    async def create_session(self, user_id: Optional[str] = None) -> ConversationSession:
        """Create a new conversation session"""
        session_id = str(uuid.uuid4())
        session = ConversationSession(
            session_id=session_id,
            user_id=user_id,
            invoice_data=InvoiceData(),
            metadata=SessionMetadata()
        )
        
        self._sessions[session_id] = session
        return session
    
    async def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Get session by ID"""
        return self._sessions.get(session_id)
    
    async def update_session(self, session: ConversationSession) -> None:
        """Update session data"""
        session.update_timestamp()
        self._sessions[session.session_id] = session
    
    async def delete_session(self, session_id: str) -> None:
        """Delete session"""
        if session_id in self._sessions:
            del self._sessions[session_id]
    
    def get_all_sessions(self) -> Dict[str, ConversationSession]:
        """Get all sessions (for debugging)"""
        return self._sessions.copy()


class InMemoryInvoiceRepository(IInvoiceRepository):
    """
    In-memory invoice repository for development/testing
    Single Responsibility: Handle invoice storage operations
    
    Note: In production, replace with database implementation
    """
    
    def __init__(self):
        self._invoices: Dict[str, CreatedInvoice] = {}
        self._invoice_counter = 1000  # Starting invoice number
    
    async def create_invoice(
        self, 
        invoice_data: InvoiceData, 
        user_id: Optional[str] = None
    ) -> CreatedInvoice:
        """Create invoice and return created invoice details"""
        invoice_id = str(uuid.uuid4())
        invoice_number = f"INV-{self._invoice_counter:06d}"
        self._invoice_counter += 1
        
        created_invoice = CreatedInvoice(
            invoice_id=invoice_id,
            invoice_number=invoice_number,
            customer_name=invoice_data.customer_name or "",
            customer_email=invoice_data.customer_email or "",
            description=invoice_data.invoice_description or "",
            amount=invoice_data.total_amount or 0.0,
            due_date=invoice_data.due_date or "",
            status="pending",
            created_at=datetime.now(),
            preview_url=f"https://yourapp.com/invoice/{invoice_id}/preview",
            pdf_url=f"https://yourapp.com/invoice/{invoice_id}/pdf"
        )
        
        self._invoices[invoice_id] = created_invoice
        return created_invoice
    
    async def get_invoice(self, invoice_id: str) -> Optional[CreatedInvoice]:
        """Get invoice by ID"""
        return self._invoices.get(invoice_id)
    
    def get_all_invoices(self) -> Dict[str, CreatedInvoice]:
        """Get all invoices (for debugging)"""
        return self._invoices.copy()


class MockNotificationService:
    """Mock notification service for development"""
    
    async def send_invoice_created_notification(self, invoice: CreatedInvoice) -> bool:
        """Mock notification - just log the event"""
        print(f"📧 Notification: Invoice {invoice.invoice_number} created for {invoice.customer_email}")
        return True
