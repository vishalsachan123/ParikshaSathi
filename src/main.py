from fastapi import FastAPI
from src.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware


from scalar_fastapi import get_scalar_api_reference
from src.utils.logger import logger
from src.data_models.response_format import QuizEvaluation
# logger.disabled = True
from  src.services.azure_clients import getResponseModelClient
from src.utils.helper_methods import format_prompt, simulate_paper_submission
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import List, Optional


from src.data_models.schemas import ChatRequest



app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)



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

@app.get("/evaluateAnswers")
async def get_evaluateAnswers(user_id: int, subject: str, n:int):
    try:                     
        return await getQuizResponse(user_id, subject, n)
    except Exception as e:
        return {"error": str(e)}





# ✅ Chat endpoint
@app.post("/api/chat")
async def chat(req: ChatRequest):

    q = req.query.lower()

    # 🔹 simple logic (string response only)
    if "explain" in q:
        return f"Explanation: The correct answer is '{req.correct}' for this question."

    elif "answer" in q:
        return f"Correct answer is: {req.correct}"

    elif "my answer" in q:
        if req.user_answer:
            return f"You selected: {req.user_answer}"
        return "You have not selected any answer."

    elif "correct or not" in q:
        if req.user_answer == req.correct:
            return "Yes ✅ Your answer is correct!"
        else:
            return f"No ❌ Correct answer is {req.correct}"

    else:
        return "Ask something like: explain, answer, or check my answer2."

async def getQuizResponse(user_id: int, subject: str, n: int):
    try:
        llm_client = await getResponseModelClient()
        user_input = await simulate_paper_submission(subject=subject)
        messages = await format_prompt(user_input=user_input[:n])

        structured_llm = llm_client.with_structured_output(
            QuizEvaluation,
            method="json_schema",
            strict=False,          # ✅ keep (since defaults exist)
            include_raw=True       # ✅ needed for token usage
        )

        try:
            result = await structured_llm.ainvoke(messages)

            # ✅ Extract
            parsed = result.get("parsed")
            raw = result.get("raw")

            if parsed is None:
                raise ValueError("Parsing failed")

            # ✅ Token usage (Azure-safe)
            usage = raw.response_metadata.get("token_usage") or \
                    raw.response_metadata.get("usage", {})

            # ✅ Clean serialization (prevents warnings)
            clean_data = QuizEvaluation(**parsed.model_dump()).model_dump()

            # ✅ Optional debug (SAFE)
            debug_info = {
                "model": raw.response_metadata.get("model_name"),
                "finish_reason": raw.response_metadata.get("finish_reason"),
                "has_parsed": parsed is not None
            }

            return {
                "status": "success",
                "data": clean_data,
                "token_usage": usage,
                "debug": debug_info,   # ✅ safe debug (optional)
                "error": None,
                "from": 1
            }

        except Exception as e:
            # 🔁 Fallback (JSON mode)
            raw_response = await llm_client.ainvoke(messages)

            import json
            try:
                parsed_json = json.loads(raw_response.content)

                validated = QuizEvaluation.model_validate(parsed_json)

                usage = raw_response.response_metadata.get("token_usage") or \
                        raw_response.response_metadata.get("usage", {})

                return {
                    "status": "fallback_success",
                    "data": validated.model_dump(),
                    "token_usage": usage,
                    "error": str(e),
                    "from": 2
                }

            except Exception as inner_error:
                return {
                    "status": "failed",
                    "data": None,
                    "token_usage": None,
                    "error": f"{str(e)} | {str(inner_error)}",
                    "from": 3
                }

    except Exception as e:
        return {
            "status": "failed",
            "data": None,
            "token_usage": None,
            "error": str(e),
            "from": 4
        }




