from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from app.schemas.workout import ExerciseResponse
import re
import json

def clean_json_content(content: str) -> str:
    """Remove markdown code block formatting from JSON content"""
    # Remove ```json at the beginning and ``` at the end
    content = content.strip()
    if content.startswith('```json'):
        content = content[7:]  # Remove ```json
    elif content.startswith('```'):
        content = content[3:]   # Remove ```
    
    if content.endswith('```'):
        content = content[:-3]  # Remove trailing ```
    
    return content.strip()

def classify_intent(llm, user_message: str) -> str:
    """Classify user intent as either 'exercise' or 'nutrition'"""
    messages = [
    (
        "system",
        "You are an intent classification model. Your task is to classify user messages into 'exercise' or 'nutrition' or 'other' categories. Only respond with one of these three words. Do not add any explanations or additional text.",
    ),
    ("human", f"{user_message}")
]
    return llm.invoke(messages).content.strip().lower()


async def handle_exercise_request(llm, tools, user_message: str, user_id: str = None):
    """Handle exercise-related requests"""
    
    # Filter tools for exercise-related ones
    
    # Create structured output LLM
    structured_llm = llm.with_structured_output(ExerciseResponse)
    
    # Exercise-specific prompt
    exercise_prompt = f"""You are a fitness expert assistant. Your task is to:
1. Use available tools to gather exercise information
2. Generate a comprehensive workout plan
3. Return both explanatory text and structured data
4. NEVER MAKE UP EXERCISE NAMES OR DETAILS, USE TOOLS TO FIND REAL EXERCISES AND THEIR IDS
5. To start first make sure to list all available facts about exercises using the list_facts tool. Then plan the target muscles and exercises accordingly. Then use the get_exercise_by_target tool to find the exercise details and add the use the best one in the plan.
6. Make sure the plan is complete and each muscle group is covered with appropriate exercises. 
7. If the user has a specific user_id, tailor the plan to their profile and preferences.
8. If the request is about analyzing previous workouts, use the user_id to get their recent workouts and provide insights based on that. And in that case return the data as null
Here is the user_id you can use to get the user profile and preferences: {user_id if user_id else "No user_id provided"}

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
2. data: Complete workout plan in WorkoutPlan format, if null it means the request was about analyzing previous workouts and providing insights based on that. 

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

async def handle_nutrition_request(llm, tools, user_message: str, user_id: str = None):
    """Handle nutrition-related requests"""
    
    # Filter tools for nutrition-related ones
    
    # Create structured output LLM
    structured_llm = llm
    
    # Nutrition-specific prompt
    nutrition_prompt = f"""You are a nutrition expert assistant. Your task is to:
1. Use available tools to get the users nutrition information if needed. If no tools related to nutrition are available, proceed to step and make it. The tools only related to exercise should not be used.
2. Generate a comprehensive meal plan or answer nutrition questions
3. Return both explanatory text and structured data when applicable
4. If the user has a specific user_id, tailor the meal plan to their profile and preferences.
5. Always make sure that the meal plan is realistic and follows nutritional guidelines. Make sure to include the daily macros breakdown (protein, carbs, fat in grams) and total daily calories. Use realistic meal names and nutritional parameters.
6. Make sure no filed in the meal plan schema is missing. If you don't have the information, make reasonable assumptions based on standard nutritional guidelines.
7. Make sure to calculate the calories as whole numbers (integers) for each meal and ingredient. And make sure the total calories for each day is the sum of all meals and snacks calories. And the calories for each meal is the sum of all ingredients calories.
user_id you can use to get the user profile and preferences: {user_id if user_id else "No user_id provided"}

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

IMPORTANT: Respond ONLY with valid JSON format. Do NOT include any markdown formatting, code blocks, or additional explanation. Do NOT wrap the response in ```json``` blocks.

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
    ],
    "total_days": <number_of_days>
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

Remember: Return ONLY the JSON object, no markdown formatting or explanation.
"""
    
    structured_result = await structured_llm.ainvoke([HumanMessage(content=structure_prompt)])
    results = structured_result
    print("Raw results:", results.content)
    
    # Clean the JSON content to remove markdown formatting
    cleaned_content = clean_json_content(results.content)
    print("Cleaned content:", cleaned_content)
    
    try:
        results = json.loads(cleaned_content)
        return results
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Content causing error: {cleaned_content}")
        # Fallback: return a basic structure
        return {
            "text": "Sorry, there was an error processing the nutrition response. Please try again.",
            "data": None
        }