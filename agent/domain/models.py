"""
Domain Models - Core business entities
Following Clean Architecture: Domain layer (innermost)
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator
import re


class InvoiceData(BaseModel):
    """Core invoice data entity with validation"""
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
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v
    
    @field_validator('total_amount')
    @classmethod
    def validate_amount(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return v
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        return v
    
    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Due date must be in YYYY-MM-DD format')
    
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
    
    def is_complete(self) -> bool:
        """Check if all required fields are present"""
        return len(self.get_missing_fields()) == 0


class ResponseMetadata(BaseModel):
    """Metadata for individual API responses"""
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    cost_usd: float = 0.0
    response_time_ms: int = 0


class SessionMetadata(BaseModel):
    """Cumulative session metadata"""
    total_api_calls: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cached_tokens: int = 0
    total_cost_usd: float = 0.0
    total_response_time_ms: int = 0
    session_start_time: datetime = None
    last_call_time: Optional[datetime] = None
    
    class Config:
        arbitrary_types_allowed = True
