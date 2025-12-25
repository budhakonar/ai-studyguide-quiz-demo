# apps/streamlit_app.py
# Drop-in Streamlit app: PDF -> Study Guide + Interactive Quiz (popup) with source page + excerpt

import json
import re
from typing import Dict, List, Optional, Tuple

import fitz  # PyMuPDF
import streamlit as st

from src.studygen.generate import run_pipeline


# -----------------------------
# Dialog compatibility (Streamlit versions)
# -----------------------------
DIALOG = getattr(st, "dialog", getattr(st, "experimental_dialog", None))
if DIALOG is None:
    raise RuntimeError(
        "Your Streamlit version does not support dialogs. Upgrade Streamlit: "
        "python -m pip install --upgrade streamlit"
    )


# -----------------------------
# PDF extraction (page-aware)
# -----------------------------
@st.cache_data(show_spinner=False)
def extract_pages_from_pdf_bytes(pdf_bytes: bytes, max_pages: Optional[int] = None) -> List[Dict]:
    """
    Returns: [{"page": 1, "text": "..."} , ...]
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page_count = len(doc)
    end = min(page_count, max_pages) if max_pages else page_count

    pages = []
    for i in range(end):
        txt = doc[i].get_text("text") or ""
        pages.append({"page": i + 1, "text": txt})
    return pages


def join_pages(pages: List[Dict]) -> str:
    return "\n\n".join(p["text"] for p in pages).strip()


# -----------------------------
# Lightweight source attribution (deterministic)
# -----------------------------
_STOP = {
    "the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "with", "as", "by",
    "is", "are", "was", "were", "be", "been", "this", "that", "these", "those", "it",
    "its", "from", "at", "into", "over", "under", "than", "then", "also", "such",
}

def _keywords(question: str) -> List[str]:
    toks = re.findall(r"[a-zA-Z]{4,}", question.lower())
    return [t for t in toks if t not in _STOP]


def _best_page_for_question(question: str, pages: List[Dict]) -> Tuple[int, str]:
    kws = _keywords(question)
    if not pages:
        return 1, ""
    if not kws:
        return pages[0]["page"], pages[0]["text"]

    best_score = -1
    best_page = pages[0]
    for p in pages:
        t = (p["text"] or "").lower()
        score = sum(t.count(k) for k in kws[:12])  # cap for speed
        if score > best_score:
            best_score = score
            best_page = p

    return best_page["page"], best_page["text"]


def _excerpt(page_text: str, question: str, window: int = 280) -> str:
    if not page_text:
        return ""
    kws = _keywords(question)
    low = page_text.lower()

    pos = -1
    for k in kws[:8]:
        pos = low.find(k)
        if pos != -1:
            break

    if pos == -1:
        # fallback: first chunk
        return page_text[: 2 * window].strip()

    start = max(0, pos - window)
    end = min(len(page_text), pos + window)
    snippet = page_text[start:end].strip()
    if start > 0:
        snippet = "… " + snippet
    if end < len(page_text):
        snippet = snippet + " …"
    return snippet


def attach_sources(quiz: Dict, pages: List[Dict]) -> Dict:
    """
    Mutates quiz dict to add:
      - source_page: int
      - source_excerpt: str
    """
    for q in quiz.get("questions", []):
        page_num, page_text = _best_page_for_question(q.get("question", ""), pages)
        q["source_page"] = page_num
        q["source_excerpt"] = _excerpt(page_text, q.get("question", ""))
    return quiz


# -----------------------------
# Interactive quiz dialog (one question at a time)
# -----------------------------
@DIALOG("Quiz")
def quiz_dialog():
    quiz = st.session_state.get("quiz")
    if not quiz or "questions" not in quiz or not quiz["questions"]:
        st.error("No quiz found. Generate a quiz first.")
        return

    qs = quiz["questions"]
    i = st.session_state.get("q_index", 0)
    i = max(0, min(i, len(qs) - 1))
    st.session_state.q_index = i

    q = qs[i]
    st.markdown(f"### Question {i + 1} of {len(qs)}")
    st.write(q["question"])

    choices = q["choices"]
    keys = ["A", "B", "C", "D"]

    def fmt(k: str) -> str:
        return f"{k}. {choices.get(k, '')}"

    # Persist choice per question
    choice_key = f"choice_{i}"
    if choice_key not in st.session_state:
        st.session_state[choice_key] = "A"

    choice = st.radio("Select an answer:", keys, format_func=fmt, key=choice_key)

    submitted_key = f"submitted_{i}"
    if submitted_key not in st.session_state:
        st.session_state[submitted_key] = False

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Submit", type="primary"):
            st.session_state[submitted_key] = True
            # record answer
            answers = st.session_state.get("answers", {})
            answers[i] = choice
            st.session_state.answers = answers
            st.rerun()

    with c2:
        # allow skipping without answering
        if st.button("Skip"):
            st.session_state[submitted_key] = True
            st.rerun()

    if st.session_state[submitted_key]:
        correct = q.get("correct")
        selected = st.session_state.get("answers", {}).get(i)

        if selected is None:
            st.warning("Skipped. You can still review the explanation and source.")
        elif selected == correct:
            st.success("Correct.")
        else:
            st.error(f"Incorrect. Correct answer: {correct}. {choices.get(correct, '')}")

        rationale = q.get("rationale", "")
        if rationale:
            st.write(f"**Rationale:** {rationale}")

        # Show source attribution
        src_page = q.get("source_page")
        src_excerpt = q.get("source_excerpt", "")
        if src_page is not None:
            st.info(f"Source: PDF page {src_page}")
        if src_excerpt:
            with st.expander("Show excerpt from PDF"):
                st.write(src_excerpt)

        nav1, nav2, nav3 = st.columns([1, 1, 1])
        with nav1:
            if st.button("Back", disabled=(i == 0)):
                st.session_state.q_index = i - 1
                st.rerun()
        with nav2:
            if st.button("Next", disabled=(i >= len(qs) - 1)):
                st.session_state.q_index = i + 1
                st.rerun()
        with nav3:
            if st.button("Finish"):
                st.session_state.finished = True
                st.rerun()


# -----------------------------
# App UI
# -----------------------------
st.set_page_config(page_title="AI Study Guide + Quiz Generator (PDF)", layout="wide")
st.title("AI Study Guide + Quiz Generator (PDF)")
st.caption("Upload a PDF → Generate a study guide → Take an interactive quiz with page + excerpt references.")

with st.sidebar:
    st.header("Settings")
    model = st.selectbox("Model", ["gpt-4o-mini"], index=0)  # keep constrained for your structured quiz
    n_questions = st.slider("Number of quiz questions", min_value=5, max_value=20, value=10, step=1)
    max_pages = st.slider("Max pages to process (speed)", min_value=1, max_value=40, value=10, step=1)

uploaded = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded:
    pdf_bytes = uploaded.read()

    with st.spinner("Extracting text from PDF..."):
        pages = extract_pages_from_pdf_bytes(pdf_bytes, max_pages=max_pages)
        raw_text = join_pages(pages)

    if not raw_text.strip():
        st.error("No extractable text found. If this is a scanned PDF, you would need OCR as a next enhancement.")
        st.stop()

    st.success(f"Extracted {len(raw_text):,} characters from {len(pages)} page(s).")

    with st.expander("Preview extracted text"):
        st.write(raw_text[:4000] + ("..." if len(raw_text) > 4000 else ""))

    colA, colB = st.columns([1, 1])
    with colA:
        generate_clicked = st.button("Generate Study Guide + Quiz", type="primary")
    with colB:
        open_quiz_clicked = st.button("Open Quiz (if already generated)")

    # Allow reopening quiz without regenerating
    if open_quiz_clicked:
        if st.session_state.get("quiz"):
            quiz_dialog()
        else:
            st.warning("No quiz found yet. Click 'Generate Study Guide + Quiz' first.")

    if generate_clicked:
        # Reset state for new run
        st.session_state.quiz = None
        st.session_state.study_guide = None
        st.session_state.q_index = 0
        st.session_state.answers = {}
        st.session_state.finished = False
        # Clear per-question submission flags/choices
        for k in list(st.session_state.keys()):
            if k.startswith("submitted_") or k.startswith("choice_"):
                del st.session_state[k]

        with st.spinner("Generating content (this may take a minute)..."):
            try:
                guide, quiz = run_pipeline(raw_text, model=model, n_questions=n_questions)
                quiz = attach_sources(quiz, pages)

                st.session_state.study_guide = guide
                st.session_state.quiz = quiz
            except Exception as e:
                st.exception(e)
                st.stop()

        st.success("Generation complete.")

        left, right = st.columns(2)
        with left:
            st.subheader("Study Guide")
            st.markdown(st.session_state.study_guide)

            st.download_button(
                label="Download Study Guide (.md)",
                data=st.session_state.study_guide,
                file_name="study_guide.md",
                mime="text/markdown",
            )

        with right:
            st.subheader("Quiz (JSON)")
            st.json(st.session_state.quiz)

            st.download_button(
                label="Download Quiz (.json)",
                data=json.dumps(st.session_state.quiz, indent=2),
                file_name="quiz.json",
                mime="application/json",
            )

        # Launch the interactive quiz popup immediately
        quiz_dialog()

# If finished, show a simple score summary on the main page
if st.session_state.get("finished") and st.session_state.get("quiz"):
    qs = st.session_state.quiz.get("questions", [])
    answers = st.session_state.get("answers", {})
    correct = 0
    answered = 0
    for i, q in enumerate(qs):
        if i in answers:
            answered += 1
            if answers[i] == q.get("correct"):
                correct += 1

    st.divider()
    st.subheader("Quiz Results")
    st.write(f"Answered: {answered}/{len(qs)}")
    st.write(f"Correct: {correct}/{len(qs)}")
    st.button("Review Quiz", on_click=quiz_dialog)
