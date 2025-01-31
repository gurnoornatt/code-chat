from datetime import datetime, timedelta, UTC
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv
from backend.db.supabase_client import get_supabase

# Load environment variables
load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY not found in environment variables")

# OAuth2 scheme for token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_student(token: str = Depends(oauth2_scheme)) -> str:
    """Get current authenticated student from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        student_id: str = payload.get("sub")
        role: str = payload.get("role")
        if student_id is None or role is None:
            raise credentials_exception
        if role != "student":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Verify student exists in database
    supabase = get_supabase()
    result = supabase.table("students").select("id").eq("id", student_id).execute()
    
    if not result.data:
        raise credentials_exception
        
    return student_id

async def get_current_admin(token: str = Depends(oauth2_scheme)) -> str:
    """Get current authenticated admin from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        admin_id: str = payload.get("sub")
        role: str = payload.get("role")
        if admin_id is None or role is None:
            raise credentials_exception
        if role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perform this action"
            )
    except JWTError:
        raise credentials_exception
        
    return admin_id

def verify_admin(user_data: dict) -> bool:
    """Verify if user has admin role"""
    return user_data.get("role") == "admin" 