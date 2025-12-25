STUDY_GUIDE_PROMPT = """You are an expert tutor. Create a student-friendly study guide from the material.
Requirements:
- Use headings and bullet points.
- Include: Key Concepts, Definitions, Examples (if present), Common Pitfalls, and a 5-bullet Quick Review.
- Keep it concise but complete.
Material:
"""

QUIZ_PROMPT = """Create a quiz from the study guide.

Return ONLY valid JSON. Do not include markdown fences. Do not include commentary.
The JSON must match exactly:

{
  "questions": [
    {
      "question": "string",
      "choices": {"A":"string","B":"string","C":"string","D":"string"},
      "correct": "A",
      "rationale": "string"
    }
  ]
}

Rules:
- Exactly {n} questions
- "correct" must be one of A,B,C,D
- Always include the top-level key "questions"
Study guide:
"""
