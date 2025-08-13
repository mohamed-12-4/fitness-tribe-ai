import os
import google.generativeai as gemini
from google import genai
import logging
from PIL import Image
from io import BytesIO
from google.genai import types
from dotenv import load_dotenv
import requests
import json
from typing import Dict, Optional
# Initialize the Gemini API key and the model
load_dotenv()  # Try current directory first
if not os.getenv("GEMINI_API_KEY"):
    # Try relative path if current directory doesn't work
    load_dotenv('../.env')
if not os.getenv("GEMINI_API_KEY"):
    # Try absolute path as last resort
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    load_dotenv(env_path)

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
gemini.configure(api_key=GEMINI_KEY)
model_name = "gemini-2.5-flash"
model = gemini.GenerativeModel(model_name)
client = genai.Client(api_key=GEMINI_KEY)


class GeminiModel:
    @staticmethod
    def search_food_info(food_name: str) -> Optional[Dict]:
        """Search for food information using Open Food Facts API"""
        try:
            search_url = "https://world.openfoodfacts.org/cgi/search.pl"
            params = {
                'search_terms': food_name,
                'search_simple': 1,
                'action': 'process',
                'json': 1,
                'page_size': 5
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('products'):
                for product in data['products']:
                    if product.get('nutriments'):
                        return {
                            'product_name': product.get('product_name', ''),
                            'calories_100g': product['nutriments'].get('energy-kcal_100g', 0),
                            'protein_100g': product['nutriments'].get('proteins_100g', 0),
                            'carbs_100g': product['nutriments'].get('carbohydrates_100g', 0),
                            'fat_100g': product['nutriments'].get('fat_100g', 0),
                            'fiber_100g': product['nutriments'].get('fiber_100g', 0),
                            'ingredients': product.get('ingredients_text', ''),
                            'nutrition_grade': product.get('nutrition_grades', ''),
                            'brands': product.get('brands', ''),
                        }
            return None
            
        except Exception as e:
            logging.error(f"Error searching Open Food Facts: {str(e)}")
            return None

    @staticmethod
    def analyze_meal(image_data):
        prompt = (
            "Analyze the following meal image and identify the main dish/meal. "
            "Provide detailed nutritional analysis including:\n"
            "1. The overall name/description of the meal\n"
            "2. Total calories for the entire meal\n"
            "3. Calories breakdown per visible ingredient\n"
            "4. Total protein in grams\n"
            "5. Total carbohydrates in grams\n"
            "6. Total fats in grams\n\n"
            "All nutritional values should be whole numbers (no decimals).\n\n"
            "Respond in the following JSON format: "
            '{\n'
            '  "food_name": "<descriptive name of the meal>",\n'
            '  "total_calories": <total_calories_as_whole_number>,\n'
            '  "calories_per_ingredient": {\n'
            '    "<ingredient1>": <calories_as_whole_number>,\n'
            '    "<ingredient2>": <calories_as_whole_number>\n'
            '  },\n'
            '  "total_protein": <protein_grams_as_whole_number>,\n'
            '  "total_carbohydrates": <carbs_grams_as_whole_number>,\n'
            '  "total_fats": <fats_grams_as_whole_number>\n'
            '}'
        )

        try:
            # Convert image data (which could be bytes) into an Image object
            image = Image.open(BytesIO(image_data))

            # Call the Gemini model with both the prompt and the image
            response = model.generate_content([prompt, image])

            # Log the response for debugging purposes
            logging.info(f"Gemini API Full Response (Analyze Meal): {response}")

            gemini_result = response.text
            logging.info(f"Output Text (Analyze Meal): {gemini_result}")

            # Try to parse and enhance with Open Food Facts data
            try:
                parsed_result = json.loads(gemini_result)
                
                # Enhance with Open Food Facts data for additional verification
                food_name = parsed_result.get('food_name', '')
                nutrition_data = GeminiModel.search_food_info(food_name)
                
                if nutrition_data:
                    # Add additional nutrition info as metadata
                    parsed_result['nutrition_verification'] = {
                        'source': 'Open Food Facts',
                        'verified_data': nutrition_data
                    }
                
                return json.dumps(parsed_result)
                
            except json.JSONDecodeError:
                # If parsing fails, return original Gemini response
                logging.warning("Failed to parse Gemini response as JSON, returning raw text")
                return gemini_result

        except Exception as e:
            logging.error(f"Error analyzing meal: {str(e)}")
            return None

    @staticmethod
    def generate_workout_plan(profile_data):
        # Build equipment part separately to avoid quote conflicts
        equipment_part = ""
        if profile_data.get('equipment'):
            equipment_part = f"The user has the following available equipment: {', '.join(profile_data['equipment'])}. "

        prompt = (
            f"Create a workout plan for a {profile_data['age']} year old {profile_data['sex']}, "
            f"weighing {profile_data['weight']}kg and {profile_data['height']}cm tall, with the goal of {profile_data['goal']}. "
            f"The workout plan should include {profile_data['workouts_per_week']} sessions per week. "
            f"{equipment_part}"
            "The workout plan should focus exclusively on safe, appropriate, and positive exercise recommendations. "
            "Avoid any mention of sensitive or controversial topics. Do not include any content related to sexuality, hate speech, violence, or other harmful themes. "
            "Respond in valid JSON format with no additional explanation or text. "
            "The plan should include:\n"
            "- A warm-up section with a description and duration.\n"
            "- Cardio recommendations with a description and duration.\n"
            "- Number of sessions per week.\n"
            "- Detailed exercises for each session with sets, reps, and rest times.\n"
            "- A cooldown section with a description and duration.\n\n"
            "Respond in strict JSON format, ensuring all data is appropriately formatted and focused solely on the workout plan. Ensure that all reps values in the workout_sessions are in double quotes. Here is the format:\n"
            "{\n"
            "  \"warmup\": {\"description\": \"<description>\", \"duration\": <duration in minutes>},\n"
            "  \"cardio\": {\"description\": \"<description>\", \"duration\": <duration in minutes>},\n"
            "  \"sessions_per_week\": <sessions>,\n"
            "  \"workout_sessions\": [\n"
            "    {\n"
            "      \"exercises\": [\n"
            "        {\"name\": \"<exercise name>\", \"sets\": <sets>, \"reps\": \"<reps>\", \"rest\": <rest time in seconds>}\n"
            "      ]\n"
            "    }\n"
            "  ],\n"
            "  \"cooldown\": {\"description\": \"<description>\", \"duration\": <duration in minutes>}\n"
            "}\n"
        )
        logging.info(f"Generated prompt: {prompt}")
        try:

            response = model.generate_content(contents=prompt)

            # Log the response for debugging purposes
            logging.info(f"Full Gemini API Response: {response}")

            output_text = response.text
            # Check if the response is empty or None
            if not output_text or output_text.strip() == "":
                logging.error("Empty response from Gemini API")
                return None

            logging.info(f"Gemini output text: {output_text}")
            return output_text

        except Exception as e:
            logging.error(
                f"Error communicating with Gemini API or while parsing the response: {str(e)}"
            )
            return None

    @staticmethod
    def generate_nutrition_plan(profile_data):
        # Extract dietary preferences and intolerances for the prompt
        dietary_prefs = ""
        if profile_data.get('dietary_preferences'):
            dietary_prefs = f"Dietary preferences: {', '.join(profile_data['dietary_preferences'])}. "
        
        food_intolerance = ""
        if profile_data.get('food_intolerance'):
            food_intolerance = f"Food intolerances/allergies to avoid: {', '.join(profile_data['food_intolerance'])}. "

        duration_days = profile_data.get('duration_days', 7)  # Default to 7 days

        prompt = (
            f"Create a personalized {duration_days}-day nutrition plan for a {profile_data['age']} year old "
            f"{profile_data['sex']}, weighing {profile_data['weight']}kg, height {profile_data['height']}cm, "
            f"with the goal of {profile_data['goal']}. "
            f"{dietary_prefs}{food_intolerance}"
            f"Generate a unique meal plan for each of the {duration_days} days with varied meals to prevent monotony. "
            "Each day should have different meals while maintaining nutritional balance. "
            "Focus on sustainable ingredients and environmentally friendly products from UAE brands like "
            "Al Ain Farms, Bayara, Kibsons, Organic Foods & Cafe, Lulu, Carrefour, Spinneys, etc.\n\n"
            "For each day, provide:\n"
            "- One breakfast option\n"
            "- One lunch option\n"
            "- One dinner option\n"
            "- 1-2 snack options\n"
            "- Calculate total daily calories and macronutrients\n\n"
            "Each meal should include:\n"
            "- A description\n"
            "- Ingredients with quantities (grams, cups, tablespoons)\n"
            "- Calorie counts per ingredient and per meal (as whole numbers, no decimals)\n"
            "- A detailed recipe with cooking time\n"
            "- UAE brand suggestions where applicable\n\n"
            "Ensure variety across days - no meal should be repeated exactly.\n"
            "All calorie values should be whole numbers (integers), not decimals.\n\n"
            "Respond in valid JSON format with no additional explanation or text:\n\n"
            "{\n"
            "  \"daily_calories_range\": {\"min\": <min calories>, \"max\": <max calories>},\n"
            "  \"macronutrients_range\": {\n"
            "    \"protein\": {\"min\": <min grams>, \"max\": <max grams>},\n"
            "    \"carbohydrates\": {\"min\": <min grams>, \"max\": <max grams>},\n"
            "    \"fat\": {\"min\": <min grams>, \"max\": <max grams>}\n"
            "  },\n"
            "  \"daily_meal_plans\": [\n"
            "    {\n"
            "      \"day\": 1,\n"
            "      \"date\": \"2025-08-12\",\n"
            "      \"breakfast\": {\n"
            "        \"description\": \"<meal description>\",\n"
            "        \"ingredients\": [\n"
            "          {\"ingredient\": \"<ingredient>\", \"quantity\": \"<quantity>\", \"calories\": <whole_number_calories>}\n"
            "        ],\n"
            "        \"total_calories\": <whole_number_calories>,\n"
            "        \"recipe\": \"<detailed recipe with cooking time>\",\n"
            "        \"suggested_brands\": [\"<UAE brands>\"]\n"
            "      },\n"
            "      \"lunch\": {\"description\": \"...\", \"ingredients\": [...], \"total_calories\": <whole_number_calories>, \"recipe\": \"...\", \"suggested_brands\": [...]},\n"
            "      \"dinner\": {\"description\": \"...\", \"ingredients\": [...], \"total_calories\": <whole_number_calories>, \"recipe\": \"...\", \"suggested_brands\": [...]},\n"
            "      \"snacks\": [\n"
            "        {\"description\": \"...\", \"ingredients\": [...], \"total_calories\": <whole_number_calories>, \"recipe\": \"...\", \"suggested_brands\": [...]}\n"
            "      ],\n"
            "      \"total_daily_calories\": <whole_number_total>,\n"
            "      \"daily_macros\": {\"protein\": <grams>, \"carbohydrates\": <grams>, \"fat\": <grams>}\n"
            "    }\n"
            f"    // Repeat for all {duration_days} days with different meals each day\n"
            "  ],\n"
            f"  \"total_days\": {duration_days}\n"
            "}"
        )

        try:
            response = model.generate_content(prompt)
            logging.info(f"Full Gemini API Response: {response}")
            return response.text

        except Exception as e:
            logging.error(f"Error generating nutrition plan: {str(e)}")
            return None
