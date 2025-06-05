#!/usr/bin/env python3
"""
Test script for Gemini AI configuration
Run this to verify your Gemini API key is working
"""

import os
import sys
import django
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup Django
sys.path.append('/Users/maxime/Documents/Isitech_django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Isitech_django.settings')
django.setup()

def test_gemini_config():
    """Test if Gemini API is properly configured and working"""
    
    print("🤖 Testing Gemini AI Configuration...")
    print("=" * 50)
    
    # Check if API key is set
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable not set")
        print("💡 Please add your API key to the .env file")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Test import
    try:
        import google.generativeai as genai
        print("✅ Google Generative AI library imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Google Generative AI: {e}")
        print("💡 Run: pip install google-generativeai")
        return False
    
    # Test API connection
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        print("🔄 Testing API connection with a simple prompt...")
        
        response = model.generate_content(
            "Write a single sentence about artificial intelligence.",
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 50,
            }
        )
        
        if response and response.text:
            print("✅ API connection successful!")
            print(f"📝 Test response: {response.text.strip()}")
            return True
        else:
            print("❌ API returned empty response")
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ API connection failed: {error_msg}")
        
        if "API_KEY" in error_msg.upper():
            print("💡 Your API key might be invalid. Check it at: https://aistudio.google.com/app/apikey")
        elif "QUOTA" in error_msg.upper():
            print("💡 You might have exceeded your API quota. Check your usage.")
        else:
            print("💡 There might be a network issue or API service problem.")
        
        return False

if __name__ == "__main__":
    success = test_gemini_config()
    print("=" * 50)
    if success:
        print("🎉 Gemini AI is ready to use!")
        print("🚀 You can now use the AI Article Generator")
    else:
        print("🔧 Please fix the issues above before using the AI features")
    print("=" * 50)
