from pydantic import BaseModel
from typing import List, Literal

ChoiceKey = Literal["A", "B", "C", "D"]

class Choices(BaseModel):
    A: str
    B: str
    C: str
    D: str

class QuizQuestion(BaseModel):
    question: str
    choices: Choices
    correct: ChoiceKey
    rationale: str

class Quiz(BaseModel):
    questions: List[QuizQuestion]
