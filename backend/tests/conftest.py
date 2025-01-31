import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.auth.utils import create_access_token
import os
from unittest.mock import MagicMock
from backend.db.supabase_client import get_supabase
from datetime import datetime, timedelta, UTC
from typing import Dict, Any, List
import uuid

# Ensure we're using test environment variables
os.environ["TESTING"] = "1"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_KEY"] = "test-key"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"

class MockSupabaseQuery:
    def __init__(self, data: List[Dict[str, Any]], table: 'MockSupabaseTable'):
        self.data = data
        self.table = table
        self.conditions = []
        self.order_conditions = []
    
    def eq(self, field: str, value: Any):
        self.conditions.append(("eq", field, value))
        return self
    
    def order(self, field: str, desc: bool = False):
        self.order_conditions.append((field, desc))
        return self
    
    def execute(self):
        filtered_data = self.data.copy()
        for op, field, value in self.conditions:
            if op == "eq":
                filtered_data = [item for item in filtered_data if item.get(field) == value]
        
        if self.order_conditions:
            for field, desc in reversed(self.order_conditions):
                filtered_data.sort(
                    key=lambda x: x.get(field, ""),
                    reverse=desc
                )
        
        return MagicMock(data=filtered_data)

class MockSupabaseTable:
    def __init__(self, initial_data: List[Dict[str, Any]]):
        self.data = initial_data.copy()
    
    def select(self, *args):
        return MockSupabaseQuery(self.data, self)
    
    def insert(self, value: Dict[str, Any]):
        new_id = str(uuid.uuid4())
        new_record = {**value, "id": new_id}
        self.data.append(new_record)
        return MockSupabaseQuery([new_record], self)
    
    def update(self, value: Dict[str, Any]):
        return MockSupabaseQuery(self.data, self)
    
    def delete(self):
        return MockSupabaseQuery([], self)

class MockStorage:
    def from_(self, bucket: str):
        return self
    
    def upload(self, path: str, data: bytes):
        return {"Key": path}
    
    def download(self, path: str):
        return b"test content"
    
    def remove(self, paths: List[str]):
        return True

@pytest.fixture(autouse=True)
def mock_supabase(monkeypatch):
    """Mock Supabase client for all tests"""
    mock_client = MagicMock()
    
    # Create mock tables with initial data
    test_student_id = str(uuid.uuid4())
    test_question_id = str(uuid.uuid4())
    test_conversation_id = str(uuid.uuid4())
    
    tables = {
        "students": MockSupabaseTable([
            {
                "id": test_student_id,
                "email": "test@example.com",
                "password": "testpass123",
                "name": "Test Student",
                "grade_level": "12",
                "school": "Test High School",
                "created_at": datetime.now(UTC).isoformat()
            }
        ]),
        "questions": MockSupabaseTable([
            {
                "id": test_question_id,
                "student_id": test_student_id,
                "question_text": "How do I use a for loop?",
                "code_context": "# Example code",
                "resolved": False,
                "created_at": datetime.now(UTC).isoformat()
            }
        ]),
        "conversations": MockSupabaseTable([
            {
                "id": test_conversation_id,
                "student_id": test_student_id,
                "question_id": test_question_id,
                "message_type": "student",
                "message_text": "How do I use a for loop?",
                "created_at": datetime.now(UTC).isoformat()
            }
        ]),
        "files": MockSupabaseTable([]),
        "resources": MockSupabaseTable([]),
        "feedback": MockSupabaseTable([])
    }
    
    def get_table(name: str):
        return tables.get(name, MockSupabaseTable([]))
    
    mock_client.table = get_table
    mock_client.storage = MockStorage()
    
    def mock_get_supabase():
        return mock_client
    
    monkeypatch.setattr("backend.db.supabase_client.get_supabase", mock_get_supabase)
    return mock_client

@pytest.fixture
def test_client():
    """Test client with the FastAPI app"""
    return TestClient(app)

@pytest.fixture
def test_student():
    """Test student data"""
    return {
        "email": "test@example.com",
        "password": "testpass123",
        "name": "Test Student",
        "grade_level": "12",
        "school": "Test High School",
        "created_at": datetime.now(UTC).isoformat()
    }

@pytest.fixture
def student_token(test_student):
    """Create a valid student token"""
    # First create the student in the database
    supabase = get_supabase()
    result = supabase.table("students").insert(test_student).execute()
    student_id = result.data[0]["id"]
    
    # Create access token
    access_token = create_access_token(
        data={"sub": student_id, "role": "student"},
        expires_delta=timedelta(minutes=30)
    )
    
    return access_token

@pytest.fixture
def admin_token():
    """Create a valid admin token"""
    admin_id = str(uuid.uuid4())
    access_token = create_access_token(
        data={"sub": admin_id, "role": "admin"},
        expires_delta=timedelta(minutes=30)
    )
    return access_token 