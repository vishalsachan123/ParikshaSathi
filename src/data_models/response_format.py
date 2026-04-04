from typing import List
from pydantic import BaseModel, Field

class QuestionFeedback(BaseModel):
    id: int
    topic: str
    is_correct: bool
    reasoning: str = Field(..., description="Short explanation why correct option is right")
    steps: List[str] = Field(default_factory=list)
    why_wrong: str = Field(default="")


class TopicPerformance(BaseModel):
    topic: str
    correct: int
    total: int


class FinalSummary(BaseModel):
    total_questions: int
    correct_answers: int
    accuracy_percentage: float
    topic_performance: List[TopicPerformance]   # ✅ FIXED
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]


class QuizEvaluation(BaseModel):
    question_wise_feedback: List[QuestionFeedback]
    final_summary: FinalSummary
