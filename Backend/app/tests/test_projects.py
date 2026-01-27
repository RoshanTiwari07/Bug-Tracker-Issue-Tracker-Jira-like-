"""Tests for Project endpoints"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test data
test_user = {
    "username": "projectuser",
    "email": "projectuser@example.com",
    "password": "Password123!"
}

test_project = {
    "name": "Test Project",
    "description": "A test project",
    "key": "TP"
}

test_project_update = {
    "name": "Updated Project",
    "description": "Updated description"
}


class TestProjectManagement:
    """Test project CRUD operations"""

    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        client.post("/api/v1/auth/register", json=test_user)
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user["username"],
                "password": test_user["password"]
            }
        )
        return response.json()["access_token"]

    def test_create_project(self, auth_token):
        """Test creating a new project"""
        response = client.post(
            "/api/v1/projects/",
            json=test_project,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == test_project["name"]
        assert data["description"] == test_project["description"]
        assert data["key"] == test_project["key"]
        assert "id" in data

    def test_list_projects(self, auth_token):
        """Test listing projects"""
        # Create a project first
        client.post(
            "/api/v1/projects/",
            json=test_project,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # List projects
        response = client.get(
            "/api/v1/projects",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert any(p["name"] == test_project["name"] for p in data)

    def test_get_project(self, auth_token):
        """Test getting a specific project"""
        # Create a project
        create_response = client.post(
            "/api/v1/projects/",
            json=test_project,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        project_id = create_response.json()["id"]
        
        # Get the project
        response = client.get(
            f"/api/v1/projects/{project_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == test_project["name"]

    def test_update_project(self, auth_token):
        """Test updating a project"""
        # Create a project
        create_response = client.post(
            "/api/v1/projects/",
            json=test_project,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        project_id = create_response.json()["id"]
        
        # Update the project
        response = client.put(
            f"/api/v1/projects/{project_id}",
            json=test_project_update,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == test_project_update["name"]
        assert data["description"] == test_project_update["description"]

    def test_delete_project(self, auth_token):
        """Test deleting a project"""
        # Create a project
        create_response = client.post(
            "/api/v1/projects/",
            json=test_project,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        project_id = create_response.json()["id"]
        
        # Delete the project
        response = client.delete(
            f"/api/v1/projects/{project_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 204

    def test_create_project_without_auth(self):
        """Test creating project without authentication"""
        response = client.post(
            "/api/v1/projects/",
            json=test_project
        )
        assert response.status_code == 403

    def test_get_nonexistent_project(self, auth_token):
        """Test getting nonexistent project"""
        response = client.get(
            "/api/v1/projects/99999",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 404
