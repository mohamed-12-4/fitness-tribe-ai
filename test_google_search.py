#!/usr/bin/env python3
"""
Test script for Google Search functionality with Gemini
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.models.gemini_model import GeminiModel
import json

def test_google_search():
    """Test the Google search functionality"""
    print("Testing Google Search...")
    
    # Test the search function directly
    search_result = GeminiModel.google_search("chicken breast nutrition facts", 3)
    print("\n=== Direct Search Results ===")
    print(json.dumps(search_result, indent=2))
    
    return search_result

def test_function_call():
    """Test the function call handler"""
    print("\n\nTesting Function Call Handler...")
    
    # Create a mock function call object
    class MockFunctionCall:
        def __init__(self):
            self.name = "google_search"
            self.args = {"query": "best protein sources for muscle building", "num_results": 3}
    
    mock_call = MockFunctionCall()
    result = GeminiModel.handle_function_call(mock_call)
    
    print("\n=== Function Call Results ===")
    print(json.dumps(result, indent=2))
    
    return result

def main():
    """Main test function"""
    print("🔍 Google Search Tool Test")
    print("=" * 50)
    
    # Check if SERP API key is configured
    serp_key = os.getenv("SERP_API_KEY")
    if not serp_key or serp_key == "your_serp_api_key_here":
        print("⚠️  SERP API key not configured!")
        print("Please set your SERP_API_KEY in the .env file")
        print("Get your key from: https://serpapi.com/")
        return
    
    try:
        # Test direct search
        search_result = test_google_search()
        
        # Test function call handler
        function_result = test_function_call()
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
