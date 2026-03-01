import re
from api_helper import calculate_smart_match_score

def _clean_text(text: str) -> set:
    """
    Normalize text:
    - lowercase
    - remove special characters
    - split into unique words
    """
    if not text:
        return set()

    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    words = text.split()

    return set(words)


def calculate_match_score(resume_text: str, job_text: str, use_ai: bool = True) -> float:
    """
    Calculate resume-job match score (0–100)
    
    If use_ai=True: Uses Gemini AI for intelligent matching
    If use_ai=False: Falls back to keyword-based matching
    
    Logic:
    - AI: Analyzes skills, experience, keywords, job requirements
    - Fallback: Extract unique words and find common matches
    """

    if not resume_text or not job_text:
        return 0.0
    
    # Try AI-powered matching first
    if use_ai:
        try:
            result = calculate_smart_match_score(resume_text, job_text)
            if result and result.get("score"):
                return result["score"]
        except Exception as e:
            print(f"AI matching failed, falling back to keyword matching: {e}")
    
    # Fallback: Keyword-based matching
    resume_words = _clean_text(resume_text)
    job_words = _clean_text(job_text)

    if not resume_words or not job_words:
        return 0.0

    matched_words = resume_words.intersection(job_words)
    score = (len(matched_words) / len(job_words)) * 100

    return round(score, 2)


def get_match_details(resume_text: str, job_text: str) -> dict:
    """
    Get detailed matching information including keywords and explanation
    Returns: {score, matched_keywords, explanation}
    """
    try:
        return calculate_smart_match_score(resume_text, job_text)
    except Exception as e:
        print(f"Error getting match details: {e}")
        return {
            "score": calculate_match_score(resume_text, job_text, use_ai=False),
            "explanation": "Basic keyword matching used",
            "matched_keywords": []
        }
