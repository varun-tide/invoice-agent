"""
API Tests - Integration testing
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from server.server import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health and basic endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "🤖 Invoice Agent API"
        assert "version" in data
        assert "endpoints" in data
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert "timestamp" in data
        assert "agent_available" in data


class TestConversationAPI:
    """Test conversation endpoints"""
    
    def test_conversation_endpoint(self):
        """Test basic conversation"""
        response = client.post(
            "/api/v1/conversation",
            json={
                "user_input": "I need an invoice for $500",
                "user_id": "test_user"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "session_id" in data
        assert "invoice_status" in data
        assert data["invoice_status"] == "collecting"
    
    def test_conversation_with_session_id(self):
        """Test conversation with existing session"""
        # First create a session
        response1 = client.post(
            "/api/v1/conversation",
            json={
                "user_input": "I need an invoice for John Doe",
                "user_id": "test_user"
            }
        )
        session_id = response1.json()["session_id"]
        
        # Continue conversation
        response2 = client.post(
            "/api/v1/conversation",
            json={
                "user_input": "Email is john@example.com",
                "session_id": session_id
            }
        )
        assert response2.status_code == 200
        data = response2.json()
        assert data["session_id"] == session_id
    
    def test_complete_invoice_flow(self):
        """Test complete invoice creation flow"""
        # Create invoice with all details
        response = client.post(
            "/api/v1/conversation",
            json={
                "user_input": "Create invoice for John Doe at john@example.com for $500 web development due 2025-02-15",
                "user_id": "test_user"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        session_id = data["session_id"]
        
        # Invoice should be ready if all fields provided
        if data["invoice_status"] == "ready":
            assert data["invoice_data"] is not None
            
            # Approve the invoice
            approve_response = client.post(
                "/api/v1/invoice/approve",
                json={
                    "session_id": session_id,
                    "action": "approve"
                }
            )
            
            assert approve_response.status_code == 200
            approve_data = approve_response.json()
            assert approve_data["success"] is True
            assert "invoice_id" in approve_data
            assert "invoice_number" in approve_data


class TestSessionAPI:
    """Test session management endpoints"""
    
    def test_get_session_info(self):
        """Test getting session information"""
        # Create a session first
        response = client.post(
            "/api/v1/conversation",
            json={
                "user_input": "I need an invoice",
                "user_id": "test_user"
            }
        )
        session_id = response.json()["session_id"]
        
        # Get session info
        info_response = client.get(f"/api/v1/session/{session_id}")
        assert info_response.status_code == 200
        data = info_response.json()
        assert data["session_id"] == session_id
        assert "status" in data
        assert "missing_fields" in data
    
    def test_reset_session(self):
        """Test session reset"""
        # Create and populate a session
        response = client.post(
            "/api/v1/conversation",
            json={
                "user_input": "Invoice for John Doe",
                "user_id": "test_user"
            }
        )
        session_id = response.json()["session_id"]
        
        # Reset session
        reset_response = client.post(f"/api/v1/session/{session_id}/reset")
        assert reset_response.status_code == 200
        data = reset_response.json()
        assert data["success"] is True
        assert data["session_id"] == session_id
    
    def test_nonexistent_session(self):
        """Test accessing non-existent session"""
        fake_session_id = "fake-session-id"
        
        response = client.get(f"/api/v1/session/{fake_session_id}")
        assert response.status_code == 404


class TestErrorHandling:
    """Test error handling"""
    
    def test_invalid_conversation_request(self):
        """Test invalid conversation request"""
        response = client.post(
            "/api/v1/conversation",
            json={"user_input": ""}  # Empty input
        )
        assert response.status_code == 422  # Validation error
    
    def test_invalid_approval_request(self):
        """Test invalid approval request"""
        response = client.post(
            "/api/v1/invoice/approve",
            json={
                "session_id": "fake-session",
                "action": "approve"
            }
        )
        assert response.status_code == 400  # Session not found


class TestDebugEndpoints:
    """Test debug endpoints (only available in debug mode)"""
    
    def test_debug_sessions(self):
        """Test debug sessions endpoint"""
        response = client.get("/debug/sessions")
        assert response.status_code == 200
        data = response.json()
        assert "total_sessions" in data
        assert "sessions" in data
    
    def test_debug_invoices(self):
        """Test debug invoices endpoint"""
        response = client.get("/debug/invoices")
        assert response.status_code == 200
        data = response.json()
        assert "total_invoices" in data
        assert "invoices" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
