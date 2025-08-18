"""
Application Interfaces - Dependency Inversion Principle
Following Clean Architecture: Application layer interfaces
"""

from abc import ABC, abstractmethod
from typing import Optional
from ..domain.entities import ConversationSession, CreatedInvoice, InvoiceData


class IInvoiceAgentService(ABC):
    """Interface for Invoice Agent service (Dependency Inversion)"""
    
    @abstractmethod
    async def process_user_input(
        self, 
        user_input: str, 
        session: ConversationSession
    ) -> str:
        """Process user input and return agent response"""
        pass
    
    @abstractmethod
    async def process_user_input_api(
        self, 
        user_input: str, 
        session: ConversationSession
    ) -> dict:
        """Process user input and return structured response for API"""
        pass
    
    @abstractmethod
    async def get_session_metadata(self, session: ConversationSession) -> dict:
        """Get formatted session metadata"""
        pass


class ISessionRepository(ABC):
    """Interface for session storage (Dependency Inversion)"""
    
    @abstractmethod
    async def create_session(self, user_id: Optional[str] = None) -> ConversationSession:
        """Create a new conversation session"""
        pass
    
    @abstractmethod
    async def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Get session by ID"""
        pass
    
    @abstractmethod
    async def update_session(self, session: ConversationSession) -> None:
        """Update session data"""
        pass
    
    @abstractmethod
    async def delete_session(self, session_id: str) -> None:
        """Delete session"""
        pass


class IInvoiceRepository(ABC):
    """Interface for invoice persistence (Dependency Inversion)"""
    
    @abstractmethod
    async def create_invoice(
        self, 
        invoice_data: InvoiceData, 
        user_id: Optional[str] = None
    ) -> CreatedInvoice:
        """Create invoice and return created invoice details"""
        pass
    
    @abstractmethod
    async def get_invoice(self, invoice_id: str) -> Optional[CreatedInvoice]:
        """Get invoice by ID"""
        pass


class INotificationService(ABC):
    """Interface for notifications (future extensibility)"""
    
    @abstractmethod
    async def send_invoice_created_notification(
        self, 
        invoice: CreatedInvoice
    ) -> bool:
        """Send notification when invoice is created"""
        pass
