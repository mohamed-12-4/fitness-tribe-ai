#!/usr/bin/env python3
"""
Example: Using Gemini with Google Search Tool for Food Analysis
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import google.generativeai as gemini
from google.genai import types
from app.models.gemini_model import GeminiModel
import json

def example_food_query():
    """Example of asking about food with Google search grounding"""
    
    # Initialize the model with the search tool
    GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
    if not GEMINI_KEY:
        print("❌ GEMINI_API_KEY not found!")
        return
    
    gemini.configure(api_key=GEMINI_KEY)
    
    # Create the Google search tool
    google_search_tool = types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="google_search",
                description="Search Google for information about food, nutrition, recipes, or any general topic",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "query": types.Schema(
                            type=types.Type.STRING,
                            description="The search query to look up information"
                        ),
                        "num_results": types.Schema(
                            type=types.Type.INTEGER,
                            description="Number of search results to return (default: 5)"
                        )
                    },
                    required=["query"]
                )
            )
        ]
    )
    
    model = gemini.GenerativeModel("gemini-2.5-flash", tools=[google_search_tool])
    
    # Ask about a specific food item
    prompt = """
    I want to know about quinoa. Please search for current nutritional information 
    and health benefits, then provide me with a comprehensive summary including:
    
    1. Nutritional facts per 100g
    2. Health benefits
    3. How to cook it
    4. Best food pairings
    
    Use the google_search function to get the most current information.
    """
    
    print("🤖 Asking Gemini about quinoa with Google search...")
    print("Query:", prompt)
    print("\n" + "="*80)
    
    try:
        response = model.generate_content(prompt)
        
        # Handle function calls
        if response.candidates[0].content.parts:
            conversation = [prompt]
            
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    print(f"\n🔍 Model is searching: {part.function_call.args.get('query', 'unknown query')}")
                    
                    # Handle the function call
                    function_result = GeminiModel.handle_function_call(part.function_call)
                    
                    print(f"📊 Search returned {function_result.get('total_results', 0)} results")
                    
                    # Add function call and response to conversation
                    conversation.extend([
                        types.Content(parts=[part]),
                        types.Content(parts=[types.Part(
                            function_response=types.FunctionResponse(
                                name=part.function_call.name,
                                response=function_result
                            )
                        )])
                    ])
            
            # Get final response with search results
            if len(conversation) > 1:
                final_response = model.generate_content(conversation)
                print("\n📝 Final Answer:")
                print("-" * 40)
                print(final_response.text)
            else:
                print("\n📝 Direct Answer:")
                print("-" * 40)
                print(response.text)
        else:
            print("\n📝 Direct Answer:")
            print("-" * 40)
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    print("🔍 Google Search + Gemini Integration Example")
    print("=" * 50)
    
    # Check requirements
    serp_key = os.getenv("SERP_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if not serp_key or serp_key == "your_serp_api_key_here":
        print("⚠️  SERP API key not configured!")
        print("Please set your SERP_API_KEY in the .env file")
        return
        
    if not gemini_key:
        print("⚠️  GEMINI API key not found!")
        print("Please set your GEMINI_API_KEY in the .env file")
        return
    
    # Run the example
    example_food_query()

if __name__ == "__main__":
    main()
