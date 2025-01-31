from supabase import create_client, Client
from dotenv import load_dotenv
import os
from typing import Optional
from fastapi import HTTPException

# Load environment variables
load_dotenv()

# Get Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials not found in environment variables")

_supabase_client: Optional[Client] = None

def get_supabase() -> Client:
    """
    Returns the Supabase client instance.
    Use this as a dependency in FastAPI routes.
    """
    global _supabase_client
    if _supabase_client is None:
        try:
            # Initialize Supabase client
            _supabase_client = create_client(
                SUPABASE_URL,
                SUPABASE_KEY,
            )
            
            # Test the connection by making a simple query
            try:
                _supabase_client.table('students').select('id').limit(1).execute()
            except Exception as e:
                print(f"Database table access error: {e}")
                raise HTTPException(
                    status_code=500,
                    detail="Database tables not properly configured"
                )
                
        except Exception as e:
            print(f"Error initializing Supabase client: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize database connection"
            )
    return _supabase_client 