import re

_STOP = {
    "the","a","an","and","or","to","of","in","on","for","with","as","by","is","are",
    "was","were","be","been","this","that","these","those","it","its","from","at"
}

def _keywords(question: str):
    toks = re.findall(r"[a-zA-Z]{4,}", question.lower())
    return [t for t in toks if t not in _STOP]

def _best_page(question: str, pages):
    kws = _keywords(question)
    if not kws:
        return pages[0]["page"], pages[0]["text"]

    best = (0, pages[0])
    for p in pages:
        t = p["text"].lower()
        score = sum(t.count(k) for k in kws)
        if score > best[0]:
            best = (score, p)

    return best[1]["page"], best[1]["text"]

def _excerpt(page_text: str, question: str, window: int = 250) -> str:
    kws = _keywords(question)
    low = page_text.lower()
    pos = -1
    hit = None
    for k in kws[:6]:
        pos = low.find(k)
        if pos != -1:
            hit = k
            break

    if pos == -1:
        # fallback: first N chars
        return page_text[: 2*window].strip()

    start = max(0, pos - window)
    end = min(len(page_text), pos + window)
    snippet = page_text[start:end].strip()
    if start > 0:
        snippet = "… " + snippet
    if end < len(page_text):
        snippet = snippet + " …"
    return snippet

def attach_sources(quiz: dict, pages):
    for q in quiz.get("questions", []):
        page_num, page_text = _best_page(q["question"], pages)
        q["source_page"] = page_num
        q["source_excerpt"] = _excerpt(page_text, q["question"])
    return quiz
