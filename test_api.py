"""
API Integration Test Script
Tests all Gemini API functions to ensure everything is working
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_api_connection():
    """Test basic API connection"""
    print("=" * 50)
    print("Testing API Connection...")
    print("=" * 50)
    
    try:
        from api_helper import test_api_connection
        
        is_working = test_api_connection()
        
        if is_working:
            print("✅ API Connection: SUCCESS")
            return True
        else:
            print("❌ API Connection: FAILED")
            return False
    
    except Exception as e:
        print(f"❌ API Connection Error: {e}")
        return False


def test_smart_matching():
    """Test AI-powered resume matching"""
    print("\n" + "=" * 50)
    print("Testing AI Resume Matching...")
    print("=" * 50)
    
    try:
        from ai_matching import calculate_match_score, get_match_details
        
        resume_sample = """
        Senior Software Engineer with 5 years of experience.
        Skills: Python, JavaScript, React, Node.js, AWS, Docker
        Experience: Led a team of 3 developers on cloud migration project
        """
        
        job_sample = """
        Senior Developer Position
        Required Skills: Python, AWS, Docker, React
        Experience: 5+ years backend development
        """
        
        # Test basic matching
        score = calculate_match_score(resume_sample, job_sample, use_ai=True)
        print(f"Match Score: {score}%")
        
        # Test detailed matching
        details = get_match_details(resume_sample, job_sample)
        print(f"Score: {details['score']}%")
        print(f"Matched Keywords: {', '.join(details['matched_keywords'])}")
        print(f"Explanation: {details['explanation'][:100]}...")
        
        print("✅ AI Resume Matching: SUCCESS")
        return True
    
    except Exception as e:
        print(f"❌ AI Resume Matching Error: {e}")
        return False


def test_chat_response():
    """Test AI chat response generation"""
    print("\n" + "=" * 50)
    print("Testing AI Chat Response...")
    print("=" * 50)
    
    try:
        from ai_chat import generate_ai_response
        
        test_message = "What should I include in my resume for a Software Engineer position?"
        response = generate_ai_response(test_message, "user", "Software Engineer")
        
        print(f"User Message: {test_message}")
        print(f"AI Response: {response[:150]}...")
        
        print("✅ AI Chat Response: SUCCESS")
        return True
    
    except Exception as e:
        print(f"❌ AI Chat Response Error: {e}")
        return False


def test_job_analysis():
    """Test job requirement analysis"""
    print("\n" + "=" * 50)
    print("Testing Job Requirement Analysis...")
    print("=" * 50)
    
    try:
        from api_helper import analyze_job_requirements
        
        job_description = """
        Senior Product Manager Role
        Required: 5+ years PM experience, SQL, Python (for analytics)
        Nice to have: Machine Learning basics, Agile, Leadership
        Salary: $150K-$200K
        """
        
        analysis = analyze_job_requirements(job_description)
        
        print(f"Required Skills: {', '.join(analysis['required_skills'])}")
        print(f"Nice to Have: {', '.join(analysis['nice_to_have'])}")
        print(f"Experience: {analysis['experience']}")
        
        print("✅ Job Requirement Analysis: SUCCESS")
        return True
    
    except Exception as e:
        print(f"❌ Job Requirement Analysis Error: {e}")
        return False


def test_interview_suggestions():
    """Test interview question generation"""
    print("\n" + "=" * 50)
    print("Testing Interview Question Generation...")
    print("=" * 50)
    
    try:
        from ai_chat import suggest_interview_questions
        
        questions = suggest_interview_questions("Python Developer", ["Python", "React", "AWS"])
        
        print("Generated Interview Questions:")
        for i, q in enumerate(questions, 1):
            print(f"{i}. {q}")
        
        print("✅ Interview Question Generation: SUCCESS")
        return True
    
    except Exception as e:
        print(f"❌ Interview Question Generation Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n🚀 GEMINI API INTEGRATION TEST SUITE\n")
    
    results = {
        "API Connection": test_api_connection(),
        "Smart Matching": test_smart_matching(),
        "Chat Response": test_chat_response(),
        "Job Analysis": test_job_analysis(),
        "Interview Questions": test_interview_suggestions()
    }
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    total_passed = sum(1 for r in results.values() if r)
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests PASSED! API integration is working correctly.")
        return 0
    else:
        print(f"\n⚠️ {total_tests - total_passed} test(s) failed. Check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
