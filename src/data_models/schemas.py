from pydantic import BaseModel, EmailStr
from typing import Optional, Any

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