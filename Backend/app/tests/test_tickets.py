"""Tests for Ticket endpoints"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test data
test_user = {
    "username": "ticketuser",
    "email": "ticketuser@example.com",
    "password": "Password123!"
}

test_project = {
    "name": "Ticket Project",
    "description": "Project for tickets",
    "key": "TICK"
}

test_ticket = {
    "title": "Fix login bug",
    "description": "Users cannot login with special characters",
    "priority": "high",
    "issue_type": "bug"
}

test_ticket_update = {
    "title": "Updated ticket title",
    "description": "Updated description",
    "priority": "critical"
}


class TestTicketManagement:
    """Test ticket CRUD operations"""

    @pytest.fixture
    def setup(self):
        """Setup user, project, and auth"""
        client.post("/api/v1/auth/register", json=test_user)
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user["username"],
                "password": test_user["password"]
            }
        )
        token = login_response.json()["access_token"]
        
        # Create project
        project_response = client.post(
            "/api/v1/projects/",
            json=test_project,
            headers={"Authorization": f"Bearer {token}"}
        )
        project_id = project_response.json()["id"]
        
        return {"token": token, "project_id": project_id}

    def test_create_ticket(self, setup):
        """Test creating a new ticket"""
        response = client.post(
            "/api/v1/tickets",
            json={
                **test_ticket,
                "project_id": setup["project_id"]
            },
            headers={"Authorization": f"Bearer {setup['token']}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == test_ticket["title"]
        assert data["description"] == test_ticket["description"]
        assert data["priority"] == test_ticket["priority"]
        assert "key" in data  # Auto-generated key

    def test_get_ticket(self, setup):
        """Test getting a specific ticket"""
        # Create a ticket
        create_response = client.post(
            "/api/v1/tickets",
            json={
                **test_ticket,
                "project_id": setup["project_id"]
            },
            headers={"Authorization": f"Bearer {setup['token']}"}
        )
        ticket_id = create_response.json()["id"]
        
        # Get the ticket
        response = client.get(
            f"/api/v1/tickets/{ticket_id}",
            headers={"Authorization": f"Bearer {setup['token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == test_ticket["title"]

    def test_update_ticket(self, setup):
        """Test updating a ticket"""
        # Create a ticket
        create_response = client.post(
            "/api/v1/tickets",
            json={
                **test_ticket,
                "project_id": setup["project_id"]
            },
            headers={"Authorization": f"Bearer {setup['token']}"}
        )
        ticket_id = create_response.json()["id"]
        
        # Update the ticket
        response = client.patch(
            f"/api/v1/tickets/{ticket_id}",
            json=test_ticket_update,
            headers={"Authorization": f"Bearer {setup['token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == test_ticket_update["title"]

    def test_change_ticket_status(self, setup):
        """Test changing ticket status"""
        # Create a ticket
        create_response = client.post(
            "/api/v1/tickets",
            json={
                **test_ticket,
                "project_id": setup["project_id"]
            },
            headers={"Authorization": f"Bearer {setup['token']}"}
        )
        ticket_id = create_response.json()["id"]
        
        # Change status
        response = client.patch(
            f"/api/v1/tickets/{ticket_id}/status",
            json={"status": "in_progress"},
            headers={"Authorization": f"Bearer {setup['token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"

    def test_delete_ticket(self, setup):
        """Test deleting a ticket"""
        # Create a ticket
        create_response = client.post(
            "/api/v1/tickets",
            json={
                **test_ticket,
                "project_id": setup["project_id"]
            },
            headers={"Authorization": f"Bearer {setup['token']}"}
        )
        ticket_id = create_response.json()["id"]
        
        # Delete the ticket
        response = client.delete(
            f"/api/v1/tickets/{ticket_id}",
            headers={"Authorization": f"Bearer {setup['token']}"}
        )
        assert response.status_code == 204


class TestTicketSearch:
    """Test ticket search and filtering"""

    @pytest.fixture
    def setup_with_tickets(self):
        """Setup user, project, and multiple tickets"""
        client.post("/api/v1/auth/register", json=test_user)
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user["username"],
                "password": test_user["password"]
            }
        )
        token = login_response.json()["access_token"]
        
        # Create project
        project_response = client.post(
            "/api/v1/projects/",
            json=test_project,
            headers={"Authorization": f"Bearer {token}"}
        )
        project = project_response.json()
        
        # Create multiple tickets
        client.post(
            "/api/v1/tickets",
            json={
                "title": "Critical bug",
                "description": "System crash",
                "priority": "critical",
                "issue_type": "bug",
                "project_id": project["id"]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        client.post(
            "/api/v1/tickets",
            json={
                "title": "Add new feature",
                "description": "User requested feature",
                "priority": "low",
                "issue_type": "feature",
                "project_id": project["id"]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        return {"token": token, "project_name": project["key"]}

    def test_search_by_keyword(self, setup_with_tickets):
        """Test searching tickets by keyword"""
        response = client.get(
            f"/api/v1/tickets/{setup_with_tickets['project_name']}/search",
            params={"keyword": "bug"},
            headers={"Authorization": f"Bearer {setup_with_tickets['token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0

    def test_search_by_priority(self, setup_with_tickets):
        """Test filtering by priority"""
        response = client.get(
            f"/api/v1/tickets/{setup_with_tickets['project_name']}/search",
            params={"priority": "critical"},
            headers={"Authorization": f"Bearer {setup_with_tickets['token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0

    def test_search_by_status(self, setup_with_tickets):
        """Test filtering by status"""
        response = client.get(
            f"/api/v1/tickets/{setup_with_tickets['project_name']}/search",
            params={"status": "todo"},
            headers={"Authorization": f"Bearer {setup_with_tickets['token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0

    def test_search_with_pagination(self, setup_with_tickets):
        """Test pagination"""
        response = client.get(
            f"/api/v1/tickets/{setup_with_tickets['project_name']}/search",
            params={"skip": 0, "limit": 1},
            headers={"Authorization": f"Bearer {setup_with_tickets['token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 1
