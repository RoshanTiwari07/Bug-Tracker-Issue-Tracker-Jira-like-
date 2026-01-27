"""Tests for Attachment endpoints"""
import pytest
from io import BytesIO
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test data
test_user = {
    "username": "attachmentuser",
    "email": "attachmentuser@example.com",
    "password": "Password123!"
}

test_project = {
    "name": "Attachment Project",
    "description": "Project for attachment tests",
    "key": "ATTACH"
}

test_ticket = {
    "title": "Ticket with attachments",
    "description": "Testing file attachments",
    "priority": "medium",
    "issue_type": "bug"
}


class TestAttachmentManagement:
    """Test attachment CRUD operations"""

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

    def test_upload_attachment(self, setup):
        """Test uploading a file attachment"""
        # Create a test file
        file_content = b"Test file content"
        files = {
            "file": ("test.txt", BytesIO(file_content), "text/plain")
        }
        
        response = client.post(
            f"/api/v1/attachments/tickets/{setup['ticket_id']}/upload",
            files=files,
            headers={"Authorization": f"Bearer {setup['token']}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["filename"] == "test.txt"
        assert "id" in data
        assert "upload_time" in data

    def test_get_ticket_attachments(self, setup):
        """Test getting all attachments on a ticket"""
        # Upload a file
        file_content = b"Test file content"
        files = {
            "file": ("test.txt", BytesIO(file_content), "text/plain")
        }
        client.post(
            f"/api/v1/attachments/tickets/{setup['ticket_id']}/upload",
            files=files,
            headers={"Authorization": f"Bearer {setup['token']}"}
        )
        
        # Get attachments
        response = client.get(
            f"/api/v1/attachments/tickets/{setup['ticket_id']}/attachments",
            headers={"Authorization": f"Bearer {setup['token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert data[0]["filename"] == "test.txt"

    def test_download_attachment(self, setup):
        """Test downloading an attachment"""
        # Upload a file
        file_content = b"Test file content"
        files = {
            "file": ("test.txt", BytesIO(file_content), "text/plain")
        }
        upload_response = client.post(
            f"/api/v1/attachments/tickets/{setup['ticket_id']}/upload",
            files=files,
            headers={"Authorization": f"Bearer {setup['token']}"}
        )
        attachment_id = upload_response.json()["id"]
        
        # Download the file
        response = client.get(
            f"/api/v1/attachments/{attachment_id}/download",
            headers={"Authorization": f"Bearer {setup['token']}"}
        )
        assert response.status_code == 200
        assert response.content == file_content

    def test_delete_attachment(self, setup):
        """Test deleting an attachment"""
        # Upload a file
        file_content = b"Test file content"
        files = {
            "file": ("test.txt", BytesIO(file_content), "text/plain")
        }
        upload_response = client.post(
            f"/api/v1/attachments/tickets/{setup['ticket_id']}/upload",
            files=files,
            headers={"Authorization": f"Bearer {setup['token']}"}
        )
        attachment_id = upload_response.json()["id"]
        
        # Delete the attachment
        response = client.delete(
            f"/api/v1/attachments/{attachment_id}",
            headers={"Authorization": f"Bearer {setup['token']}"}
        )
        assert response.status_code == 204

    def test_upload_without_auth(self, setup):
        """Test uploading without authentication"""
        file_content = b"Test file content"
        files = {
            "file": ("test.txt", BytesIO(file_content), "text/plain")
        }
        
        response = client.post(
            "/api/v1/attachments/tickets/{}/upload".format(setup['ticket_id']),
            files=files
        )
        assert response.status_code == 403

    def test_upload_to_nonexistent_ticket(self, setup):
        """Test uploading to nonexistent ticket"""
        file_content = b"Test file content"
        files = {
            "file": ("test.txt", BytesIO(file_content), "text/plain")
        }
        
        response = client.post(
            "/api/v1/attachments/tickets/99999/upload",
            files=files,
            headers={"Authorization": f"Bearer {setup['token']}"}
        )
        assert response.status_code == 404

    def test_upload_multiple_files(self, setup):
        """Test uploading multiple files"""
        file1 = ("file1.txt", BytesIO(b"Content 1"), "text/plain")
        file2 = ("file2.txt", BytesIO(b"Content 2"), "text/plain")
        
        # Upload first file
        response1 = client.post(
            f"/api/v1/attachments/tickets/{setup['ticket_id']}/upload",
            files={"file": file1},
            headers={"Authorization": f"Bearer {setup['token']}"}
        )
        assert response1.status_code == 201
        
        # Upload second file
        response2 = client.post(
            f"/api/v1/attachments/tickets/{setup['ticket_id']}/upload",
            files={"file": file2},
            headers={"Authorization": f"Bearer {setup['token']}"}
        )
        assert response2.status_code == 201
        
        # Verify both files exist
        list_response = client.get(
            f"/api/v1/attachments/tickets/{setup['ticket_id']}/attachments",
            headers={"Authorization": f"Bearer {setup['token']}"}
        )
        data = list_response.json()
        assert len(data) == 2
