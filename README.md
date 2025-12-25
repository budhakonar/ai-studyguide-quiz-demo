# AI Study Guide + Interactive Quiz Generator (PDF)

Turn any text-based PDF into a structured study guide and an interactive quiz experience.
The quiz runs one question at a time in a Streamlit modal, shows correctness + rationale, and displays the PDF page + excerpt where the question is grounded—so learners can review source material and continue.

---

## Demo Features
- Upload a PDF (text-based)
- Extract text page-by-page (PyMuPDF)
- Generate a structured **Study Guide** (headings + bullets)
- Generate a **Quiz** (MCQs with correct answer + rationale)
- Take the quiz in an interactive popup/modal (one question at a time)
- For each question: show **source page + excerpt** from the PDF
- Download outputs:
  - `study_guide.md`
  - `quiz.json` (includes source metadata)

---

## Tech Stack
- Python
- Streamlit (UI)
- OpenAI API (LLM generation)
- PyMuPDF (PDF extraction)
- Token-aware chunking (tiktoken)
- Structured quiz schema (Pydantic + OpenAI structured outputs)

---

## Project Structure

apps/
  streamlit_app.py          # Streamlit UI (upload, generate, interactive quiz)
src/
  studygen/
    pdf_extract.py          # PDF extraction
    chunking.py             # token-aware chunking
    prompts.py              # prompts for guide + quiz
    schema.py               # Pydantic quiz schema
    openai_client.py        # OpenAI client wrapper
    generate.py             # pipeline orchestration
outputs/                    # (optional) local outputs (gitignored)

---

## Setup

### 1) Clone repo
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

### 2) Create and activate a virtual environment

Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1

Git Bash:
python -m venv venv
source venv/Scripts/activate

### 3) Install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

### 4) Set your OpenAI API key
Create a `.env` file in the repo root:

OPENAI_API_KEY=sk-...

Do NOT commit `.env` (it should be in `.gitignore`).

---

## Run the App
python -m streamlit run apps/streamlit_app.py

Open the local URL Streamlit prints (usually http://localhost:8501).

---

## How It Works (High Level)
1. Extract PDF text page-by-page using PyMuPDF.
2. Chunk text safely based on tokens to fit model limits.
3. Generate a Study Guide from chunks + a final merge/cleanup pass.
4. Generate a Quiz using structured outputs to ensure valid schema.
5. Attach source page + excerpt for each question by matching question keywords to the most relevant PDF page.
6. Streamlit renders:
   - Study guide
   - Quiz JSON
   - Interactive quiz dialog with answer feedback and citations

---

## Limitations
- Works best with **text-based PDFs**. Scanned PDFs (images) require OCR (future work).
- Source attribution uses deterministic keyword matching; it is reliable for “where in the PDF” but is not a full semantic retriever.

---

## Roadmap / Future Enhancements
- OCR support for scanned PDFs (Tesseract or cloud OCR)
- Audio/podcast support:
  - Whisper transcription → same pipeline
- Improved retrieval grounding:
  - Embeddings + semantic search for stronger citation quality
- Difficulty selection and spaced repetition mode

---

## Resume Bullet (Example)
Built an AI-powered study tool that converts PDFs into structured study guides and interactive quizzes using Python, Streamlit, and OpenAI APIs, including token-aware chunking, schema-validated outputs, and PDF page/excerpt grounding for each quiz question.

---

## License
MIT (or your preferred license)
