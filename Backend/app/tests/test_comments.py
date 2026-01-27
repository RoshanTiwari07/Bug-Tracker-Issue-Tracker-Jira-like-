"""Tests for Comment endpoints"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test data
test_user = {
    "username": "commentuser",
    "email": "commentuser@example.com",
    "password": "Password123!"
}

test_project = {
    "name": "Comment Project",
    "description": "Project for comment tests",
    "key": "COMM"
}

test_ticket = {
    "title": "Test ticket for comments",
    "description": "Ticket to test comments",
    "priority": "medium",
    "issue_type": "bug"
}

test_comment = {
    "content": "This is a test comment"
}

test_comment_update = {
    "content": "Updated comment content"
}


class TestCommentManagement:
    """Test comment CRUD operations"""

    @pytest.fixture
    def setup(self):
        """Setup user, project, ticket, and auth"""
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
        
        # Create ticket
        ticket_response = client.post(
            "/api/v1/tickets",
            json={
                **test_ticket,
                "project_id": project_id
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        ticket_id = ticket_response.json()["id"]
        
        return {"token": token, "ticket_id": ticket_id}

    def test_add_comment(self, setup):
        """Test adding a comment to a ticket"""
        response = client.post(
            f"/api/v1/tickets/{setup['ticket_id']}/comments",
            json=test_comment,
            headers={"Authorization": f"Bearer {setup['token']}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == test_comment["content"]
        assert "id" in data
        assert "author_id" in data

    def test_get_comments(self, setup):
        """Test getting all comments on a ticket"""
        # Add a comment
        client.post(
            f"/api/v1/tickets/{setup['ticket_id']}/comments",
            json=test_comment,
            headers={"Authorization": f"Bearer {setup['token']}"}
        )
        
        # Get comments
        response = client.get(
            f"/api/v1/tickets/{setup['ticket_id']}/comments",
            headers={"Authorization": f"Bearer {setup['token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert data[0]["content"] == test_comment["content"]

    def test_update_comment(self, setup):
        """Test updating a comment"""
        # Add a comment
        add_response = client.post(
            f"/api/v1/tickets/{setup['ticket_id']}/comments",
            json=test_comment,
            headers={"Authorization": f"Bearer {setup['token']}"}
        )
        comment_id = add_response.json()["id"]
        
        # Update the comment
        response = client.patch(
            f"/api/v1/comments/{comment_id}",
            json=test_comment_update,
            headers={"Authorization": f"Bearer {setup['token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == test_comment_update["content"]

    def test_delete_comment(self, setup):
        """Test deleting a comment"""
        # Add a comment
        add_response = client.post(
            f"/api/v1/tickets/{setup['ticket_id']}/comments",
            json=test_comment,
            headers={"Authorization": f"Bearer {setup['token']}"}
        )
        comment_id = add_response.json()["id"]
        
        # Delete the comment
        response = client.delete(
            f"/api/v1/comments/{comment_id}",
            headers={"Authorization": f"Bearer {setup['token']}"}
        )
        assert response.status_code == 204

    def test_comment_without_auth(self, setup):
        """Test adding comment without authentication"""
        response = client.post(
            f"/api/v1/tickets/{setup['ticket_id']}/comments",
            json=test_comment
        )
        assert response.status_code == 403

    def test_comment_on_nonexistent_ticket(self, setup):
        """Test commenting on nonexistent ticket"""
        response = client.post(
            "/api/v1/tickets/99999/comments",
            json=test_comment,
            headers={"Authorization": f"Bearer {setup['token']}"}
        )
        assert response.status_code == 404


class TestCommentReplies:
    """Test nested comment replies"""

    @pytest.fixture
    def setup_with_comment(self):
        """Setup and create initial comment"""
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
        
        # Create ticket
        ticket_response = client.post(
            "/api/v1/tickets",
            json={
                **test_ticket,
                "project_id": project_id
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        ticket_id = ticket_response.json()["id"]
        
        # Create comment
        comment_response = client.post(
            f"/api/v1/tickets/{ticket_id}/comments",
            json=test_comment,
            headers={"Authorization": f"Bearer {token}"}
        )
        comment_id = comment_response.json()["id"]
        
        return {"token": token, "comment_id": comment_id}

    def test_reply_to_comment(self, setup_with_comment):
        """Test replying to a comment"""
        reply_data = {"content": "This is a reply"}
        response = client.post(
            f"/api/v1/comments/{setup_with_comment['comment_id']}/reply",
            json=reply_data,
            headers={"Authorization": f"Bearer {setup_with_comment['token']}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == reply_data["content"]
        assert data["parent_id"] == setup_with_comment["comment_id"]
