from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List, Dict
from pydantic import BaseModel
from datetime import datetime, UTC
from backend.db.supabase_client import get_supabase
from backend.auth.utils import get_current_student
import json

router = APIRouter(prefix="/files", tags=["files"])

class FileMetadata(BaseModel):
    id: str
    name: str
    content_type: str
    size: int
    student_id: str
    created_at: datetime

class FileContent(BaseModel):
    content: str
    metadata: FileMetadata

class FileResponse(BaseModel):
    id: str
    name: str
    content_type: str
    size: int
    student_id: str
    storage_path: str
    created_at: datetime

@router.post("/upload", response_model=FileResponse)
async def upload_file(
    file: UploadFile = File(...),
    student_id: str = Depends(get_current_student)
):
    """Upload a file to storage"""
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    supabase = get_supabase()
    
    # Read file content
    content = await file.read()
    
    # Generate storage path
    storage_path = f"files/{student_id}/{file.filename}"
    
    # Upload to storage
    try:
        result = supabase.storage.from_("files").upload(
            storage_path,
            content
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )
    
    # Store file metadata in database
    file_data = {
        "name": file.filename,
        "content_type": file.content_type,
        "size": len(content),
        "student_id": student_id,
        "storage_path": storage_path,
        "created_at": datetime.now(UTC).isoformat()
    }
    
    result = supabase.table("files").insert(file_data).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store file metadata"
        )
    
    return FileResponse(**result.data[0])

@router.get("/list", response_model=List[FileResponse])
async def list_files(
    student_id: str = Depends(get_current_student)
):
    """List all files for the current student"""
    supabase = get_supabase()
    
    result = supabase.table("files")\
        .select("*")\
        .eq("student_id", student_id)\
        .order("created_at", desc=True)\
        .execute()
    
    return [FileResponse(**file) for file in result.data] if result.data else []

@router.get("/{file_id}/content", response_model=FileContent)
async def get_file_content(
    file_id: str,
    student_id: str = Depends(get_current_student)
):
    """Get file content and metadata"""
    supabase = get_supabase()
    
    # Get file metadata
    result = supabase.table("files")\
        .select("*")\
        .eq("id", file_id)\
        .eq("student_id", student_id)\
        .execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    file_metadata = result.data[0]
    
    # Get file content from storage
    storage_response = supabase.storage.from_("files")\
        .download(file_metadata["storage_path"])
    
    if not storage_response:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve file content"
        )
    
    return FileContent(
        content=storage_response.decode(),
        metadata=FileMetadata(**file_metadata)
    )

@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    student_id: str = Depends(get_current_student)
):
    """Delete a file"""
    supabase = get_supabase()
    
    # Get file metadata
    result = supabase.table("files")\
        .select("*")\
        .eq("id", file_id)\
        .eq("student_id", student_id)\
        .execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    file_data = result.data[0]
    
    # Delete from storage
    try:
        supabase.storage.from_("files").remove([file_data["storage_path"]])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file from storage: {str(e)}"
        )
    
    # Delete metadata from database
    result = supabase.table("files")\
        .delete()\
        .eq("id", file_id)\
        .eq("student_id", student_id)\
        .execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file metadata"
        )
    
    return {"message": "File deleted successfully"} 