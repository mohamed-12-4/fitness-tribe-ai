from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
import asyncio
from app.agents.agents import classify_intent, handle_exercise_request, handle_nutrition_request
import json
from langchain_core.messages import HumanMessage

# Create LLM class
load_dotenv()  # Try current directory first
if not os.getenv("GEMINI_API_KEY"):
    # Try relative path if current directory doesn't work
    load_dotenv('../.env')
if not os.getenv("GEMINI_API_KEY"):
    # Try absolute path as last resort
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    load_dotenv(env_path)



# Import your schemas
import sys
sys.path.append('/home/mohamed/Code/fitness-tribe-ai')

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

async def main():
    # Create LLM with structured output
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        google_api_key=api_key,
    )

    llm_nutrition = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.9,
        google_api_key=api_key,
    )
    
    # Create structured output LLM
    
    client = MultiServerMCPClient({
        "fitness": {
            "command": "python3",
            "args": ["app/playground/mcp_server.py"],
            "transport": "stdio",
        }
    })
    
    try:
        tools = await client.get_tools()
        user_message = "I want you to generate a 7 days nutrition plan with breakfast, lunch, dinner and snacks. I'm going to the gym 5 days a week to build muscle and strength. My goal is to consume around 3000 calories per day with a good balance of protein, carbs, and fats"
        intent = classify_intent(user_message)
        print(f"Classified intent: {intent}")
        if intent == "exercise":
            structured_result = await handle_exercise_request(llm, tools, user_message)
        else:
            structured_result = await handle_nutrition_request(llm_nutrition, tools, user_message)
        print("\n=== STRUCTURED RESPONSE ===")
        print(f"Text: {structured_result.text}")
        print(f"\nData: {structured_result.data}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())