from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime, UTC
from backend.db.supabase_client import get_supabase
from backend.auth.utils import get_current_student, get_current_admin

router = APIRouter(prefix="/resources", tags=["resources"])

class Resource(BaseModel):
    id: str
    title: str
    description: str
    content: str
    file_type: str
    tags: List[str]
    created_at: datetime
    updated_at: datetime

class ResourceCreate(BaseModel):
    title: str
    description: str
    content: str
    file_type: str
    tags: List[str]

@router.post("/", response_model=Resource)
async def create_resource(
    resource: ResourceCreate,
    admin_id: str = Depends(get_current_admin)
):
    """Create a new learning resource (admin only)"""
    supabase = get_supabase()
    
    now = datetime.now(UTC).isoformat()
    resource_data = {
        **resource.dict(),
        "created_at": now,
        "updated_at": now
    }
    
    result = supabase.table("resources").insert(resource_data).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create resource"
        )
    
    return Resource(**result.data[0])

@router.get("/", response_model=List[Resource])
async def list_resources(
    student_id: str = Depends(get_current_student)
):
    """List all resources"""
    supabase = get_supabase()
    
    result = supabase.table("resources")\
        .select("*")\
        .order("created_at", desc=True)\
        .execute()
    
    return [Resource(**r) for r in result.data] if result.data else []

@router.get("/{resource_id}", response_model=Resource)
async def get_resource(
    resource_id: str,
    student_id: str = Depends(get_current_student)
):
    """Get a specific resource"""
    supabase = get_supabase()
    
    result = supabase.table("resources")\
        .select("*")\
        .eq("id", resource_id)\
        .execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    return Resource(**result.data[0])

@router.put("/{resource_id}", response_model=Resource)
async def update_resource(
    resource_id: str,
    resource: ResourceCreate,
    admin_id: str = Depends(get_current_admin)
):
    """Update a specific resource (admin only)"""
    supabase = get_supabase()
    
    # Check if resource exists
    result = supabase.table("resources")\
        .select("*")\
        .eq("id", resource_id)\
        .execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    # Update resource
    resource_data = {
        **resource.dict(),
        "updated_at": datetime.now(UTC).isoformat()
    }
    
    result = supabase.table("resources")\
        .update(resource_data)\
        .eq("id", resource_id)\
        .execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update resource"
        )
    
    return Resource(**result.data[0])

@router.get("/search", response_model=List[Resource])
async def search_resources(
    tag: str,
    student_id: str = Depends(get_current_student)
):
    """Search resources by tag"""
    supabase = get_supabase()
    
    result = supabase.table("resources")\
        .select("*")\
        .execute()
    
    # Filter by tag (since Supabase doesn't support array contains in free tier)
    resources = [
        Resource(**r) for r in result.data
        if tag in r.get("tags", [])
    ] if result.data else []
    
    return resources

@router.delete("/{resource_id}")
async def delete_resource(
    resource_id: str,
    admin_id: str = Depends(get_current_admin)
):
    """Delete a specific resource (admin only)"""
    supabase = get_supabase()
    
    # Check if resource exists
    result = supabase.table("resources")\
        .select("*")\
        .eq("id", resource_id)\
        .execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    # Delete resource
    result = supabase.table("resources")\
        .delete()\
        .eq("id", resource_id)\
        .execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete resource"
        )
    
    return {"message": "Resource deleted successfully"} 