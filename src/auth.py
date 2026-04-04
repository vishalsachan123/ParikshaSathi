import jwt
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from passlib.context import CryptContext
from .database import get_db, Base, engine
from .models import UserDB
from .schemas import UserSignup, UserLogin, APIResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration (Move these to .env later!)
SECRET_KEY = "your_super_secret_key_change_me" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 hours

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- SIGNUP ROUTE ---
@router.post("/signup", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def signup(user: UserSignup, db: Session = Depends(get_db)):
    try:
        Base.metadata.create_all(bind=engine)
        
        db_user = db.query(UserDB).filter(UserDB.email == user.email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_pass = pwd_context.hash(user.password[:72])
        new_user = UserDB(username=user.username, email=user.email, password=hashed_pass)
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {
            "status": "success",
            "message": "User registered successfully",
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

# --- SIGNIN ROUTE ---
@router.post("/signin", response_model=APIResponse)
def signin(credentials: UserLogin, db: Session = Depends(get_db)):
    try:
        # 1. Find User
        user = db.query(UserDB).filter(UserDB.email == credentials.email).first()
        
        # 2. Verify existence and password
        if not user or not pwd_context.verify(credentials.password[:72], user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid email or password"
            )
        
        # 3. Generate Token
        token = create_access_token(data={"sub": user.email, "user_id": user.id})
        
        # 4. Return response with token
        return {
            "status": "success",
            "token": token,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An internal server error occurred")