import json
import re
from typing import Any, Dict, Tuple

def extract_json_object(text: str) -> str:
    """
    Extract the first top-level JSON object from a string.
    Handles cases where the model returns extra text before/after JSON.
    """
    # Fast path: already JSON
    stripped = text.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped

    # Find first {...} block (greedy but bounded by balancing is hard; this works well in practice)
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in model output.")
    return match.group(0).strip()

def parse_quiz_json(text: str) -> Dict[str, Any]:
    json_str = extract_json_object(text)
    data = json.loads(json_str)

    if not isinstance(data, dict):
        raise ValueError("Parsed JSON is not an object.")
    if "questions" not in data:
        raise KeyError('Missing required top-level key: "questions"')
    if not isinstance(data["questions"], list) or len(data["questions"]) == 0:
        raise ValueError('"questions" must be a non-empty list.')

    return data
