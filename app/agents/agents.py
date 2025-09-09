from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from app.schemas.workout import ExerciseResponse
from app.schemas.agent import AgentResponse
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
        "You are an intent classification model. Your task is to classify user messages into 'exercise' or 'nutrition' or 'other' categories, make the classification based on the general theme of the question and not on specific keywords, only use 'other' when the  question is unrelated to fitness or nutrition at all. Only respond with one of these three words. Do not add any explanations or additional text.",
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
9. Always make sure to get the user profile and preferences if user_id is provided and use it to tailor the workout plan and analysis.
10. For any questions related to fitness, exercise, or workout plans, ALWAYS respond with with valid answers.

Here is the user_id you can use to get the user profile and preferences: {user_id if user_id else "No user_id provided"}

Response format:
- text: Include your reasoning, explanations, and any additional context
- data: The complete workout plan following the WorkoutPlan schema

Always use tools to find real exercises before creating the plan (if asked to create one)."""

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
1. text: Summary and explanation of the workout plan, don't include the workout ID (if any). And make sure to return the same text with no changes
2. data: Complete workout plan in WorkoutPlan format, if null it means the request was about analyzing previous workouts OR providing insights. 

Agent response:
{final_message}

Create a comprehensive workout plan (ONLY IF REQUESTED AND DATA IS NOT NULL (CONTAINS A WORKOUT PLAN)) with:
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
8. For any questions related to nutrition, diet, or meal plans, ALWAYS respond with valid answers.
9. Always use tools to get real nutrition information if needed before creating the meal plan (if asked to create one).
10. If the request is a general nutrition question and not about generating a meal plan, set data to null and provide the answer in text.
11. For any recommendations ir advices, make sure they are suitable for users in UAE, considering local dietary habits and available food options.
12. Focus on sustainability aspects in nutrition, such as recommending plant-based options, reducing food waste, and considering environmental impacts of food choices.

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
1. text: The text of advice or meal plan. Don't make it as a summary, include all the details and explanations the AI will return to the user
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
    
async def handle_general_request(llm, tools, user_message: str, user_id: str = None):
    """Handle exercise-related requests"""
    
    # Filter tools for exercise-related ones
    
    # Create structured output LLM
    structured_llm = llm.with_structured_output(AgentResponse)
    
    # Exercise-specific prompt
    prompt = f"""
    you are a helpful assistant, who specialized in sustainability, fitness and nutrition, your task is to answer any general questions the user might have, you can use the available tools if needed, but if the tools are not related to the question, you can ignore them and just answer the question based on your knowledge. If the question is related to exercise or fitness, make sure to provide accurate and helpful information. Also, the users will be mostly in UAE, make sure if you're giving a recommendation or advice, it is suitable for that region. Always focus on the sustainability aspects and make sure the responses are accurate.
    Also you have access to the user_id if provided: {user_id if user_id else "No user_id provided"}
    you can use the user_id to get the user profile and preferences if needed to tailor your response.
    Also note that the units used in the user profile are in metric system (kg, cm, etc). Make sure you answer accordingly. And explain your answers if needed, specially for calculating things.
    Return in this format:
    text: all the text and information that the AI will return to the user
    data: Make it null always as this is a general question

    """

    # Create exercise agent
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=prompt
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
1. text: The text the AI will return to the user
2. data: Make it null always as this is a general question 

Agent response:
{final_message}

"""
    
    structured_result = await structured_llm.ainvoke([HumanMessage(content=structure_prompt)])
    
    # Ensure data is properly handled
    data_value = structured_result.data
    if data_value == 'null' or data_value == 'None' or data_value is None:
        data_value = None
    elif not isinstance(data_value, dict):
        data_value = None
    
    return AgentResponse(text=structured_result.text, data=data_value)
