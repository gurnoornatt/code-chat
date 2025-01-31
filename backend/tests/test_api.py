import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.auth.utils import create_access_token
import uuid

# Test data
test_user = {
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User"
}

test_admin = {
    "email": "admin@example.com",
    "password": "adminpassword123",
    "full_name": "Admin User",
    "role": "admin"
}

# Create test UUIDs
TEST_USER_ID = str(uuid.uuid4())
TEST_ADMIN_ID = str(uuid.uuid4())

@pytest.fixture
def user_token():
    """Create a test user token"""
    return create_access_token({"sub": TEST_USER_ID, "role": "student"})

@pytest.fixture
def admin_token():
    """Create a test admin token"""
    return create_access_token({"sub": TEST_ADMIN_ID, "role": "admin"})

def test_health_check(test_client):
    """Test health check endpoint"""
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "message": "API is running"}

def test_register_user(test_client):
    """Test user registration"""
    student = {
        "email": "test@example.com",
        "password": "testpass123",
        "name": "Test Student",
        "grade_level": "12",
        "school": "Test High School"
    }
    response = test_client.post("/auth/register", json=student)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login(test_client, test_student):
    """Test user login"""
    credentials = {
        "email": test_student["email"],
        "password": "testpass123"
    }
    response = test_client.post("/auth/token", json=credentials)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_chat_functionality(test_client, student_token):
    """Test chat functionality"""
    headers = {"Authorization": f"Bearer {student_token}"}
    
    # Test creating a question
    question = {
        "question_text": "How do I use a for loop in Python?",
        "code_context": "# I want to iterate over a list\nmy_list = [1, 2, 3]"
    }
    response = test_client.post("/chat/questions", json=question, headers=headers)
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["question_text"] == question["question_text"]
    question_id = response.json()["id"]
    
    # Test getting questions
    response = test_client.get("/chat/questions", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    
    # Test getting conversation history
    response = test_client.get(f"/chat/conversations/{question_id}", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    # Test submitting feedback
    feedback = {
        "response_id": str(uuid.uuid4()),
        "rating": 5,
        "comment": "Very helpful explanation!"
    }
    response = test_client.post(f"/chat/responses/{question_id}/feedback", json=feedback, headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Feedback submitted successfully"

def test_file_management(test_client, student_token):
    """Test file management functionality"""
    headers = {"Authorization": f"Bearer {student_token}"}
    
    # Test file upload
    test_content = b"print('Hello, World!')"
    files = {
        "file": ("test_script.py", test_content, "text/plain")
    }
    response = test_client.post("/files/upload", files=files, headers=headers)
    assert response.status_code == 200
    assert "id" in response.json()
    file_id = response.json()["id"]
    
    # Test listing files
    response = test_client.get("/files/list", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    
    # Test getting file content
    response = test_client.get(f"/files/{file_id}/content", headers=headers)
    assert response.status_code == 200
    assert "content" in response.json()
    assert "metadata" in response.json()
    
    # Test file deletion
    response = test_client.delete(f"/files/{file_id}", headers=headers)
    assert response.status_code == 200
    
    # Verify file is deleted
    response = test_client.get(f"/files/{file_id}/content", headers=headers)
    assert response.status_code == 404

def test_resource_management(test_client, admin_token, student_token):
    """Test resource management functionality"""
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    user_headers = {"Authorization": f"Bearer {student_token}"}
    
    # Test creating resource (admin only)
    resource = {
        "title": "Python Basics",
        "description": "Learn Python fundamentals",
        "content": "# Python Basics\n\nThis guide covers...",
        "file_type": "markdown",
        "tags": ["python", "beginner"]
    }
    response = test_client.post("/resources", json=resource, headers=admin_headers)
    assert response.status_code == 200
    assert "id" in response.json()
    resource_id = response.json()["id"]
    
    # Test listing resources
    response = test_client.get("/resources", headers=user_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    
    # Test getting specific resource
    response = test_client.get(f"/resources/{resource_id}", headers=user_headers)
    assert response.status_code == 200
    assert response.json()["title"] == resource["title"]
    
    # Test updating resource (admin only)
    updated_resource = {**resource, "title": "Updated Python Basics"}
    response = test_client.put(
        f"/resources/{resource_id}",
        json=updated_resource,
        headers=admin_headers
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Python Basics"
    
    # Test searching resources by tag
    response = test_client.get("/resources/search", params={"tag": "python"}, headers=user_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    
    # Test deleting resource (admin only)
    response = test_client.delete(f"/resources/{resource_id}", headers=admin_headers)
    assert response.status_code == 200
    
    # Verify resource is deleted
    response = test_client.get(f"/resources/{resource_id}", headers=user_headers)
    assert response.status_code == 404

def test_resource_endpoints(test_client, admin_token, user_token):
    """Test resource endpoints"""
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    user_headers = {"Authorization": f"Bearer {user_token}"}
    
    # Test creating resource (admin only)
    resource = {
        "title": "Test Resource",
        "description": "Test Description",
        "content": "Test Content",
        "file_type": "text",
        "tags": ["test", "example"]
    }
    
    response = test_client.post("/resources", json=resource, headers=admin_headers)
    assert response.status_code == 200
    resource_id = response.json()["id"]
    
    # Test listing resources
    response = test_client.get("/resources", headers=user_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    # Test getting specific resource
    response = test_client.get(f"/resources/{resource_id}", headers=user_headers)
    assert response.status_code == 200
    assert response.json()["title"] == resource["title"]
    
    # Test updating resource (admin only)
    updated_resource = {**resource, "title": "Updated Title"}
    response = test_client.put(
        f"/resources/{resource_id}",
        json=updated_resource,
        headers=admin_headers
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"
    
    # Test deleting resource (admin only)
    response = test_client.delete(f"/resources/{resource_id}", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Resource deleted successfully"

def test_unauthorized_access(test_client, user_token):
    """Test unauthorized access to admin endpoints"""
    headers = {"Authorization": f"Bearer {user_token}"}
    
    resource = {
        "title": "Test Resource",
        "description": "Test Description",
        "content": "Test Content",
        "file_type": "text",
        "tags": ["test", "example"]
    }
    
    # Try to create resource as non-admin
    response = test_client.post("/resources", json=resource, headers=headers)
    assert response.status_code == 403

def test_file_context_in_chat(test_client, user_token):
    """Test handling of file context in chat"""
    headers = {"Authorization": f"Bearer {user_token}"}
    
    # Upload a file first
    test_file_content = "def test_function():\n    return 42"
    files = {
        "file": ("test.py", test_file_content.encode(), "text/plain")
    }
    response = test_client.post("/files/upload", files=files, headers=headers)
    assert response.status_code == 200
    file_id = response.json()["id"]
    
    # Send message with file reference
    message = {
        "content": "Explain this code",
        "file_reference": file_id
    }
    response = test_client.post("/chat/send", json=message, headers=headers)
    assert response.status_code == 200
    assert response.json()["file_reference"] == file_id
    
    # Verify AI response includes file context
    message_id = response.json()["id"]
    response = test_client.get(f"/chat/response/{message_id}", headers=headers)
    assert response.status_code == 200
    assert "test_function" in response.json()["content"].lower()

def test_chat_error_handling(test_client, user_token):
    """Test error handling in chat endpoints"""
    headers = {"Authorization": f"Bearer {user_token}"}
    
    # Test empty message
    response = test_client.post("/chat/send", json={"content": ""}, headers=headers)
    assert response.status_code == 400
    
    # Test invalid file reference
    response = test_client.post(
        "/chat/send",
        json={"content": "test", "file_reference": "invalid_id"},
        headers=headers
    )
    assert response.status_code == 404
    
    # Test invalid message ID for response
    response = test_client.get("/chat/response/invalid_id", headers=headers)
    assert response.status_code == 404
    
    # Test invalid feedback
    response = test_client.post(
        "/chat/feedback",
        json={"message_id": "invalid_id", "is_helpful": True},
        headers=headers
    )
    assert response.status_code == 404

def test_file_error_handling(test_client, user_token):
    """Test error handling in file management"""
    headers = {"Authorization": f"Bearer {user_token}"}
    
    # Test upload without file
    response = test_client.post("/files/upload", headers=headers)
    assert response.status_code == 400
    
    # Test upload with empty file
    files = {
        "file": ("empty.txt", b"", "text/plain")
    }
    response = test_client.post("/files/upload", files=files, headers=headers)
    assert response.status_code == 400
    
    # Test access to non-existent file
    response = test_client.get("/files/nonexistent", headers=headers)
    assert response.status_code == 404
    
    # Test delete non-existent file
    response = test_client.delete("/files/nonexistent", headers=headers)
    assert response.status_code == 404
    
    # Test upload with invalid content type
    files = {
        "file": ("test.exe", b"invalid", "application/x-executable")
    }
    response = test_client.post("/files/upload", files=files, headers=headers)
    assert response.status_code == 400

def test_file_permissions(test_client, user_token, admin_token):
    """Test file access permissions"""
    user_headers = {"Authorization": f"Bearer {user_token}"}
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Upload file as user
    files = {
        "file": ("user_file.txt", b"user content", "text/plain")
    }
    response = test_client.post("/files/upload", files=files, headers=user_headers)
    assert response.status_code == 200
    file_id = response.json()["id"]
    
    # Test that admin can access user's file
    response = test_client.get(f"/files/{file_id}", headers=admin_headers)
    assert response.status_code == 200
    
    # Test that admin can list all files
    response = test_client.get("/files", headers=admin_headers)
    assert response.status_code == 200
    assert len(response.json()) > 0
    
    # Test that user can only access their own files
    response = test_client.get("/files", headers=user_headers)
    assert response.status_code == 200
    files_list = response.json()
    assert all(f["student_id"] == user_token["sub"] for f in files_list)

def test_resource_error_handling(test_client, admin_token, user_token):
    """Test error handling in resource management"""
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    user_headers = {"Authorization": f"Bearer {user_token}"}
    
    # Test creation with missing required fields
    resource = {
        "title": "Incomplete Resource"
    }
    response = test_client.post("/resources", json=resource, headers=admin_headers)
    assert response.status_code == 422
    
    # Test creation with invalid file type
    resource = {
        "title": "Invalid Resource",
        "description": "Test",
        "content": "Content",
        "file_type": "invalid_type",
        "tags": []
    }
    response = test_client.post("/resources", json=resource, headers=admin_headers)
    assert response.status_code == 400
    
    # Test access to non-existent resource
    response = test_client.get("/resources/nonexistent", headers=admin_headers)
    assert response.status_code == 404
    
    # Test unauthorized resource creation (non-admin)
    resource = {
        "title": "Unauthorized Resource",
        "description": "Test",
        "content": "Content",
        "file_type": "text",
        "tags": []
    }
    response = test_client.post("/resources", json=resource, headers=user_headers)
    assert response.status_code == 403
    
    # Test unauthorized resource update (non-admin)
    response = test_client.put("/resources/test-id", json=resource, headers=user_headers)
    assert response.status_code == 403
    
    # Test unauthorized resource deletion (non-admin)
    response = test_client.delete("/resources/test-id", headers=user_headers)
    assert response.status_code == 403

def test_resource_access_control(test_client, admin_token, user_token):
    """Test resource access control and permissions"""
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    user_headers = {"Authorization": f"Bearer {user_token}"}
    
    # Create a resource as admin
    resource = {
        "title": "Test Resource",
        "description": "Test Description",
        "content": "Test Content",
        "file_type": "text",
        "tags": ["test"]
    }
    response = test_client.post("/resources", json=resource, headers=admin_headers)
    assert response.status_code == 200
    resource_id = response.json()["id"]
    
    # Test that regular users can read resources
    response = test_client.get(f"/resources/{resource_id}", headers=user_headers)
    assert response.status_code == 200
    
    # Test that regular users can list resources
    response = test_client.get("/resources", headers=user_headers)
    assert response.status_code == 200
    
    # Test that regular users can search resources
    response = test_client.get("/resources/search", params={"tag": "test"}, headers=user_headers)
    assert response.status_code == 200
    
    # Clean up
    response = test_client.delete(f"/resources/{resource_id}", headers=admin_headers)
    assert response.status_code == 200 