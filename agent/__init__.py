"""
Invoice Agent Package
A conversational AI agent for creating invoices using natural language processing.

Refactored with Clean Architecture following SOLID principles:
- Domain: Core business models
- Services: Business logic services  
- Core: Application orchestration
- Agent: Main interface (backward compatible)
"""

# Main agent interface (backward compatible)
from .agent import InvoiceAgent

# Domain models
from .domain.models import InvoiceData, ResponseMetadata, SessionMetadata

# Services (available for advanced usage)
from .services import DateParserService, DescriptionFormatterService, MetadataService

# Core components (available for advanced usage)
from .core import LLMClient, InvoiceProcessor

__version__ = "2.0.0"
__author__ = "Your Team"

# Backward compatibility - main interface
__all__ = [
    "InvoiceAgent",
    "InvoiceData", 
    "ResponseMetadata",
    "SessionMetadata",
    # Advanced components
    "DateParserService",
    "DescriptionFormatterService", 
    "MetadataService",
    "LLMClient",
    "InvoiceProcessor"
]
