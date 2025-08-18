"""
Domain Entities - Core business models
Following Clean Architecture: Domain layer (innermost)
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class InvoiceStatus(str, Enum):
    """Invoice processing status"""
    COLLECTING = "collecting"
    READY = "ready" 
    CREATED = "created"


class ConversationStatus(str, Enum):
    """Conversation session status"""
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"


class InvoiceData(BaseModel):
    """Core invoice data entity"""
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    invoice_description: Optional[str] = None
    total_amount: Optional[float] = None
    due_date: Optional[str] = None
    
    @field_validator('customer_email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Basic email validation - will be enhanced by email-validator
        if '@' not in v or '.' not in v.split('@')[1]:
            raise ValueError('Invalid email format')
        return v.lower().strip()
    
    @field_validator('total_amount')
    @classmethod
    def validate_amount(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return v
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        return round(v, 2)  # Round to 2 decimal places
    
    def is_complete(self) -> bool:
        """Check if all required fields are present"""
        return all([
            self.customer_name,
            self.customer_email,
            self.invoice_description,
            self.total_amount,
            self.due_date
        ])
    
    def get_missing_fields(self) -> list[str]:
        """Get list of missing required fields"""
        missing = []
        if not self.customer_name:
            missing.append("customer_name")
        if not self.customer_email:
            missing.append("customer_email")
        if not self.invoice_description:
            missing.append("invoice_description")
        if not self.total_amount:
            missing.append("total_amount")
        if not self.due_date:
            missing.append("due_date")
        return missing


class SessionMetadata(BaseModel):
    """Session metadata for tracking API usage"""
    total_api_calls: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cached_tokens: int = 0
    total_cost_usd: float = 0.0
    total_response_time_ms: int = 0
    session_start_time: datetime = Field(default_factory=datetime.now)
    last_call_time: Optional[datetime] = None


class ConversationSession(BaseModel):
    """Conversation session entity"""
    session_id: str
    user_id: Optional[str] = None
    invoice_data: InvoiceData = Field(default_factory=InvoiceData)
    metadata: SessionMetadata = Field(default_factory=SessionMetadata)
    status: ConversationStatus = ConversationStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def update_timestamp(self) -> None:
        """Update the last updated timestamp"""
        self.updated_at = datetime.now()
    
    def get_invoice_status(self) -> InvoiceStatus:
        """Determine current invoice status"""
        if self.invoice_data.is_complete():
            return InvoiceStatus.READY
        return InvoiceStatus.COLLECTING


class CreatedInvoice(BaseModel):
    """Represents a successfully created invoice"""
    invoice_id: str
    invoice_number: str
    customer_name: str
    customer_email: str
    description: str
    amount: float
    due_date: str
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.now)
    preview_url: Optional[str] = None
    pdf_url: Optional[str] = None
