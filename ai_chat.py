"""
AI Chat Response Module
Provides AI-powered responses for chat interactions
"""

from api_helper import generate_chat_response as gemini_generate_response


def generate_ai_response(user_message: str, sender_type: str = "user", job_title: str = "", user_profile: dict = None) -> str:
    """
    Generate an AI response based on user message and context
    
    Args:
        user_message: The user's message
        sender_type: "user" for job seeker, "host" for employer
        job_title: Job title for context
        user_profile: User profile data for context
    
    Returns:
        AI-generated response
    """
    
    context = ""
    
    if sender_type == "user":
        context = f"This is a job seeker asking about opportunities"
        if job_title:
            context += f" for a {job_title} position"
        if user_profile:
            skills = user_profile.get("skills", [])
            if skills:
                context += f". Their skills: {', '.join(skills)[:100]}"
    
    elif sender_type == "host":
        context = f"This is an employer/recruiter"
        if job_title:
            context += f" managing a {job_title} position"
    
    try:
        response = gemini_generate_response(user_message, context)
        return response if response else "I couldn't generate a response at this time. Please try again."
    except Exception as e:
        print(f"Error generating AI response: {e}")
        return "I'm experiencing technical difficulties. Please try again later."


def generate_job_inquiry_response(job_title: str, applicant_name: str = "") -> str:
    """
    Generate an automated response for a job inquiry
    """
    prompt = f"Write a professional but friendly response to a job inquiry for a {job_title} position"
    if applicant_name:
        prompt += f" from {applicant_name}"
    
    try:
        response = gemini_generate_response(prompt)
        return response if response else "Thank you for your inquiry. We'll get back to you soon."
    except Exception as e:
        print(f"Error generating job inquiry response: {e}")
        return "Thank you for your inquiry. We'll get back to you soon."


def generate_rejection_email(job_title: str, applicant_name: str = "") -> str:
    """
    Generate a professional rejection email
    """
    prompt = f"Write a professional, empathetic rejection email for a {job_title} position applicant"
    if applicant_name:
        prompt = f"Write to {applicant_name}, a " + prompt
    
    try:
        response = gemini_generate_response(prompt)
        return response if response else "Thank you for your interest. Unfortunately, we've decided to move forward with other candidates."
    except Exception as e:
        print(f"Error generating rejection email: {e}")
        return "Thank you for your interest. Unfortunately, we've decided to move forward with other candidates."


def suggest_interview_questions(job_title: str, skills: list = None) -> list:
    """
    Generate interview questions for a specific job
    """
    skills_str = ", ".join(skills) if skills else ""
    
    prompt = f"""Generate 5 interview questions for a {job_title} position"""
    if skills_str:
        prompt += f" requiring skills in {skills_str}"
    
    prompt += ". Format as a numbered list."
    
    try:
        response = gemini_generate_response(prompt)
        if response:
            questions = [q.strip() for q in response.split("\n") if q.strip() and any(c.isalpha() for c in q)]
            return questions[:5]
    except Exception as e:
        print(f"Error suggesting interview questions: {e}")
    
    return ["Tell us about a challenging project you've worked on.", "How do you stay updated with industry trends?"]


def analyze_application_fit(resume_text: str, job_description: str) -> dict:
    """
    Analyze how well a candidate fits a job
    Returns: {fit_level, strengths, weaknesses, recommendations}
    """
    
    prompt = f"""
    Analyze this resume for a job position:
    
    RESUME EXCERPT:
    {resume_text[:1000]}
    
    JOB DESCRIPTION EXCERPT:
    {job_description[:1000]}
    
    Provide:
    1. Fit level (Good/Fair/Needs Development)
    2. Top 3 candidate strengths for this role
    3. Top 3 areas of concern or gaps
    4. Specific recommendations
    
    Format:
    FIT: [level]
    STRENGTHS: [list]
    GAPS: [list]
    RECOMMENDATIONS: [suggestions]
    """
    
    try:
        response = gemini_generate_response(prompt)
        
        if not response:
            return {
                "fit_level": "Unknown",
                "strengths": [],
                "gaps": [],
                "recommendations": []
            }
        
        result = {
            "fit_level": "Fair",
            "strengths": [],
            "gaps": [],
            "recommendations": ""
        }
        
        lines = response.split("\n")
        for line in lines:
            if "FIT:" in line:
                result["fit_level"] = line.replace("FIT:", "").strip()
            elif "STRENGTHS:" in line:
                strengths_str = line.replace("STRENGTHS:", "").strip()
                result["strengths"] = [s.strip() for s in strengths_str.split(",") if s.strip()]
            elif "GAPS:" in line:
                gaps_str = line.replace("GAPS:", "").strip()
                result["gaps"] = [g.strip() for g in gaps_str.split(",") if g.strip()]
            elif "RECOMMENDATIONS:" in line:
                result["recommendations"] = line.replace("RECOMMENDATIONS:", "").strip()
        
        return result
    
    except Exception as e:
        print(f"Error analyzing application fit: {e}")
        return {
            "fit_level": "Unable to analyze",
            "strengths": [],
            "gaps": [],
            "recommendations": "Try uploading a clearer resume or job description."
        }
