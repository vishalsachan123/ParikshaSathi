from fastapi import APIRouter
from src.data_models.schemas import ChatRequest
from src.generations.utils import getQuizResponse

router = APIRouter()
router = APIRouter(prefix="/gen", tags=["Generations"])

@router.get("/evaluateAnswers")
async def get_evaluateAnswers(user_id: int, subject: str, n:int):
    try:                     
        return await getQuizResponse(user_id, subject, n)
    except Exception as e:
        return {"error": str(e)}


# ✅ Chat endpoint
@router.post("/api/chat")
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


