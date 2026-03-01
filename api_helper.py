"""
Gemini API Helper Module
Handles API initialization and common functions
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env
load_dotenv()

# Initialize Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found in .env file")

genai.configure(api_key=API_KEY)

# Get the Gemini model (use newer model name)
# Try gemini-2.0-flash first, fallback to gemini-1.5-flash
try:
    model = genai.GenerativeModel("gemini-2.0-flash")
except:
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
    except:
        # Final fallback
        model = genai.GenerativeModel("gemini-1.5-pro")


def extract_resume_text_with_ai(pdf_path: str) -> str:
    """
    Extract and clean resume text from PDF using Gemini AI
    Fallback to basic extraction if PDF reading fails
    """
    import re
    
    # Try basic extraction first
    try:
        with open(pdf_path, "rb") as f:
            raw_data = f.read()
        
        # Attempt to decode
        try:
            text = raw_data.decode("utf-8", errors="ignore")
        except:
            text = raw_data.decode("latin-1", errors="ignore")
        
        if not text or len(text.strip()) < 50:
            return ""
        
        # Clean extracted text
        text = re.sub(r"\s+", " ", text)
        text = text.replace("\n", " ").strip()
        
        # Use Gemini to clean and enhance the text
        try:
            prompt = f"""
            Clean and organize this resume text. Remove garbled characters, 
            fix spacing, and return only the readable content:
            
            {text[:2000]}  # Limit to first 2000 chars to avoid API quota issues
            """
            
            response = model.generate_content(prompt, stream=False)
            if response and response.text:
                return response.text
        except:
            # If Gemini fails, return the basic extraction
            pass
        
        return text
    
    except Exception as e:
        print(f"Error extracting resume: {e}")
        return ""


def calculate_smart_match_score(resume_text: str, job_text: str) -> dict:
    """
    Calculate resume-job match score using Gemini AI
    Returns: {score: 0-100, explanation: str, matched_keywords: []}
    """
    
    if not resume_text or not job_text:
        return {
            "score": 0.0,
            "explanation": "Unable to analyze: missing resume or job description",
            "matched_keywords": []
        }
    
    try:
        prompt = f"""
        Analyze how well this resume matches the job description.
        
        RESUME:
        {resume_text[:1500]}
        
        JOB DESCRIPTION:
        {job_text[:1500]}
        
        Provide:
        1. Match score (0-100)
        2. Key matched skills/keywords (comma-separated)
        3. Brief explanation (1-2 sentences)
        
        Format your response as:
        SCORE: [number]
        KEYWORDS: [keywords]
        EXPLANATION: [explanation]
        """
        
        response = model.generate_content(prompt, stream=False)
        
        if not response or not response.text:
            return {
                "score": 0.0,
                "explanation": "Unable to analyze with AI",
                "matched_keywords": []
            }
        
        result_text = response.text
        
        # Parse the response
        score = 0.0
        keywords = []
        explanation = ""
        
        lines = result_text.split("\n")
        for line in lines:
            if "SCORE:" in line:
                try:
                    score_str = line.replace("SCORE:", "").strip()
                    score = float(score_str.split()[0])
                    score = min(100, max(0, score))  # Clamp between 0-100
                except:
                    pass
            elif "KEYWORDS:" in line:
                keywords_str = line.replace("KEYWORDS:", "").strip()
                keywords = [k.strip() for k in keywords_str.split(",") if k.strip()]
            elif "EXPLANATION:" in line:
                explanation = line.replace("EXPLANATION:", "").strip()
        
        return {
            "score": round(score, 2),
            "explanation": explanation if explanation else result_text[:200],
            "matched_keywords": keywords
        }
    
    except Exception as e:
        print(f"Error in AI matching: {e}")
        return {
            "score": 0.0,
            "explanation": f"AI analysis failed: {str(e)[:100]}",
            "matched_keywords": []
        }


def generate_chat_response(user_message: str, context: str = "") -> str:
    """
    Generate an AI-powered response for chat
    context: additional context (user profile, job details, etc.)
    """
    
    try:
        full_prompt = f"""
        You are an AI assistant helping with job matching and career development.
        Be helpful, professional, and concise.
        
        Context: {context}
        
        User message: {user_message}
        
        Provide a helpful response:
        """
        
        response = model.generate_content(full_prompt, stream=False)
        
        if response and response.text:
            return response.text.strip()
        else:
            return "I apologize, I couldn't generate a response at this time."
    
    except Exception as e:
        import traceback
        error_str = str(e)
        error_details = traceback.format_exc()
        print(f"Error generating chat response: {e}")
        print(f"Full traceback: {error_details}")
        
        # Handle quota exceeded errors specifically
        if "429" in error_str or "quota" in error_str.lower() or "exceeded" in error_str.lower():
            return "⚠️ API quota exceeded. Please try again in a few moments or upgrade your API plan at https://console.cloud.google.com/"
        
        return f"I'm experiencing technical difficulties. Please try again later."


def analyze_job_requirements(job_text: str) -> dict:
    """
    Analyze job description and extract key requirements
    Returns: {required_skills: [], nice_to_have: [], experience: str}
    """
    
    if not job_text:
        return {
            "required_skills": [],
            "nice_to_have": [],
            "experience": ""
        }
    
    try:
        prompt = f"""
        Analyze this job description and extract:
        1. Required technical skills (bullet list)
        2. Nice-to-have skills (bullet list)
        3. Years of experience needed
        
        JOB DESCRIPTION:
        {job_text[:1500]}
        
        Format your response as:
        REQUIRED: skill1, skill2, skill3
        NICE_TO_HAVE: skill1, skill2
        EXPERIENCE: X years
        """
        
        response = model.generate_content(prompt, stream=False)
        
        if not response or not response.text:
            return {
                "required_skills": [],
                "nice_to_have": [],
                "experience": ""
            }
        
        result_text = response.text
        
        required = []
        nice_to_have = []
        experience = ""
        
        lines = result_text.split("\n")
        for line in lines:
            if "REQUIRED:" in line:
                skills_str = line.replace("REQUIRED:", "").strip()
                required = [s.strip() for s in skills_str.split(",") if s.strip()]
            elif "NICE_TO_HAVE:" in line:
                skills_str = line.replace("NICE_TO_HAVE:", "").strip()
                nice_to_have = [s.strip() for s in skills_str.split(",") if s.strip()]
            elif "EXPERIENCE:" in line:
                experience = line.replace("EXPERIENCE:", "").strip()
        
        return {
            "required_skills": required,
            "nice_to_have": nice_to_have,
            "experience": experience
        }
    
    except Exception as e:
        print(f"Error analyzing job requirements: {e}")
        return {
            "required_skills": [],
            "nice_to_have": [],
            "experience": ""
        }


def test_api_connection() -> bool:
    """
    Test if the API connection is working
    """
    try:
        response = model.generate_content("Say 'API is working' briefly.", stream=False)
        return response and response.text and "working" in response.text.lower()
    except Exception as e:
        print(f"API Connection Error: {e}")
        return False
