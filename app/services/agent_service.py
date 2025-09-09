from fastapi import APIRouter, HTTPException
from app.services.workout_service import generate_workout_plan
from app.schemas.workout import WorkoutPlan, ProfileData
from app.agents.agents import classify_intent, handle_exercise_request, handle_nutrition_request, handle_general_request
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

# Create LLM class
load_dotenv()  # Try current directory first
if not os.getenv("GEMINI_API_KEY"):
    # Try relative path if current directory doesn't work
    load_dotenv('../.env')
if not os.getenv("GEMINI_API_KEY"):
    # Try absolute path as last resort
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    load_dotenv(env_path)


api_key = os.getenv("GEMINI_API_KEY")

def validate_response_data(data):
    """Ensure response data is in the correct format"""
    if data is None:
        return None
    if isinstance(data, str):
        if data.lower() in ['null', 'none', '']:
            return None
        # Try to parse as JSON if it's a string
        try:
            import json
            return json.loads(data)
        except:
            return None
    if isinstance(data, dict):
        return data
    # For any other type, convert to dict or return None
    try:
        return dict(data) if hasattr(data, '__dict__') else None
    except:
        return None

def create_mcp_client():
    from langchain_mcp_adapters.client import MultiServerMCPClient
    client = MultiServerMCPClient({
        "fitness": {
            "url": "http://localhost:8001/mcp/" if not os.getenv("MCP_SERVER_URL") else os.getenv("MCP_SERVER_URL"),
            "transport": "streamable_http",
        }
    })
    return client

async def agent(user_message: str, user_id: str = None):
    """
    Process user message and generate a response using the appropriate agent.
    
    Args:
        user_message: The message from the user
    """
    tools = await create_mcp_client().get_tools()
    llm_intent = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",
        temperature=0,
        google_api_key=api_key)

    llm_exercise = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        google_api_key=api_key,
    )

    llm_nutrition = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.9,
        google_api_key=api_key,
    )

    llm_general = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.9,
        google_api_key=api_key
    )

    try:
        intent = classify_intent(llm_intent, user_message)
        print(f"Classified intent: {intent}")
        if intent == "exercise":
            structured_result = await handle_exercise_request(llm_exercise, tools, user_message, user_id)
            # Convert ExerciseResponse to dict format for AgentResponse
            return {
                "text": structured_result.text,
                "data": validate_response_data(structured_result.data.model_dump() if structured_result.data else None)
            }
        elif intent == "nutrition":
            structured_result = await handle_nutrition_request(llm_nutrition, tools, user_message, user_id)
            # structured_result is already a dict from handle_nutrition_request
            return {
                "text": structured_result.get("text", ""),
                "data": validate_response_data(structured_result.get("data"))
            }
        else:
            structured_result = await handle_general_request(llm_general, tools, user_message, user_id)
            # Convert AgentResponse to dict format
            return {
                "text": structured_result.text,
                "data": validate_response_data(structured_result.data)
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))