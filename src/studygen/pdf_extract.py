import fitz  # PyMuPDF

def extract_pages_from_pdf_bytes(pdf_bytes: bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []
    for idx in range(len(doc)):
        txt = doc[idx].get_text("text") or ""
        pages.append({"page": idx + 1, "text": txt})
    return pages

def join_pages(pages) -> str:
    return "\n\n".join(p["text"] for p in pages).strip()
