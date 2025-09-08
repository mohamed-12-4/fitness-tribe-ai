from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from ss import ExerciseResponse,  NutritionResponse
import re
import json
def classify_intent(user_message: str) -> str:
    """Classify user intent as either 'exercise' or 'nutrition'"""
    
    # Exercise keywords
    exercise_keywords = [
        r"\bworkout\b", r"\bexercise\b", r"\btraining\b", r"\bgym\b", r"\bfitness\b",
        r"\bmuscle\b", r"\bstrength\b", r"\bcardio\b", r"\breps\b", r"\bsets\b",
        r"\bpush.?up\b", r"\bsquat\b", r"\bdeadlift\b", r"\bbench press\b",
        r"\bworkout plan\b", r"\btraining plan\b", r"\bexercise routine\b"
    ]
    
    # Nutrition keywords
    nutrition_keywords = [
        r"\bmeal\b", r"\bfood\b", r"\bnutrition\b", r"\bdiet\b", r"\beating\b",
        r"\bcalories\b", r"\bprotein\b", r"\bcarbs\b", r"\bfat\b", r"\bvitamin\b",
        r"\bmeal plan\b", r"\bdiet plan\b", r"\bnutrition plan\b", r"\bbrand\b",
        r"\bbreakfast\b", r"\blunch\b", r"\bdinner\b", r"\bsnack\b"
    ]
    
    # Count matches
    exercise_matches = sum(1 for keyword in exercise_keywords if re.search(keyword, user_message, re.I))
    nutrition_matches = sum(1 for keyword in nutrition_keywords if re.search(keyword, user_message, re.I))
    
    # Return the category with more matches, default to exercise if tied
    if nutrition_matches > exercise_matches:
        return "nutrition"
    else:
        return "exercise"


async def handle_exercise_request(llm, tools, user_message: str):
    """Handle exercise-related requests"""
    
    # Filter tools for exercise-related ones
    
    # Create structured output LLM
    structured_llm = llm.with_structured_output(ExerciseResponse)
    
    # Exercise-specific prompt
    exercise_prompt = """You are a fitness expert assistant. Your task is to:
1. Use available tools to gather exercise information
2. Generate a comprehensive workout plan
3. Return both explanatory text and structured data
4. NEVER MAKE UP EXERCISE NAMES OR DETAILS, USE TOOLS TO FIND REAL EXERCISES AND THEIR IDS
5. To start first make sure to list all available facts about exercises using the list_facts tool. Then plan the target muscles and exercises accordingly. Then use the get_exercise_by_target tool to find the exercise details and add the use the best one in the plan.

Response format:
- text: Include your reasoning, explanations, and any additional context
- data: The complete workout plan following the WorkoutPlan schema

Always use tools to find real exercises before creating the plan."""

    # Create exercise agent
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=exercise_prompt
    )
    
    # Get agent response
    agent_result = await agent.ainvoke({
        "messages": [HumanMessage(content=user_message)]
    })
    
    # Extract the final message content
    final_message = agent_result["messages"][-1].content
    
    # Use structured LLM to format the response
    structure_prompt = f"""
Based on the following agent response, create a structured output with:
1. text: Summary and explanation of the workout plan
2. data: Complete workout plan in WorkoutPlan format

Agent response:
{final_message}

Create a comprehensive workout plan with:
- Proper warm-up (5-10 minutes)
- Cardio component (15-20 minutes) 
- Workout sessions covering major muscle groups
- Cool-down (5-10 minutes)
- Each exercise should have: name, sets, reps, rest time
- Use realistic exercise names and parameters
"""
    
    structured_result = await structured_llm.ainvoke([HumanMessage(content=structure_prompt)])
    return ExerciseResponse(text=structured_result.text, data=structured_result.data)

async def handle_nutrition_request(llm, tools, user_message: str):
    """Handle nutrition-related requests"""
    
    # Filter tools for nutrition-related ones
    
    # Create structured output LLM
    structured_llm = llm
    
    # Nutrition-specific prompt
    nutrition_prompt = """You are a nutrition expert assistant. Your task is to:
1. Use available tools to get the users nutrition information if needed. If no tools related to nutrition are available, proceed to step and make it. The tools only related to exercise should not be used.
2. Generate a comprehensive meal plan or answer nutrition questions
3. Return both explanatory text and structured data when applicable

Response format:
- text: Include your reasoning, explanations, and any additional context
- data: The complete meal plan following the MealPlan schema (or null for general questions or recommendations)

Always use the appropriate tool based on the user's request."""

    # Create nutrition agent
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=nutrition_prompt
    )
    
    # Get agent response
    agent_result = await agent.ainvoke({
        "messages": [HumanMessage(content=user_message)]
    })
    
    # Extract the final message content
    final_message = agent_result["messages"][-1].content
    from datetime import datetime
    today_date = datetime.now().strftime("%Y-%m-%d")
    
    # Use structured LLM to format the response
    structure_prompt = f"""
Based on the following agent response, create a structured output with:
1. text: Summary and explanation of the nutrition advice or meal plan
2. data: Complete meal plan in MealPlan format (or null if this is a general question). If the data is a meal plan structure it in this format:

Respond in valid JSON format with no additional explanation or text:

{{"text": "<summary text>",
"data": <If needed only for generation responses> {{
    "daily_calories_range": {{"min": <min calories>, "max": <max calories>}},
    "macronutrients_range": {{
        "protein": {{"min": <min grams>, "max": <max grams>}},
        "carbohydrates": {{"min": <min grams>, "max": <max grams>}},
        "fat": {{"min": <min grams>, "max": <max grams>}}
    }},
    "daily_meal_plans": [
        {{
        "day": 1,
        "date": "{today_date}",
        "breakfast": {{
            "description": "<meal description>",
            "ingredients": [
            {{"ingredient": "<ingredient>", "quantity": "<quantity>", "calories": <whole_number_calories>}}
            ],
            "total_calories": <whole_number_calories>,
            "recipe": "<detailed recipe with cooking time>",
            "suggested_brands": ["<UAE brands>"]
        }},
        "lunch": {{"description": "...", "ingredients": [...], "total_calories": <whole_number_calories>, "recipe": "...", "suggested_brands": [...]}},
        "dinner": {{"description": "...", "ingredients": [...], "total_calories": <whole_number_calories>, "recipe": "...", "suggested_brands": [...]}},
        "snacks": [
            {{"description": "...", "ingredients": [...], "total_calories": <whole_number_calories>, "recipe": "...", "suggested_brands": [...]}}
        ],
        "total_daily_calories": <whole_number_total>,
        "daily_macros": {{"protein": <grams>, "carbohydrates": <grams>, "fat": <grams>}}
        }}
        // Repeat for all duration days with different meals each day
    ],
    "total_days": duration days
}}}}

Agent response:
{final_message}

If this is a meal plan request, create a comprehensive meal plan with:
- Daily calorie ranges
- Macronutrient breakdowns
- Daily meal plans with breakfast, lunch, dinner, and snacks
- Detailed recipes and brand recommendations
- Use realistic meal names and nutritional parameters

If this is a general nutrition question, set data to null and provide the answer in text.
"""
    
    structured_result = await structured_llm.ainvoke([HumanMessage(content=structure_prompt)])
    results = structured_result
    print(results)
    results = json.loads(results.content)
    return results