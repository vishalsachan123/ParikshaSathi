from fastapi import FastAPI
# from src.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware


from scalar_fastapi import get_scalar_api_reference
from src.log_here.logger import logger
from src.data_models.response_format import QuizEvaluation
# logger.disabled = True
from  src.services.azure_clients import getResponseModelClient
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import List, Optional


from src.data_models.schemas import ChatRequest
from src.generations.routes import router as generations_router
from src.account.routes import router as account_router


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


PUBLIC_PATHS = {"/", "/docs", "/redoc", "/openapi.json", "/health", "/login", "/register"}


@app.middleware("http")
async def authenticate_middleware(request: Request, call_next):
    if request.url.path in PUBLIC_PATHS:
        return await call_next(request)

    # auth_header = request.headers.get("Authorization")
    # if not auth_header or not auth_header.startswith("Bearer "):
    #     raise HTTPException(status_code=401, detail="Not authenticated")

    # token = auth_header.split(" ")[1]
    # # Add your token validation logic here...

    response = await call_next(request)
    return response


@app.get("/")
async def get_root():
    return {"message": "Health is ok : ParikshaSathi"}



@app.get("/scalar")
async def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API"
    )


