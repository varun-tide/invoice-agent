#!/usr/bin/env python3
"""
Development server startup script
Easy way to run the server locally
"""

import uvicorn
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

if __name__ == "__main__":
    print("🚀 Starting Invoice Agent API Server...")
    print("📋 Available endpoints:")
    print("   - API Documentation: http://localhost:8000/docs")
    print("   - Health Check: http://localhost:8000/api/v1/health")
    print("   - Root: http://localhost:8000/")
    print("   - Debug Sessions: http://localhost:8000/debug/sessions")
    print("   - Debug Invoices: http://localhost:8000/debug/invoices")
    print()
    
    uvicorn.run(
        "server.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
