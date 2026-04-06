from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import jwt
import os
from scalar_fastapi import get_scalar_api_reference
from src.log_here.logger import logger
from src.data_models.response_format import QuizEvaluation
# logger.disabled = True
from  src.services.azure_clients import getResponseModelClient
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

from src.data_models.schemas import ChatRequest
from src.generations.routes import router as generations_router
from src.account.routes import router as account_router
load_dotenv()

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(account_router)
app.include_router(generations_router)


PUBLIC_PATHS = {"/", "/docs", "/auth/signin", "/auth/signup"}


# JWT Configuration (Move these to .env later!)
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 hours


def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # You can extract user info here
        user_id = payload.get("user_id")
        email = payload.get("sub")

        if user_id is None:
            return False, None
        return True, payload  # ✅ return decoded data

    except Exception as e:
        detail="Token is invalid or expired"
        return False, None




@app.middleware("http")
async def authenticate_middleware(request: Request, call_next):
    try:
        # ✅ Allow preflight requests
        if request.method == "OPTIONS":
            return await call_next(request)

        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Not authenticated")

        token = auth_header.split(" ")[1]

        status, payload = verify_access_token(token)

        # ✅ Optional: attach user to request
        if not status:
            return {"status" : "Authentication Problem"}
        
        request.state.user = payload

        response = await call_next(request)
        return response

    except Exception as e:
        return {"status" : "Authentication Problem"}
    



@app.get("/")
async def get_root():
    return {"message": "Health is ok : ParikshaSathi"}



@app.get("/scalar")
async def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API"
    )


