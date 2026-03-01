import os
from api_helper import extract_resume_text_with_ai

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract resume text from PDF using Gemini AI
    Falls back to basic extraction if AI is unavailable
    """

    if not pdf_path or not os.path.exists(pdf_path):
        return ""

    text = ""

    try:
        # Try AI-powered extraction first
        text = extract_resume_text_with_ai(pdf_path)
        if text and len(text.strip()) > 50:
            return text
    except Exception as e:
        print(f"AI extraction failed, falling back to basic: {e}")

    # Fallback: basic extraction
        with open(pdf_path, "rb") as f:
            raw = f.read()

        # Try decoding raw bytes (best-effort)
        try:
            text = raw.decode("utf-8", errors="ignore")
        except Exception:
            text = raw.decode("latin-1", errors="ignore")

    except Exception:
        return ""

    # Clean text
    text = text.replace("\n", " ").replace("\r", " ")
    text = " ".join(text.split())

    return text
