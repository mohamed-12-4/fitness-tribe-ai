import os
import google.generativeai as gemini
from google import genai
import logging
from PIL import Image
from io import BytesIO
from google.genai import types
from dotenv import load_dotenv
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
    def analyze_meal(image_data):
        prompt = (
            "Analyze the following meal image and provide the name of the food, "
            "total calorie count, and calories per ingredient. "
            "Respond in the following JSON format: "
            '{ "food_name": "<food name>", "total_calories": <total calorie count>, '
            '"calories_per_ingredient": {"<ingredient1>": <calories>, "<ingredient2>": <calories>, ...} }'
        )

        try:
            # Convert image data (which could be bytes) into an Image object
            image = Image.open(BytesIO(image_data))

            # Call the Gemini model with both the prompt and the image
            response = model.generate_content([prompt, image])

            # Log the response for debugging purposes
            logging.info(f"Gemini API Full Response (Analyze Meal): {response}")

            # Directly return the output text
            output_text = response.text
            logging.info(f"Output Text (Analyze Meal): {output_text}")

            return output_text

        except Exception as e:
            logging.error(f"Error communicating with Gemini API: {str(e)}")
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
        grounding_tool = types.Tool(google_search=types.GoogleSearch())

        prompt = (
            f"Provide a personalized nutrition plan for a {profile_data['age']} year old, "
            f"{profile_data['sex']}, weighing {profile_data['weight']}kg, height {profile_data['height']}cm, "
            f"with the goal of {profile_data['goal']}. The nutrition plan should include:\n\n"
            "- A daily calorie intake range.\n"
            "- Focus in making the plan use sustainable Ingredients and products that are environmentally friendly. Make sure to mention local brands in the UAE and you can use tools to search for them\n"
            "- Macronutrient distribution in daily ranges in grams for protein, carbohydrates, and fat.\n"
            "- A meal plan with an appropriate number of meals. Breakfast, lunch, dinner, and snacks each should have 3 options.\n"
            "- Each meal option should include:\n"
            "  - A description.\n"
            "  - Ingredients with quantities (grams, cups, tablespoons).\n"
            "  - Calorie counts per ingredient and per meal.\n"
            "  - A detailed recipe including step-by-step instructions and total cooking time.\n"
            "- Ensure the response follows strict JSON format rules with no trailing commas, and all strings are properly quoted.\n\n"
            "Respond in valid JSON format with no additional explanation or text.\n\n"
            "{\n"
            "  \"daily_calories_range\": {\"min\": <min calories>, \"max\": <max calories>},\n"
            "  \"macronutrients_range\": {\n"
            "    \"protein\": {\"min\": <min grams>, \"max\": <max grams>},\n"
            "    \"carbohydrates\": {\"min\": <min grams>, \"max\": <max grams>},\n"
            "    \"fat\": {\"min\": <min grams>, \"max\": <max grams>}\n"
            "  },\n"
            "  \"meal_plan\": {\n"
            "    \"breakfast\": [\n"
            "      {\"description\": \"<meal description>\", \"ingredients\": [\n"
            "        {\"ingredient\": \"<ingredient>\", \"quantity\": \"<quantity>\", \"calories\": <calories>}\n"
            "      ], \"total_calories\": <calories>, \"recipe\": \"<short recipe>\"}, \"suggested_brands\": [\"<List of local UAE brand names, e.g., Al Ain Farms, Bayara>\"]\n"
            "    ],\n"
            "    \"lunch\": [ ... ],\n"
            "    \"dinner\": [ ... ],\n"
            "    \"snacks\": [ ... ]\n"
            "  }\n"
            "}"
        )

        try:
            grounding_tool = types.Tool(
            google_search=types.GoogleSearch())

            # Configure generation settings
            config = types.GenerateContentConfig(
                tools=[grounding_tool]
            )

            response = client.models.generate_content(model=model_name, contents=prompt, config=config)

            # Log the response for debugging purposes
            logging.info(f"Full Gemini API Response: {response}")
            output_text = response.text

            return output_text

        except Exception as e:
            logging.error(
                f"Error communicating with Gemini API or while parsing the response: {str(e)}"
            )
            return None
