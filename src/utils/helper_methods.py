from  src.prompts.system_messages import SYSTEM_MESSAGE
import json
from pathlib import Path
from typing import Any
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