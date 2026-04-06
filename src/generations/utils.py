import json
from pathlib import Path
from typing import Any
import hashlib

from src.data_models.response_format import QuizEvaluation
from src.data_models.schemas import ChatRequest, QuizSubmissionRequest

from  src.services.azure_clients import getResponseModelClient
from  src.prompts.system_messages import SYSTEM_MESSAGE_TEMPLATE
from pathlib import Path
from src.services.azure_clients import getResponseModelClient

BASE_DIR = Path(__file__).resolve().parent.parent
json_file_path_org = BASE_DIR / "sample_data" / "questions.json"
import json

async def format_prompt(req: QuizSubmissionRequest):
    try:

        subject_str = ", ".join(req.subject)
        # ✅ Format system message dynamically
        system_message = SYSTEM_MESSAGE_TEMPLATE.format(
            exam=req.exam,
            subject=subject_str
        )

        # ✅ Filter ONLY wrong questions
        wrong_questions = [
            {
                "questionNumber": q.questionNumber,
                "questionText": q.questionText,
                "options": q.options,
                "correctAnswer": q.correctAnswer,
                "userResponse": q.userResponse,
            }
            for q in req.results
            if q.userResponse != None and  q.userResponse != q.correctAnswer
        ]

        # ✅ Create messages
        messages = [
            {
                "role": "system",
                "content": system_message,
            },
            {
                "role": "user",
                "content": json.dumps({
                    "wrong_questions": wrong_questions
                })
            }
        ]

        return messages

    except Exception as e:
        return []
    


async def simulate_paper_submission(subject:str):

    try:
        json_file_path = json_file_path_org
        # 1. Load the JSON file
        file_path = Path(json_file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Assuming your structure has "questions" key containing physics, chemistry, math
        all_questions = data.get("questions", {}).get(subject, '')

        for question in all_questions:
            if "explanation" in question:
                del question["explanation"]
            if "extra" in question:
                del question["extra"]
            if "subject" in question:
                del question["subject"]
        return all_questions
        
    except Exception as e:
        raise


async def getQuizResponse(req : QuizSubmissionRequest):
    try:
        llm_client = await getResponseModelClient()
        # user_input = await simulate_paper_submission(subject='math')
        messages = await format_prompt(req)

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


            return {
                "status": "success",
                "data": clean_data,
                "token_usage": usage,
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
    



def build_system_prompt(ctx, exam, subjects):
    subjects_str = ", ".join(subjects)

    return f"""
You are an expert {subjects_str} tutor for {exam} level.

Q: {ctx.question}
Options: {", ".join(ctx.options)}
Student: {ctx.userSelectedOption}
Correct: {ctx.correctOption}

Generate response in Markdown Format.
Explain briefly (2–3 lines).
If wrong, point mistake clearly.
Use steps only if needed (math/physics, keep minimal).
Max 8–10 lines.

Suggest 2 short follow-up questions.
"""




async def get_questionwise_interaction_response(req: ChatRequest, ctx, user_id):

    ctx = req.question_context

    system_prompt = build_system_prompt(
        ctx,
        exam=req.question_context.examType,
        subjects=req.question_context.subjects
    )

    llm = await getResponseModelClient()

    messages = [
        {"role": "system", "content": system_prompt}
    ] + [msg.model_dump() for msg in req.history] + [
        {"role": "user", "content": req.user_query}
    ]

    res = await llm.ainvoke(messages)
    return res.content

    


    
