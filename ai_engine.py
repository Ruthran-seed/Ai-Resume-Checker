import os
import json
import re
from dotenv import load_dotenv
import google.generativeai as genai
from PyPDF2 import PdfReader

# ---------- Load ENV ----------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ---------- Gemini Model ----------
model = genai.GenerativeModel("gemini-pro")

# ---------- PDF Text Extraction ----------
def extract_text(pdf_path: str) -> str:
    """
    Extract text from a PDF resume
    """
    text = ""
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        print("PDF read error:", e)

    return text.strip()

# ---------- Gemini Resume ↔ JD Matching ----------
def gemini_match_resume(job_keywords: list, resume_text: str) -> dict:
    """
    Uses Gemini to semantically match resume against job keywords.
    Returns dict with match %, matched skills, missing skills.
    """

    prompt = f"""
You are an Applicant Tracking System (ATS).

Job required skills:
{", ".join(job_keywords)}

Resume content:
{resume_text}

Your task:
1. Identify matching skills
2. Identify missing skills
3. Calculate a match percentage (0 to 100)

Respond strictly in valid JSON only.

JSON format:
{{
  "match_percentage": number,
  "matched_skills": [],
  "missing_skills": []
}}
"""

    try:
        response = model.generate_content(prompt)
        raw_text = response.text
        return _parse_gemini_response(raw_text)
    except Exception as e:
        print("Gemini error:", e)
        return _empty_result()

# ---------- Safe JSON Parsing ----------
def _parse_gemini_response(text: str) -> dict:
    """
    Extract JSON safely from Gemini response
    """
    try:
        match = re.search(r"\{.*\}", text, re.S)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print("JSON parse error:", e)

    return _empty_result()

# ---------- Fallback ----------
def _empty_result() -> dict:
    return {
        "match_percentage": 0,
        "matched_skills": [],
        "missing_skills": []
    }
