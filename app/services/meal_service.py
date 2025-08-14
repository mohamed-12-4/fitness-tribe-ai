# app/services/meal_service.py

from app.models.gemini_model import GeminiModel
from app.schemas.meal import Meal
from fastapi import HTTPException
import logging
import json


def analyze_meal(image_data: bytes) -> Meal:
    logging.info("Starting meal analysis")
    try:
        result_text = GeminiModel.analyze_meal(image_data)
        if not result_text:
            raise HTTPException(status_code=500, detail="No response from Gemini API")

        logging.info(f"Gemini API Response Text (Analyze Meal): {result_text}")

        # Clean the result_text to remove Markdown formatting
        clean_result_text = result_text.strip("```json\n").strip("```")
        logging.info(f"Cleaned Result Text (Analyze Meal): {clean_result_text}")

        # Parse the cleaned JSON response
        try:
            result = json.loads(clean_result_text)
        except json.JSONDecodeError as e:
            logging.error(f"JSON Decode Error: {str(e)}")
            logging.error(f"Raw response: {clean_result_text}")
            raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {str(e)}")

        # Extract all required fields
        food_name = result.get("food_name")
        total_calories = result.get("total_calories")
        calories_per_ingredient = result.get("calories_per_ingredient", {})
        sustainability = result.get("sustainability", {})
        total_protein = result.get("total_protein")
        total_carbohydrates = result.get("total_carbohydrates")
        total_fats = result.get("total_fats")

        logging.info(f"Parsed - Food: {food_name}, Calories: {total_calories}, "
                    f"Protein: {total_protein}, Carbs: {total_carbohydrates}, Fats: {total_fats}")

        # Validate that all required fields are present
        if not all([food_name is not None, total_calories is not None, 
                   total_protein is not None, total_carbohydrates is not None, 
                   total_fats is not None, sustainability]):
            missing_fields = []
            if food_name is None: missing_fields.append("food_name")
            if total_calories is None: missing_fields.append("total_calories")
            if total_protein is None: missing_fields.append("total_protein")
            if total_carbohydrates is None: missing_fields.append("total_carbohydrates")
            if total_fats is None: missing_fields.append("total_fats")
            if not sustainability: missing_fields.append("sustainability")
            
            logging.error(f"Missing required fields: {missing_fields}")
            raise HTTPException(
                status_code=500,
                detail=f"Missing required fields in AI response: {', '.join(missing_fields)}"
            )

        # Create and return Meal object (field validators will handle type conversion)
        return Meal(
            food_name=food_name,
            total_calories=total_calories,
            calories_per_ingredient=calories_per_ingredient,
            sustainability=sustainability,
            total_protein=total_protein,
            total_carbohydrates=total_carbohydrates,
            total_fats=total_fats
        )

    except HTTPException:
        # Re-raise HTTP exceptions without wrapping
        raise
    except Exception as e:
        logging.error(f"Exception (Analyze Meal): {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
