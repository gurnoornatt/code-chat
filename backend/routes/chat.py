from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime, UTC
from backend.db.supabase_client import get_supabase
from backend.auth.utils import get_current_student

router = APIRouter(prefix="/chat", tags=["chat"])

class QuestionCreate(BaseModel):
    question_text: str
    code_context: Optional[str] = None

class Question(BaseModel):
    id: str
    student_id: str
    question_text: str
    code_context: Optional[str]
    created_at: datetime
    resolved: bool

class AIResponse(BaseModel):
    id: str
    question_id: str
    response_text: str
    is_hint: bool
    created_at: datetime

class Conversation(BaseModel):
    id: str
    student_id: str
    question_id: str
    message_type: str
    message_text: str
    created_at: datetime

class FeedbackCreate(BaseModel):
    response_id: str
    rating: int
    comment: Optional[str] = None

@router.post("/questions", response_model=Question)
async def create_question(
    question: QuestionCreate,
    student_id: str = Depends(get_current_student)
):
    """Create a new question"""
    supabase = get_supabase()
    
    question_data = {
        "student_id": student_id,
        "question_text": question.question_text,
        "code_context": question.code_context,
        "resolved": False,
        "created_at": datetime.now(UTC).isoformat()
    }
    
    result = supabase.table("questions").insert(question_data).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create question"
        )
    
    question_id = result.data[0]["id"]
    
    # Create initial conversation message
    conversation_data = {
        "student_id": student_id,
        "question_id": question_id,
        "message_type": "student",
        "message_text": question.question_text,
        "created_at": datetime.now(UTC).isoformat()
    }
    
    result = supabase.table("conversations").insert(conversation_data).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )
    
    return Question(**result.data[0])

@router.get("/questions", response_model=List[Question])
async def get_questions(
    student_id: str = Depends(get_current_student)
):
    """Get all questions for the current student"""
    supabase = get_supabase()
    
    result = supabase.table("questions")\
        .select("*")\
        .eq("student_id", student_id)\
        .order("created_at", desc=True)\
        .execute()
    
    return [Question(**q) for q in result.data] if result.data else []

@router.get("/conversations/{question_id}", response_model=List[Conversation])
async def get_conversation(
    question_id: str,
    student_id: str = Depends(get_current_student)
):
    """Get conversation history for a specific question"""
    supabase = get_supabase()
    
    # Verify question belongs to student
    question_result = supabase.table("questions")\
        .select("*")\
        .eq("id", question_id)\
        .eq("student_id", student_id)\
        .execute()
    
    if not question_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    result = supabase.table("conversations")\
        .select("*")\
        .eq("question_id", question_id)\
        .order("created_at")\
        .execute()
    
    return [Conversation(**msg) for msg in result.data] if result.data else []

@router.post("/responses/{question_id}/feedback")
async def submit_feedback(
    question_id: str,
    feedback: FeedbackCreate,
    student_id: str = Depends(get_current_student)
):
    """Submit feedback for an AI response"""
    if not 1 <= feedback.rating <= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5"
        )
    
    supabase = get_supabase()
    
    # Verify question belongs to student
    question_result = supabase.table("questions")\
        .select("*")\
        .eq("id", question_id)\
        .eq("student_id", student_id)\
        .execute()
    
    if not question_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Verify response exists and belongs to the question
    response_result = supabase.table("conversations")\
        .select("*")\
        .eq("id", feedback.response_id)\
        .eq("question_id", question_id)\
        .eq("message_type", "ai")\
        .execute()
    
    if not response_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Response not found"
        )
    
    feedback_data = {
        **feedback.dict(),
        "student_id": student_id,
        "created_at": datetime.now(UTC).isoformat()
    }
    
    result = supabase.table("feedback").insert(feedback_data).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit feedback"
        )
    
    return {"message": "Feedback submitted successfully"} 