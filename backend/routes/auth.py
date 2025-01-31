from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta, UTC
from backend.db.supabase_client import get_supabase
from backend.auth.utils import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

class StudentCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    grade_level: str
    school: str

class StudentLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=Token)
async def register(student: StudentCreate):
    """Register a new student"""
    supabase = get_supabase()
    
    # Check if email already exists
    result = supabase.table("students")\
        .select("*")\
        .eq("email", student.email)\
        .execute()
    
    if result.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new student
    student_data = {
        **student.dict(),
        "created_at": datetime.now(UTC).isoformat()
    }
    
    result = supabase.table("students").insert(student_data).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create student"
        )
    
    # Create access token
    student_id = result.data[0]["id"]
    access_token = create_access_token(
        data={"sub": student_id, "role": "student"},
        expires_delta=timedelta(minutes=30)
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(student: StudentLogin):
    """Login with email and password"""
    supabase = get_supabase()
    
    # Find student by email
    result = supabase.table("students")\
        .select("*")\
        .eq("email", student.email)\
        .execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    student_data = result.data[0]
    
    # Verify password
    if student_data["password"] != student.password:  # In production, use proper password hashing
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": student_data["id"], "role": "student"},
        expires_delta=timedelta(minutes=30)
    )
    
    return {"access_token": access_token, "token_type": "bearer"} 