from pydantic import BaseModel, EmailStr
from typing import Optional, Any, List, Literal

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




class QuestionContextPayload(BaseModel):
    question: str
    options: List[str]
    userSelectedOption: str
    correctOption: str
    examType: str
    subjects: List[str]
    questionNo: int

class Message(BaseModel):
    role: Literal["assistant", "user"]
    content: str

class ChatRequest(BaseModel):
    question_context: QuestionContextPayload
    user_query: str
    history: List[Message]




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