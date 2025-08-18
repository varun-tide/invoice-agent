"""
API Models - Request/Response schemas
Following Clean Architecture: Interface adapters layer
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ConversationRequest(BaseModel):
    """Request model for conversation endpoint"""
    user_input: str = Field(..., description="User's message input", min_length=1)
    session_id: Optional[str] = Field(None, description="Existing session ID")
    user_id: Optional[str] = Field(None, description="User identifier")


class ConversationResponse(BaseModel):
    """Response model for conversation endpoint"""
    success: bool = Field(..., description="Operation success status")
    action: str = Field(..., description="Action type (collecting_information, ready_for_approval, etc.)")
    message: str = Field(..., description="Human-readable message")
    session_id: str = Field(..., description="Session identifier")
    invoice_status: str = Field(..., description="Current invoice status (incomplete, complete, editing)")
    missing_fields: Optional[list[str]] = Field(None, description="List of missing required fields")
    current_data: Optional[Dict[str, Any]] = Field(None, description="Current invoice data")
    invoice_data: Optional[Dict[str, Any]] = Field(None, description="Complete invoice data when ready")
    preview: Optional[Dict[str, Any]] = Field(None, description="Invoice preview data")
    extracted_data: Optional[Dict[str, Any]] = Field(None, description="Data extracted from current input")
    session_metadata: Dict[str, Any] = Field(..., description="Session metadata including tokens and cost")
    
    # For invoice creation responses
    invoice: Optional[Dict[str, Any]] = Field(None, description="Created invoice details")
    error: Optional[str] = Field(None, description="Error message if any")


class InvoiceApprovalRequest(BaseModel):
    """Request model for invoice approval"""
    session_id: str = Field(..., description="Session identifier")
    action: str = Field("approve", description="Action to perform")
    field_updates: Optional[Dict[str, Any]] = Field(None, description="Field updates for edit action")


class InvoiceApprovalResponse(BaseModel):
    """Response model for invoice approval"""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    invoice_id: Optional[str] = Field(None, description="Created invoice ID")
    invoice_number: Optional[str] = Field(None, description="Invoice number")
    preview_url: Optional[str] = Field(None, description="Invoice preview URL")
    pdf_url: Optional[str] = Field(None, description="Invoice PDF URL")


class SessionInfoResponse(BaseModel):
    """Response model for session information"""
    session_id: str = Field(..., description="Session identifier")
    status: str = Field(..., description="Session status")
    created_at: str = Field(..., description="Session creation time")
    updated_at: str = Field(..., description="Last update time")
    invoice_status: str = Field(..., description="Invoice completion status")
    missing_fields: list[str] = Field(..., description="Missing required fields")
    metadata: Dict[str, Any] = Field(..., description="Session metadata")


class SessionResetResponse(BaseModel):
    """Response model for session reset"""
    success: bool = Field(..., description="Operation success status") 
    message: str = Field(..., description="Response message")
    session_id: str = Field(..., description="Session identifier")


class HealthCheckResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Check timestamp")
    version: str = Field(..., description="API version")
    agent_available: bool = Field(..., description="Invoice agent availability")


class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
