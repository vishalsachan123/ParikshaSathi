from fastapi import APIRouter, Request
from src.data_models.schemas import ChatRequest, QuizSubmissionRequest
from src.generations.utils import getQuizResponse, get_questionwise_interaction_response
from fastapi import Request


router = APIRouter()
router = APIRouter(prefix="/gen", tags=["Generations"])

@router.post("/evaluateAnswers")
async def evaluate_answers(req: QuizSubmissionRequest, request: Request):
    try:
        user_details = request.state.user
        return await getQuizResponse(req)
    except Exception as e:
        return {"error": str(e)}


# ✅ Chat endpoint
@router.post("/api/chat")
async def chat(req: ChatRequest, request: Request):
    try:
        user = request.state.user
        user_id = user["user_id"]
        ctx = req.question_context
        
        response = await get_questionwise_interaction_response(req, ctx, user_id)
        return {"answer" : response}
    except Exception as e:
        return {"answer": "..."}



