from typing import List
from pydantic import BaseModel, Field


class QuestionFeedback(BaseModel):
    questionNumber: int
    
    # ✅ Persuasive + corrective feedback
    feedback: str = Field(
        ..., 
        description="Short persuasive and corrective feedback (max 1-2 lines)"
    )
    
    # ✅ Steps to solve
    steps: List[str] = Field(
        ..., 
        description="Concise step-by-step solution (upto 5 to 6 lines)"
    )


class FinalSummary(BaseModel):
    weaknesses: List[str] = Field(
        ..., 
        description="Topics where user made mistakes"
    )
    
    suggestions: List[str] = Field(
        ..., 
        description="Actionable improvement tips (short)"
    )


class QuizEvaluation(BaseModel):
    wrong_questions_feedback: List[QuestionFeedback]
    
    final_summary: FinalSummary