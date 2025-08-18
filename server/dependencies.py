"""
Dependency Injection Container
Following Clean Architecture: Dependency Inversion Principle
"""

from functools import lru_cache

from .application.interfaces import (
    IInvoiceAgentService,
    ISessionRepository,
    IInvoiceRepository,
    INotificationService
)
from .application.use_cases import (
    ConversationUseCase,
    InvoiceCreationUseCase,
    SessionManagementUseCase
)
from .infrastructure import (
    InvoiceAgentService,
    InMemorySessionRepository,
    InMemoryInvoiceRepository,
    MockNotificationService
)


class Container:
    """
    Dependency Injection Container
    Single Responsibility: Manage object creation and dependencies
    """
    
    def __init__(self):
        self._session_repository: ISessionRepository = None
        self._invoice_repository: IInvoiceRepository = None
        self._agent_service: IInvoiceAgentService = None
        self._notification_service: INotificationService = None
    
    @property
    def session_repository(self) -> ISessionRepository:
        """Get session repository instance (Singleton)"""
        if self._session_repository is None:
            self._session_repository = InMemorySessionRepository()
        return self._session_repository
    
    @property
    def invoice_repository(self) -> IInvoiceRepository:
        """Get invoice repository instance (Singleton)"""
        if self._invoice_repository is None:
            self._invoice_repository = InMemoryInvoiceRepository()
        return self._invoice_repository
    
    @property
    def agent_service(self) -> IInvoiceAgentService:
        """Get agent service instance (Singleton)"""
        if self._agent_service is None:
            self._agent_service = InvoiceAgentService()
        return self._agent_service
    
    @property
    def notification_service(self) -> INotificationService:
        """Get notification service instance (Singleton)"""
        if self._notification_service is None:
            self._notification_service = MockNotificationService()
        return self._notification_service
    
    def get_conversation_use_case(self) -> ConversationUseCase:
        """Create conversation use case with dependencies"""
        return ConversationUseCase(
            agent_service=self.agent_service,
            session_repository=self.session_repository
        )
    
    def get_invoice_creation_use_case(self) -> InvoiceCreationUseCase:
        """Create invoice creation use case with dependencies"""
        return InvoiceCreationUseCase(
            session_repository=self.session_repository,
            invoice_repository=self.invoice_repository,
            notification_service=self.notification_service
        )
    
    def get_session_management_use_case(self) -> SessionManagementUseCase:
        """Create session management use case with dependencies"""
        return SessionManagementUseCase(
            session_repository=self.session_repository
        )


# Global container instance
@lru_cache()
def get_container() -> Container:
    """Get the global dependency container (Singleton)"""
    return Container()


# FastAPI dependency functions
def get_conversation_use_case() -> ConversationUseCase:
    """FastAPI dependency for conversation use case"""
    container = get_container()
    return container.get_conversation_use_case()


def get_invoice_creation_use_case() -> InvoiceCreationUseCase:
    """FastAPI dependency for invoice creation use case"""
    container = get_container()
    return container.get_invoice_creation_use_case()


def get_session_management_use_case() -> SessionManagementUseCase:
    """FastAPI dependency for session management use case"""
    container = get_container()
    return container.get_session_management_use_case()
