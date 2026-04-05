import json
from pathlib import Path
from typing import Any

from src.data_models.response_format import QuizEvaluation
from  src.services.azure_clients import getResponseModelClient
from  src.prompts.system_messages import SYSTEM_MESSAGE
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
json_file_path_org = BASE_DIR / "sample_data" / "questions.json"

async def format_prompt(user_input:Any):
    try: 
        messages=[
                {
                    "role": "system",
                    "content": SYSTEM_MESSAGE,
                },
                {
                    "role": "user",
                    "content": str(user_input),
                }
            ]

        return messages
    except Exception as e:
        pass


async def simulate_paper_submission(subject:str):

    try:
        json_file_path = "D:\Git_Repos\ParikshaSathi\src\sample_data\questions.json"
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
