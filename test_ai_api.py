"""
Test script to verify API is working
"""
import os
from dotenv import load_dotenv

print("Testing Gemini API Connection...")

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

print(f"API Key loaded: {bool(API_KEY)}")
print(f"API Key (first 20 chars): {API_KEY[:20] if API_KEY else 'None'}...")

try:
    import google.generativeai as genai
    print("✓ google.generativeai imported successfully")
    
    genai.configure(api_key=API_KEY)
    print("✓ API configured")
    
    # Try to initialize model
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        print("✓ gemini-2.0-flash model loaded")
    except Exception as e:
        print(f"✗ gemini-2.0-flash failed: {e}")
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            print("✓ gemini-1.5-flash model loaded (fallback)")
        except Exception as e2:
            print(f"✗ gemini-1.5-flash failed: {e2}")
            model = genai.GenerativeModel("gemini-1.5-pro")
            print("✓ gemini-1.5-pro model loaded (fallback)")
    
    # Test a simple message
    print("\nTesting API response...")
    response = model.generate_content("Say hello in one sentence")
    print(f"✓ API Response: {response.text}")
    
    print("\n✅ All tests passed!")
    
except Exception as e:
    import traceback
    print(f"\n✗ Error: {e}")
    print(f"Full traceback:\n{traceback.format_exc()}")
