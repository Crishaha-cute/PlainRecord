"""Extract text from an uploaded record file (.pdf or .txt)."""

import io
from pypdf import PdfReader


def extract_text(uploaded_file) -> str:
    """
    Given a Streamlit UploadedFile, return its text content.
    Supports .pdf and .txt files.
    """
    name = uploaded_file.name.lower()

    if name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="ignore")

    if name.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(uploaded_file.read()))
        pages_text = []
        for page in reader.pages:
            pages_text.append(page.extract_text() or "")
        return "\n".join(pages_text).strip()

    raise ValueError(f"Unsupported file type: {uploaded_file.name}")
