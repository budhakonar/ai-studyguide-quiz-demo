from typing import Tuple, Dict, Any

from .chunking import chunk_text
from .prompts import STUDY_GUIDE_PROMPT, QUIZ_PROMPT
from .schema import Quiz
from .openai_client import client, require_api_key, responses_text


def generate_study_guide(raw_text: str, model: str) -> str:
    chunks = chunk_text(raw_text, model=model, max_tokens_per_chunk=1200)

    partial_summaries = []
    for c in chunks:
        prompt = STUDY_GUIDE_PROMPT + "\n\n" + c.text
        partial = responses_text(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert tutor. Produce a structured study guide."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_output_tokens=700,
        )
        partial_summaries.append(partial)

    combined = "\n\n".join(partial_summaries)

    final_prompt = (
        "Combine and clean up the following partial study guides into ONE cohesive study guide. "
        "Remove duplicates, keep structure, and keep it student-friendly.\n\n"
        + combined
    )
    return responses_text(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert tutor. Produce a cohesive structured study guide."},
            {"role": "user", "content": final_prompt},
        ],
        temperature=0.2,
        max_output_tokens=900,
    )


def generate_quiz(study_guide: str, model: str, n: int = 10) -> dict:
    """
    Uses Structured Outputs via responses.parse() so the output conforms to Quiz schema.
    """
    require_api_key()

    # Avoid .format() because the prompt contains JSON braces.
    prompt = QUIZ_PROMPT.replace("{n}", str(n)) + "\n\n" + study_guide

    resp = client.responses.parse(
        model=model,
        input=[
            {"role": "system", "content": "You are an expert exam writer. Return only the required structured output."},
            {"role": "user", "content": prompt},
        ],
        text_format=Quiz,
    )

    quiz_obj = resp.output_parsed
    return quiz_obj.model_dump()


def run_pipeline(raw_text: str, model: str, n_questions: int) -> Tuple[str, Dict[str, Any]]:
    guide = generate_study_guide(raw_text, model=model)
    quiz = generate_quiz(guide, model=model, n=n_questions)
    return guide, quiz
