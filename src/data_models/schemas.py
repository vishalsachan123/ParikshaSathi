from pydantic import BaseModel, EmailStr
from typing import Optional, Any, List

class UserSignup(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    class Config:
        from_attributes = True

# The structured response for the frontend
class APIResponse(BaseModel):
    status: str
    message: str
    data: Optional[Any] = None
    token: Optional[str] = None # Added for login


# ✅ Request schema
class ChatRequest(BaseModel):
    question: str
    options: List[str]
    correct: str
    user_answer: Optional[str]
    query: str




class QuestionSubmission(BaseModel):
    questionNumber: int
    questionText: str
    options: List[str]
    correctAnswer: int
    userResponse: Optional[int] = None
    explanation: Optional[str] = None


class QuizSubmissionRequest(BaseModel):
    results: List[QuestionSubmission]
    exam: str
    subject: List[str]   # ✅ change to list